#!/usr/bin/env python3
"""
analyze_antenna.py
------------------
Analyzes LiteVNA S1P exports and outputs standardized antenna metrics
for the antenna-database project.

Usage:
    python analyze_antenna.py <file.s1p> [options]

Examples:
    python analyze_antenna.py HF-01_2400MHz.s1p
    python analyze_antenna.py HF-01_2400MHz.s1p --band 2.4
    python analyze_antenna.py BFD-01_5GHz.s1p --band 5
    python analyze_antenna.py LR-01_915MHz.s1p --band lora
    python analyze_antenna.py GPS-01_L1.s1p --band gps
    python analyze_antenna.py HF-01_2400MHz.s1p --plot
    python analyze_antenna.py HF-01_2400MHz.s1p --csv output.csv

Requirements:
    pip install scikit-rf numpy pandas matplotlib

License: MIT
"""

import sys
import argparse
import numpy as np
import pandas as pd
import skrf as rf
from pathlib import Path


# ── Band definitions ──────────────────────────────────────────────────────────
BANDS = {
    '2.4': {
        'name': '2.4 GHz WiFi',
        'center_mhz': 2450,
        'low_mhz': 2400,
        'high_mhz': 2484,
        'target_mhz': 2450,
        'search_low_mhz': 2200,
        'search_high_mhz': 2700,
    },
    '5': {
        'name': '5 GHz WiFi',
        'center_mhz': 5500,
        'low_mhz': 5150,
        'high_mhz': 5850,
        'target_mhz': 5500,
        'search_low_mhz': 4700,
        'search_high_mhz': 6100,
    },
    '6': {
        'name': '6 GHz WiFi 6E',
        'center_mhz': 6025,
        'low_mhz': 5925,
        'high_mhz': 7125,
        'target_mhz': 6025,
        'search_low_mhz': 5800,
        'search_high_mhz': 7200,
    },
    'lora': {
        'name': 'LoRa 915 MHz',
        'center_mhz': 915,
        'low_mhz': 902,
        'high_mhz': 928,
        'target_mhz': 915,
        'search_low_mhz': 800,
        'search_high_mhz': 1050,
    },
    'lte_low': {
        'name': 'LTE Low Band',
        'center_mhz': 775,
        'low_mhz': 700,
        'high_mhz': 850,
        'target_mhz': 775,
        'search_low_mhz': 600,
        'search_high_mhz': 1000,
    },
    'adsb': {
        'name': 'ADS-B 1090 MHz',
        'center_mhz': 1090,
        'low_mhz': 1080,
        'high_mhz': 1100,
        'target_mhz': 1090,
        'search_low_mhz': 900,
        'search_high_mhz': 1300,
    },
    'uat': {
        'name': 'UAT 978 MHz',
        'center_mhz': 978,
        'low_mhz': 968,
        'high_mhz': 988,
        'target_mhz': 978,
        'search_low_mhz': 850,
        'search_high_mhz': 1100,
    },
    'gps': {
        'name': 'GPS L1',
        'center_mhz': 1575,
        'low_mhz': 1559,
        'high_mhz': 1591,
        'target_mhz': 1575.42,
        'search_low_mhz': 1300,
        'search_high_mhz': 1800,
    },
    'ais': {
        'name': 'AIS 162 MHz',
        'center_mhz': 162,
        'low_mhz': 161.975,
        'high_mhz': 162.025,
        'target_mhz': 162,
        'search_low_mhz': 140,
        'search_high_mhz': 185,
    },
    'bt': {
        'name': 'Bluetooth / BLE',
        'center_mhz': 2441,
        'low_mhz': 2402,
        'high_mhz': 2480,
        'target_mhz': 2441,
        'search_low_mhz': 2300,
        'search_high_mhz': 2600,
    },
}


# ── SWR verdict ───────────────────────────────────────────────────────────────
def swr_verdict(swr):
    """
    Verdict thresholds per WiFi Antenna Testing Methodology v4.
    SWR < 2.0 = Good — reflected power under 11%, not meaningful for wardriving.
    SWR 2.0–3.0 = Marginal — usable but note which band is weak.
    SWR > 3.0 = Do_Not_Use — excessive mismatch loss.
    """
    if swr < 2.0:
        return 'Good'
    elif swr < 3.0:
        return 'Marginal'
    else:
        return 'Do_Not_Use'


def power_reflected(swr):
    gamma = (swr - 1) / (swr + 1)
    return round(gamma**2 * 100, 2)


def loss_db(swr):
    gamma = (swr - 1) / (swr + 1)
    return round(-10 * np.log10(1 - gamma**2), 3)


