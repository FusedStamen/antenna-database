#!/usr/bin/env python3
"""
analyze_wardrive.py
-------------------
Analyzes Biscuit Ultra wardriving CSV logs and outputs standardized
antenna comparison metrics for the antenna-database project.

Usage:
    # Analyze a single run
    python analyze_wardrive.py run1.csv

    # Compare two antennas (3 runs each, alternating)
    python analyze_wardrive.py --compare TC-01_run1.csv TC-01_run2.csv TC-01_run3.csv \
                                         BFD-04_run1.csv BFD-04_run2.csv BFD-04_run3.csv \
                               --labels "TC-01" "BFD-04"

    # Batch analyze a directory
    python analyze_wardrive.py --batch ./wardriving_logs/

Requirements:
    pip install pandas numpy

License: MIT
"""

import sys
import argparse
import csv
from pathlib import Path
from collections import defaultdict
import numpy as np

try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False
    print("Warning: pandas not installed. Using basic CSV parsing.")


# ── Parse Biscuit Ultra WigleWifi CSV ─────────────────────────────────────────
def parse_biscuit_csv(filepath):
    """
    Parse a Biscuit Ultra WigleWifi 1.6 format CSV.
    Returns dict with 'wifi' and 'ble' lists of observations.
    """
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {filepath}")

    wifi = []
    ble = []
    header_skipped = 0

    with open(path, 'r', encoding='utf-8', errors='replace') as f:
        reader = csv.reader(f)
        for row in reader:
            # Skip WigleWifi header line and column header line
            if header_skipped < 2:
                header_skipped += 1
                continue
            if len(row) < 14:
                continue
            try:
                entry = {
                    'mac': row[0].strip().upper(),
                    'ssid': row[1].strip(),
                    'auth': row[2].strip(),
                    'timestamp': row[3].strip(),
                    'channel': int(row[4]) if row[4].strip() else 0,
                    'freq_mhz': int(row[5]) if row[5].strip() else 0,
                    'rssi': int(row[6]),
                    'lat': float(row[7]) if row[7].strip() else 0.0,
                    'lon': float(row[8]) if row[8].strip() else 0.0,
                    'type': row[13].strip(),
                }
                if entry['type'] == 'WIFI':
                    wifi.append(entry)
                elif entry['type'] == 'BLE':
                    ble.append(entry)
            except (ValueError, IndexError):
                continue

    return {'wifi': wifi, 'ble': ble, 'file': path.name}


# ── Compute metrics for a single run ─────────────────────────────────────────
def compute_metrics(parsed, data_type='wifi'):
    """
    Compute antenna comparison metrics from parsed CSV data.
    Uses median RSSI per BSSID to handle duplicate observations.
    """
    observations = parsed[data_type]

    if not observations:
        return {
            'file': parsed['file'],
            'type': data_type.upper(),
            'total_observations': 0,
            'unique_devices': 0,
            'devices_above_70': 0,
            'devices_70_to_80': 0,
            'devices_below_80': 0,
            'median_rssi_all': None,
            'min_median_rssi': None,
            'max_median_rssi': None,
            'pct_below_80': 0,
        }

    # Group RSSI observations by MAC
    by_mac = defaultdict(list)
    for obs in observations:
        by_mac[obs['mac']].append(obs['rssi'])

    # Compute median RSSI per device
    median_rssi = {mac: np.median(rssis) for mac, rssis in by_mac.items()}

    unique = len(median_rssi)
    rssi_values = list(median_rssi.values())

    above_70 = sum(1 for r in rssi_values if r > -70)
    between_70_80 = sum(1 for r in rssi_values if -80 <= r <= -70)
    below_80 = sum(1 for r in rssi_values if r < -80)

    return {
        'file': parsed['file'],
        'type': data_type.upper(),
        'total_observations': len(observations),
        'unique_devices': unique,
        'devices_above_70': above_70,
        'devices_70_to_80': between_70_80,
        'devices_below_80': below_80,
        'median_rssi_all': round(float(np.median(rssi_values)), 1),
        'min_median_rssi': round(float(min(rssi_values)), 1),
        'max_median_rssi': round(float(max(rssi_values)), 1),
        'pct_below_80': round(below_80 / unique * 100, 1) if unique > 0 else 0,
    }


