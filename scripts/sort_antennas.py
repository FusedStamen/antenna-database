import os
import re
import shutil
import math

# --- CONFIGURATION ---
SOURCE_DIR = "./antennas_raw"       
OUTPUT_DIR = "./antennas_sorted"    

# SWR Thresholds
SWR_GOOD_MAX = 2.0
SWR_MARGINAL_MAX = 3.0

# Wi-Fi Frequency Windows (in Hz)
FREQ_24_MIN = 2.412e9
FREQ_24_MAX = 2.484e9
FREQ_5_MIN  = 5.180e9
FREQ_5_MAX  = 5.825e9


def calculate_swr_from_ri(real, imag):
    """Calculates SWR directly from Real and Imaginary S11 components."""
    # Gamma (Reflection Coefficient magnitude) = sqrt(real^2 + imag^2)
    gamma = math.sqrt(real**2 + imag**2)
    
    if gamma >= 1.0:
        return float('inf') # 100% or more power reflection
        
    return (1 + gamma) / (1 - gamma)


def get_max_swr_for_band(file_path, freq_min, freq_max):
    """Parses RI Touchstone files and finds worst-case SWR inside frequency window."""
    if not os.path.exists(file_path):
        return float('inf')

    max_swr = 0.0
    found_data = False

    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            # Skip comments and header metadata lines
            if not line or line.startswith('!') or line.startswith(';') or line.startswith('#'):
                continue
                
            parts = re.split(r'\s+', line)
            if len(parts) >= 3:
                try:
                    freq = float(parts[0])
                    s_real = float(parts[1])
                    s_imag = float(parts[2])
                    
                    # Ignore the corrupted 0 Hz entries at the tail of sweeps
                    if freq <= 0:
                        continue
                        
                    # Filter for target Wi-Fi frequency spaces
                    if freq_min <= freq <= freq_max:
                        found_data = True
                        swr = calculate_swr_from_ri(s_real, s_imag)
                        if swr > max_swr:
                            max_swr = swr
                except ValueError:
                    continue

    return max_swr if found_data else float('inf')


def main():
    categories = ['Good', 'Marginal', 'Do_Not_Use']
    for cat in categories:
        os.makedirs(os.path.join(OUTPUT_DIR, cat), exist_ok=True)

    if not os.path.exists(SOURCE_DIR):
        print(f"Source directory '{SOURCE_DIR}' not found.")
        return

    all_files = [f for f in os.listdir(SOURCE_DIR) if f.lower().endswith('.s1p')]
    
    # Group paired frequency sweeps by their root antenna key tag
    antenna_pairs = {}
    for filename in all_files:
        match = re.match(r"(.+)-(2\.4ghz|5ghz)\.s1p", filename, re.IGNORECASE)
        if match:
            base_name = match.group(1).strip()
            band = match.group(2).lower()
            if base_name not in antenna_pairs:
                antenna_pairs[base_name] = {'2.4ghz': None, '5ghz': None}
            antenna_pairs[base_name][band] = filename

    print(f"Found {len(antenna_pairs)} unique physical antennas to analyze.\n")
    stats = {'Good': 0, 'Marginal': 0, 'Do_Not_Use': 0}

    for antenna_id, bands in antenna_pairs.items():
        file_24 = bands['2.4ghz']
        file_5 = bands['5ghz']
        
        # Check if 5G file exists to classify architectural intent
        is_dual_band = True if (file_24 and file_5) else False
        
        # Evaluate 2.4 GHz Sweep File
        if file_24:
            max_24 = get_max_swr_for_band(os.path.join(SOURCE_DIR, file_24), FREQ_24_MIN, FREQ_24_MAX)
        else:
            max_24 = float('inf') 
            
        # Evaluate 5 GHz Sweep File
        if file_5:
            max_5 = get_max_swr_for_band(os.path.join(SOURCE_DIR, file_5), FREQ_5_MIN, FREQ_5_MAX)
        else:
            max_5 = None if not is_dual_band else float('inf')

        # Determine structural tier ranking limit
        if is_dual_band:
            worst_overall_swr = max(max_24, max_5)
        else:
            worst_overall_swr = max_24

        if worst_overall_swr <= SWR_GOOD_MAX:
            category = 'Good'
        elif worst_overall_swr <= SWR_MARGINAL_MAX:
            category = 'Marginal'
        else:
            category = 'Do_Not_Use'

        stats[category] += 1

        # File Migration Execution
        for band_file in [file_24, file_5]:
            if band_file:
                src = os.path.join(SOURCE_DIR, band_file)
                dst = os.path.join(OUTPUT_DIR, category, band_file)
                shutil.copy2(src, dst)

        # Build clean console print statements
        str_24 = f"{max_24:.2f}" if max_24 != float('inf') else "FAIL/OUT-OF-BAND"
        if max_5 is None:
            str_5 = "N/A (Single-Band)"
        elif max_5 == float('inf'):
            str_5 = "FAIL/OUT-OF-BAND"
        else:
            str_5 = f"{max_5:.2f}"
            
        type_string = "Dual-Band" if is_dual_band else "2.4G Only"
        print(f"[{type_string:<9}] {antenna_id:<22} -> [{category:<10}] (Max SWR | 2.4G: {str_24} | 5G: {str_5})")

    print("\n" + "="*50)
    print(" RI-ADAPTIVE SORTING COMPLETE")
    print("="*50)
    for cat, count in stats.items():
        print(f"  {cat:<12}: {count} physical units binned successfully")
    print("="*50)


if __name__ == "__main__":
    main()