# ── Core analysis ─────────────────────────────────────────────────────────────
def analyze(s1p_path, band_key=None, plot=False, csv_out=None, verbose=True):
    path = Path(s1p_path)
    if not path.exists():
        print(f"ERROR: File not found: {s1p_path}")
        sys.exit(1)

    # Load S1P
    ntwk = rf.Network(str(path))
    freq_mhz = ntwk.f / 1e6
    swr = ntwk.s_vswr[:, 0, 0]

    # Filter out corrupted zero-frequency entries at tail of some LiteVNA exports
    valid = freq_mhz > 0
    freq_mhz = freq_mhz[valid]
    swr = swr[valid]

    if len(freq_mhz) == 0:
        raise ValueError("No valid frequency data after filtering zero-frequency entries")

    # Auto-detect band if not specified
    if band_key is None:
        center = np.mean(freq_mhz)
        if center < 300:
            band_key = 'ais'
        elif center < 1000:
            band_key = 'lora'
        elif center < 1200:
            band_key = 'adsb'
        elif center < 1700:
            band_key = 'gps'
        elif center < 3000:
            band_key = '2.4'
        elif center < 6000:
            band_key = '5'
        else:
            band_key = '6'
        if verbose:
            print(f"Auto-detected band: {band_key} ({BANDS[band_key]['name']})")

    band = BANDS[band_key]

    # Find resonance (global minimum SWR across full sweep)
    min_idx = np.argmin(swr)
    resonant_freq_mhz = freq_mhz[min_idx]
    swr_at_resonance = swr[min_idx]
    offset_mhz = round(resonant_freq_mhz - band['target_mhz'], 2)

    # SWR at band edges and center
    def swr_at(target_mhz):
        idx = np.argmin(np.abs(freq_mhz - target_mhz))
        if abs(freq_mhz[idx] - target_mhz) > 10:
            return None  # Target outside sweep range
        return round(float(swr[idx]), 4)

    swr_low = swr_at(band['low_mhz'])
    swr_center = swr_at(band['center_mhz'])
    swr_high = swr_at(band['high_mhz'])
    swr_target = swr_at(band['target_mhz'])

    # Worst in-band SWR — this is the verdict metric, consistent with sort_antennas.py
    # Uses max SWR within the defined band window, not SWR at resonance
    band_mask = (freq_mhz >= band['low_mhz']) & (freq_mhz <= band['high_mhz'])
    if band_mask.any():
        swr_worst_inband = float(np.max(swr[band_mask]))
    else:
        swr_worst_inband = float(swr_at_resonance)  # fallback if band outside sweep

    # Verdict based on worst in-band SWR
    verdict = swr_verdict(swr_worst_inband)
    refl = power_reflected(swr_worst_inband)
    loss = loss_db(swr_worst_inband)

    # ── Output ────────────────────────────────────────────────────────────────
    results = {
        'file': path.name,
        'band': band['name'],
        'sweep_start_mhz': round(freq_mhz[0], 2),
        'sweep_stop_mhz': round(freq_mhz[-1], 2),
        'resonant_freq_mhz': round(resonant_freq_mhz, 3),
        'swr_at_resonance': round(swr_at_resonance, 4),
        'swr_worst_inband': round(swr_worst_inband, 4),
        'offset_from_target_mhz': offset_mhz,
        'target_freq_mhz': band['target_mhz'],
        f'swr_at_{int(band["low_mhz"])}mhz': swr_low,
        f'swr_at_{int(band["center_mhz"])}mhz': swr_center,
        f'swr_at_{int(band["high_mhz"])}mhz': swr_high,
        'power_reflected_pct': refl,
        'mismatch_loss_db': loss,
        'verdict': verdict,
    }

    if verbose:
        print()
        print(f"{'='*55}")
        print(f"  {path.name}")
        print(f"  Band: {band['name']}")
        print(f"{'='*55}")
        print(f"  Sweep range:        {freq_mhz[0]:.1f} – {freq_mhz[-1]:.1f} MHz")
        print(f"  Resonant frequency: {resonant_freq_mhz:.3f} MHz")
        print(f"  SWR at resonance:   {swr_at_resonance:.4f}")
        print(f"  Offset from target: {offset_mhz:+.2f} MHz  (target: {band['target_mhz']} MHz)")
        print()
        print(f"  SWR at band edges:")
        if swr_low:
            print(f"    Low  ({int(band['low_mhz'])} MHz):   {swr_low}")
        if swr_center:
            print(f"    Center ({int(band['center_mhz'])} MHz): {swr_center}")
        if swr_high:
            print(f"    High ({int(band['high_mhz'])} MHz):  {swr_high}")
        print()
        print(f"  Worst in-band SWR:  {swr_worst_inband:.4f}  (verdict basis)")
        print(f"  Power reflected:    {refl}%  (at worst in-band)")
        print(f"  Mismatch loss:      {loss} dB  (at worst in-band)")
        print()
        print(f"  Verdict:            {verdict}")
        print(f"{'='*55}")

    # ── Optional plot ─────────────────────────────────────────────────────────
    if plot:
        try:
            import matplotlib.pyplot as plt
            fig, ax = plt.subplots(figsize=(12, 5))
            ax.plot(freq_mhz, swr, 'r-', linewidth=1.5, label='SWR')
            ax.axvline(band['low_mhz'], color='blue', linestyle='--', alpha=0.5, label='Band edges')
            ax.axvline(band['high_mhz'], color='blue', linestyle='--', alpha=0.5)
            ax.axvline(band['target_mhz'], color='green', linestyle=':', alpha=0.7, label=f'Target ({band["target_mhz"]} MHz)')
            ax.axvline(resonant_freq_mhz, color='red', linestyle=':', alpha=0.7, label=f'Resonance ({resonant_freq_mhz:.1f} MHz, SWR {swr_at_resonance:.3f})')
            ax.axhline(1.5, color='orange', linestyle='--', alpha=0.4, label='SWR 1.5')
            ax.axhline(2.0, color='red', linestyle='--', alpha=0.4, label='SWR 2.0')
            ax.set_xlabel('Frequency (MHz)')
            ax.set_ylabel('SWR')
            ax.set_title(f'{path.stem} — {band["name"]}')
            ax.legend(fontsize=8)
            ax.set_ylim(1, min(10, max(swr) * 1.1))
            ax.grid(True, alpha=0.3)
            plt.tight_layout()
            plot_path = path.with_suffix('.png')
            plt.savefig(plot_path, dpi=150)
            print(f"  Plot saved: {plot_path}")
            plt.show()
        except ImportError:
            print("  matplotlib not installed — skipping plot")

    # ── Optional CSV output ───────────────────────────────────────────────────
    if csv_out:
        df = pd.DataFrame([results])
        csv_path = Path(csv_out)
        if csv_path.exists():
            existing = pd.read_csv(csv_path)
            df = pd.concat([existing, df], ignore_index=True)
        df.to_csv(csv_path, index=False)
        if verbose:
            print(f"  Results appended to: {csv_out}")

    return results