# ── Print single run summary ──────────────────────────────────────────────────
def print_run_summary(metrics, label=None):
    t = metrics['type']
    name = label or metrics['file']
    print(f"\n{'='*55}")
    print(f"  {name} — {t}")
    print(f"{'='*55}")
    print(f"  Total observations:     {metrics['total_observations']}")
    print(f"  Unique devices:         {metrics['unique_devices']}")
    print()
    print(f"  RSSI > -70 dBm:         {metrics['devices_above_70']}")
    print(f"  RSSI -70 to -80 dBm:    {metrics['devices_70_to_80']}")
    print(f"  RSSI < -80 dBm:         {metrics['devices_below_80']}  ← primary metric")
    print(f"  % below -80 dBm:        {metrics['pct_below_80']}%")
    print()
    print(f"  Median RSSI (all):      {metrics['median_rssi_all']} dBm")
    print(f"  Min median RSSI:        {metrics['min_median_rssi']} dBm")
    print(f"  Max median RSSI:        {metrics['max_median_rssi']} dBm")
    print(f"{'='*55}")


# ── Compare two antenna sets ──────────────────────────────────────────────────
def compare_antennas(files_a, files_b, label_a='Antenna A', label_b='Antenna B',
                     data_type='wifi', csv_out=None):
    """
    Compare two antennas, each with multiple run files.
    Calculates mean metrics across runs and percentage difference.
    """
    def mean_metrics(files, label):
        all_metrics = []
        for f in files:
            parsed = parse_biscuit_csv(f)
            m = compute_metrics(parsed, data_type)
            all_metrics.append(m)
            print(f"  Loaded: {Path(f).name} — {m['unique_devices']} devices, "
                  f"{m['devices_below_80']} below -80 dBm")
        return all_metrics

    print(f"\nLoading {label_a} runs:")
    metrics_a = mean_metrics(files_a, label_a)
    print(f"\nLoading {label_b} runs:")
    metrics_b = mean_metrics(files_b, label_b)

    # Numeric fields to average
    numeric_fields = [
        'unique_devices', 'devices_above_70', 'devices_70_to_80',
        'devices_below_80', 'median_rssi_all', 'min_median_rssi', 'pct_below_80'
    ]

    def avg(metrics_list, field):
        vals = [m[field] for m in metrics_list if m[field] is not None]
        return round(np.mean(vals), 2) if vals else None

    avg_a = {f: avg(metrics_a, f) for f in numeric_fields}
    avg_b = {f: avg(metrics_b, f) for f in numeric_fields}

    def pct_diff(a, b):
        if a is None or b is None or b == 0:
            return None
        return round((a - b) / abs(b) * 100, 1)

    def abs_diff(a, b):
        if a is None or b is None:
            return None
        return round(a - b, 2)

    # ── Print comparison table ────────────────────────────────────────────────
    print(f"\n{'='*70}")
    print(f"  ANTENNA COMPARISON: {label_a} vs {label_b}")
    print(f"  Data type: {data_type.upper()} | Runs per antenna: {len(files_a)}/{len(files_b)}")
    print(f"{'='*70}")
    print(f"  {'Metric':<30} {label_a:>12} {label_b:>12} {'Diff':>10}")
    print(f"  {'-'*30} {'-'*12} {'-'*12} {'-'*10}")

    rows = [
        ('Unique devices', 'unique_devices', '{:.1f}', '{:+.1f} ({:+.1f}%)'),
        ('RSSI > -70 dBm', 'devices_above_70', '{:.1f}', '{:+.1f} ({:+.1f}%)'),
        ('RSSI -70 to -80 dBm', 'devices_70_to_80', '{:.1f}', '{:+.1f} ({:+.1f}%)'),
        ('RSSI < -80 dBm ★', 'devices_below_80', '{:.1f}', '{:+.1f} ({:+.1f}%)'),
        ('% below -80 dBm', 'pct_below_80', '{:.1f}%', '{:+.1f}pp'),
        ('Median RSSI (all)', 'median_rssi_all', '{:.1f} dBm', '{:+.1f} dBm'),
        ('Min median RSSI', 'min_median_rssi', '{:.1f} dBm', '{:+.1f} dBm'),
    ]

    results = {}
    for label, field, fmt, _ in rows:
        a_val = avg_a[field]
        b_val = avg_b[field]
        diff = abs_diff(a_val, b_val)
        pct = pct_diff(a_val, b_val)

        a_str = fmt.format(a_val) if a_val is not None else 'N/A'
        b_str = fmt.format(b_val) if b_val is not None else 'N/A'

        if diff is not None and pct is not None and field not in ('median_rssi_all', 'min_median_rssi', 'pct_below_80'):
            diff_str = f"{diff:+.1f} ({pct:+.1f}%)"
        elif diff is not None:
            diff_str = f"{diff:+.1f}"
        else:
            diff_str = 'N/A'

        marker = ' ←' if field == 'devices_below_80' else ''
        print(f"  {label:<30} {a_str:>12} {b_str:>12} {diff_str:>10}{marker}")
        results[field] = {'a': a_val, 'b': b_val, 'diff': diff, 'pct_diff': pct}

    print(f"{'='*70}")

    # Winner
    below80_a = avg_a['devices_below_80']
    below80_b = avg_b['devices_below_80']
    if below80_a is not None and below80_b is not None:
        if below80_a > below80_b:
            winner = label_a
            margin = pct_diff(below80_a, below80_b)
            print(f"\n  Winner: {winner} detects {margin:+.1f}% more marginal networks")
        elif below80_b > below80_a:
            winner = label_b
            margin = pct_diff(below80_b, below80_a)
            print(f"\n  Winner: {winner} detects {margin:+.1f}% more marginal networks")
        else:
            print(f"\n  Result: Tie on marginal network detection")

    # ── Optional CSV output ───────────────────────────────────────────────────
    if csv_out:
        output_rows = []
        for label, field, fmt, _ in rows:
            output_rows.append({
                'metric': label,
                f'mean_{label_a}': avg_a[field],
                f'mean_{label_b}': avg_b[field],
                'abs_diff': results[field]['diff'],
                'pct_diff': results[field]['pct_diff'],
            })
        df = pd.DataFrame(output_rows) if HAS_PANDAS else None
        if df is not None:
            df.to_csv(csv_out, index=False)
            print(f"\n  Comparison saved to: {csv_out}")

    return results