# ── Batch mode ────────────────────────────────────────────────────────────────
def batch_analyze(directory, band_key=None, csv_out='antenna_results.csv'):
    """Analyze all .s1p files in a directory."""
    d = Path(directory)
    s1p_files = sorted(d.glob('**/*.s1p'))

    if not s1p_files:
        print(f"No .s1p files found in {directory}")
        return

    print(f"Found {len(s1p_files)} S1P files\n")
    all_results = []

    for f in s1p_files:
        try:
            results = analyze(str(f), band_key=band_key, plot=False,
                            csv_out=None, verbose=False)
            all_results.append(results)
            status = f"  ✓ {f.name:<45} {results['resonant_freq_mhz']:>10.1f} MHz  SWR {results['swr_at_resonance']:.4f}  {results['verdict']}"
            print(status)
        except Exception as e:
            print(f"  ✗ {f.name:<45} ERROR: {e}")

    if all_results:
        df = pd.DataFrame(all_results)
        df.to_csv(csv_out, index=False)
        print(f"\nBatch results saved to: {csv_out}")
        print(f"Total analyzed: {len(all_results)}")
        print(f"Good:        {sum(1 for r in all_results if r['verdict'] == 'Good')}")
        print(f"Marginal:    {sum(1 for r in all_results if r['verdict'] == 'Marginal')}")
        print(f"Do_Not_Use:  {sum(1 for r in all_results if r['verdict'] == 'Do_Not_Use')}")


# ── CLI ───────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description='Analyze LiteVNA S1P exports for antenna characterization',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Band options:
  2.4      2.4 GHz WiFi (2400-2484 MHz)
  5        5 GHz WiFi (5150-5850 MHz)
  6        6 GHz WiFi 6E (5925-7125 MHz)
  lora     LoRa 915 MHz ISM (902-928 MHz)
  lte_low  LTE Low Band (700-850 MHz)
  adsb     ADS-B 1090 MHz
  uat      UAT 978 MHz
  gps      GPS L1 1575.42 MHz
  ais      AIS 162 MHz
  bt       Bluetooth / BLE (2402-2480 MHz)

Examples:
  python analyze_antenna.py HF-01_2400MHz.s1p --band 2.4 --plot
  python analyze_antenna.py BFD-01_5GHz.s1p --band 5 --csv results.csv
  python analyze_antenna.py --batch ./vna_data/ --csv batch_results.csv
        """
    )

    parser.add_argument('file', nargs='?', help='S1P file to analyze')
    parser.add_argument('--band', choices=list(BANDS.keys()),
                        help='Target band (auto-detected if not specified)')
    parser.add_argument('--plot', action='store_true',
                        help='Generate and save SWR plot as PNG')
    parser.add_argument('--csv', metavar='OUTPUT.CSV',
                        help='Append results to CSV file')
    parser.add_argument('--batch', metavar='DIRECTORY',
                        help='Analyze all .s1p files in directory')
    parser.add_argument('--quiet', action='store_true',
                        help='Suppress verbose output')

    args = parser.parse_args()

    if args.batch:
        batch_analyze(args.batch, band_key=args.band,
                     csv_out=args.csv or 'antenna_results.csv')
    elif args.file:
        analyze(args.file, band_key=args.band, plot=args.plot,
               csv_out=args.csv, verbose=not args.quiet)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