# ── Batch mode ────────────────────────────────────────────────────────────────
def batch_analyze(directory, data_type='wifi', csv_out='wardrive_results.csv'):
    d = Path(directory)
    csv_files = sorted(d.glob('**/*.csv'))
    csv_files = [f for f in csv_files if f.name != csv_out]

    if not csv_files:
        print(f"No CSV files found in {directory}")
        return

    print(f"Found {len(csv_files)} CSV files\n")
    all_results = []

    for f in csv_files:
        try:
            parsed = parse_biscuit_csv(str(f))
            m = compute_metrics(parsed, data_type)
            if m['total_observations'] == 0:
                continue
            all_results.append(m)
            print(f"  {f.name:<50} {m['unique_devices']:>4} devices  "
                  f"{m['devices_below_80']:>3} below -80")
        except Exception as e:
            print(f"  ERROR {f.name}: {e}")

    if all_results and HAS_PANDAS:
        df = pd.DataFrame(all_results)
        df.to_csv(csv_out, index=False)
        print(f"\nBatch results saved to: {csv_out}")


# ── CLI ───────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description='Analyze Biscuit Ultra wardriving CSV logs for antenna comparison',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Single run analysis
  python analyze_wardrive.py TC-01_run1.csv

  # Compare two antennas (3 runs each)
  python analyze_wardrive.py --compare \\
      TC-01_run1.csv TC-01_run2.csv TC-01_run3.csv \\
      BFD-04_run1.csv BFD-04_run2.csv BFD-04_run3.csv \\
      --labels "TC-01 (9dBi TECHTOO)" "BFD-04 (Bingfu 8dBi)"

  # Batch analyze directory
  python analyze_wardrive.py --batch ./wardriving_logs/
        """
    )

    parser.add_argument('file', nargs='?', help='Single CSV file to analyze')
    parser.add_argument('--compare', nargs='+', metavar='FILE',
                        help='Files for comparison (first half = antenna A, second half = antenna B)')
    parser.add_argument('--labels', nargs=2, metavar=('LABEL_A', 'LABEL_B'),
                        default=['Antenna A', 'Antenna B'],
                        help='Labels for the two antennas being compared')
    parser.add_argument('--type', choices=['wifi', 'ble'], default='wifi',
                        help='Data type to analyze (default: wifi)')
    parser.add_argument('--batch', metavar='DIRECTORY',
                        help='Analyze all CSV files in directory')
    parser.add_argument('--csv', metavar='OUTPUT.CSV',
                        help='Save results to CSV file')

    args = parser.parse_args()

    if args.batch:
        batch_analyze(args.batch, data_type=args.type,
                     csv_out=args.csv or 'wardrive_results.csv')

    elif args.compare:
        files = args.compare
        if len(files) % 2 != 0:
            print("ERROR: --compare requires an even number of files (split evenly between two antennas)")
            sys.exit(1)
        mid = len(files) // 2
        compare_antennas(
            files_a=files[:mid],
            files_b=files[mid:],
            label_a=args.labels[0],
            label_b=args.labels[1],
            data_type=args.type,
            csv_out=args.csv
        )

    elif args.file:
        parsed = parse_biscuit_csv(args.file)
        metrics = compute_metrics(parsed, args.type)
        print_run_summary(metrics)
        if args.csv and HAS_PANDAS:
            df = pd.DataFrame([metrics])
            df.to_csv(args.csv, index=False)
            print(f"\n  Results saved to: {args.csv}")

    else:
        parser.print_help()


if __name__ == '__main__':
    main()
