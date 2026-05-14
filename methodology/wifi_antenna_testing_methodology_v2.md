# WiFi Antenna Testing Methodology
### VNA Characterization + Fixed-Location Field Comparison
*Developed for wardriving and WiFi monitoring antenna selection*

---

## Overview

This methodology combines two complementary evaluation approaches:

1. **VNA Bench Testing** — objective electrical characterization of antenna impedance match using a LiteVNA 64
2. **Fixed-Location Field Testing** — real-world comparative performance measurement using a Biscuit Ultra wardriving device in a controlled indoor environment

Neither approach alone is sufficient. VNA testing tells you how well the antenna converts electrical energy to RF radiation. Field testing tells you how that translates to actual network detection in a real environment. Together they give a complete picture.

---

## Part 1: VNA Bench Testing

### Equipment
- LiteVNA 64
- NanoVNA-App (Windows)
- SMA calibration kit (Short, Open, Load)
- RP-SMA to SMA adapter (if required)
- 6" x 6" steel ground plane plate
- Ruler or calipers

### Calibration Profiles

Maintain separate calibration profiles for each frequency range. Do not use a single wide sweep — calibration accuracy degrades toward the edges of any profile. Recommended profiles:

| Profile Name | Start | Stop | Use |
|---|---|---|---|
| 2.4GHz WiFi BT | 2300 MHz | 2600 MHz | 2.4 GHz WiFi, Bluetooth, BLE |
| 5GHz WiFi | 4800 MHz | 6000 MHz | 5 GHz WiFi |
| UHF 433 700 900 | 400 MHz | 1000 MHz | LoRa, LTE low band, ADS-B |
| GPS + LTE mid-band | 1000 MHz | 1700 MHz | GPS L1, LTE mid-band |
| ADS-B LoRa Cell | 800 MHz | 1200 MHz | ADS-B 1090 MHz, LoRa 915 MHz, UAT 978 MHz |

Recalibrate if the VNA is moved, the temperature changes significantly, or adapters are swapped.

### Ground Plane Protocol

Antenna type determines whether the steel plate is used:

**Use the 6"x6" steel ground plane:**
- Monopole antennas (single element, relies on ground plane to complete the antenna circuit)
- Loaded stub antennas (rubber ducks, short stubbies)
- Any antenna that will be deployed on a metal-chassis device

**Do not use the steel ground plane:**
- Dipole or sleeve dipole antennas (balanced, self-contained)
- Patch antennas (have their own ground plane element)
- MIMO array units with integrated ground plane

**Ground plane mounting:**
Place the steel plate flat on a non-conductive surface (wood table, foam). Mount the antenna connector at the center of the plate. Ensure the antenna is vertical and perpendicular to the plate. Do not touch the antenna or plate during measurement — body capacitance will shift the resonance, particularly on high-Q designs. Use a short SMA extension cable if needed to avoid holding the connector.

### Measurement Procedure

1. Load the appropriate calibration profile
2. Connect the antenna (with or without ground plane per above)
3. Set the sweep range to the target profile
4. Allow 3–5 scan cycles to stabilize
5. Place the marker at the SWR minimum
6. Record: resonant frequency, SWR at resonance, SWR at band edges
7. For dual-band antennas, repeat with the 5 GHz profile
8. If the resonance is not visible within the sweep window, extend the sweep range to locate it

### Measurements to Record

For each antenna and band:

| Field | Description |
|---|---|
| Resonant frequency (MHz) | Frequency of SWR minimum |
| SWR at resonance | Lowest SWR value observed |
| Resonance offset (MHz) | Difference from band center target |
| SWR at band low edge | SWR at lowest target frequency |
| SWR at band center | SWR at center of target band |
| SWR at band high edge | SWR at highest target frequency |
| Verdict | PASS / MARGINAL / FAIL per criteria below |

### Verdict Criteria

Based on real-world power loss analysis:

| SWR | Reflected Power | Loss (dB) | Verdict |
|---|---|---|---|
| < 1.5 | < 4% | < 0.18 dB | PASS |
| 1.5 – 2.0 | 4–11% | 0.18–0.51 dB | PASS with note |
| 2.0 – 3.0 | 11–25% | 0.51–1.25 dB | MARGINAL |
| > 3.0 | > 25% | > 1.25 dB | FAIL |

**Note:** Resonance offset matters more than SWR in many cases. An antenna with SWR 1.8 but resonance centered on the target band is more useful than an antenna with SWR 1.2 but resonance 150 MHz off-center. Always evaluate both.

### Cable-Affected Measurements

For antennas with integral cables (mag-mounts, router arrays), full characterization is not possible without recalibrating at the cable end. For these antennas:

- Use the same sweep profile as direct-connect antennas
- Note that absolute SWR values are not meaningful due to standing wave ripple
- Compare **valley floor SWR** between units — the lowest dip visible on the ripple trace
- A lower valley floor indicates a better-matched antenna element regardless of cable
- Mark all results as "relative comparison only — cable-affected measurement"

---

## Part 2: Fixed-Location Field Testing

### Objective

Compare real-world network detection performance between antennas under controlled conditions. Measures the combined effect of antenna gain, radiation efficiency, pattern shape, and impedance match in an actual deployment environment.

### Equipment
- **Biscuit Ultra** wardriving device (firmware v1.4.1 or later)
- Antenna under test connected to **ESP32-C5 SMA port**
- **50-ohm terminator** (SMA Load from VNA calibration kit) on **ESP32-WROOM SMA port**
- Antennas under test
- Notebook or spreadsheet for logging

### Biscuit Ultra Hardware Configuration

The Biscuit Ultra contains two independent radios:
- **ESP32-WROOM-32U** — 2.4 GHz only, upper SMA port
- **ESP32-C5** — dual band 2.4 GHz + 5 GHz, lower SMA port

For antenna comparison testing, isolate the ESP32-C5 as the single test radio:

1. **Connect the antenna under test to the ESP32-C5 SMA port (lower)**
2. **Install the 50-ohm SMA terminator on the ESP32-WROOM SMA port (upper)**

The 50-ohm terminator is the Load standard from the LiteVNA calibration kit — it absorbs all incident RF with no reflection, properly terminating the WROOM radio without transmitting or receiving. This ensures all detected networks come from the C5 radio through the antenna under test, not from the WROOM radio independently.

**Do not leave the WROOM port open/unconnected** — an unterminated port reflects energy back into the radio and introduces an inconsistent variable across runs.

**Return the terminator to the calibration kit after testing** — it is a precision component.

### Biscuit Ultra Firmware Settings

The Biscuit Ultra (v1.4.1+) supports configurable RSSI threshold for duplicate BSSID logging:

| Setting | Behavior | Use case |
|---|---|---|
| RSSI threshold = 1 | Log every observation | Maximum data, very large files |
| RSSI threshold = 5 (default) | Re-log BSSID when RSSI changes by 5+ dBm | **Recommended for antenna comparison** |
| RSSI threshold = 50 | Effectively deduplicate to first-seen only | Minimal files, less useful for comparison |

**Use the default threshold of 5** for antenna comparison testing. This provides multiple RSSI readings per BSSID across a 5 minute run, enabling median RSSI calculation per network, while keeping file sizes manageable.

The Biscuit Ultra outputs standard **WigleWifi 1.6 format CSV** compatible with WiGLE upload and analysis tools.

### Test Location Setup

Select a fixed indoor location with the following characteristics:
- Consistent high network density (100+ unique BSSIDs detectable in 5 minutes)
- Near a window or exterior wall for maximum network visibility
- Away from large metal objects that may cause inconsistent reflections
- Reproducible device placement — mark the exact position with tape

**Mark the position precisely.** Place a physical marker (tape cross or similar) on the surface where the Biscuit sits. Return to this exact position for every run. Antenna orientation must be consistent — vertical for omnidirectional antennas.

**Reference location characteristics (validated):**
- 118 unique WiFi BSSIDs detected in 5 minutes
- 362 total WiFi observations (average ~3 observations per BSSID)
- 78 networks below -80 dBm — strong marginal signal pool
- RSSI range: -50 dBm to -94 dBm

### Test Procedure

**Before each session:**
- Confirm Biscuit Ultra firmware version
- Confirm RSSI threshold is set to 5 (default)
- Confirm 50-ohm terminator is on WROOM port
- Note time of day and any environmental conditions

**Per antenna run:**
1. Connect the antenna under test to the ESP32-C5 SMA port
2. Place Biscuit at the marked position, antenna vertical
3. Start wardrive logging
4. Run for **5 minutes** without moving the device
5. Stop logging and export CSV immediately
6. Label the file: `antenna_ID_run_N_YYYYMMDD_HHMMSS.csv`

**Run sequence:**
To control for time-of-day variation, alternate between antennas:

```
Run 1: Antenna A
Run 2: Antenna B
Run 3: Antenna A
Run 4: Antenna B
Run 5: Antenna A
Run 6: Antenna B
```

Minimum 3 runs per antenna. Allow 2 minutes between runs for the radio to reset and cool.

### Metrics

Filter the CSV to `Type == WIFI` entries only for WiFi antenna comparison. For each run calculate:

| Metric | Calculation | Why it matters |
|---|---|---|
| Total unique BSSIDs | Count distinct MACs | Overall sensitivity |
| Median RSSI per BSSID | Median of all observations per MAC, then mean across all BSSIDs | Robust central tendency — removes outlier readings |
| Networks > -70 dBm | Unique BSSIDs where median RSSI > -70 | Strong signal count |
| Networks -70 to -80 dBm | Unique BSSIDs where median RSSI -70 to -80 | Mid-range sensitivity |
| Networks < -80 dBm | Unique BSSIDs where median RSSI < -80 | **Primary comparison metric** |
| Minimum median RSSI | Weakest median RSSI across all BSSIDs | Maximum range indicator |
| Total observations | Raw row count (WIFI only) | Scan activity indicator |

**The sub -80 dBm unique BSSID count is the primary comparison metric.** Strong nearby APs are detected equally by any antenna. Antenna quality differences appear at the margins — the distant networks hovering near the noise floor.

**Use median RSSI per BSSID** rather than first-seen or mean. The default 5 dBm threshold generates ~3 observations per BSSID per 5 minute run with 6–7 dBm natural variation. Median is more robust than mean against momentary signal fluctuations.

### Data Analysis

For each antenna calculate the mean of each metric across all 3 runs. Compare means between antennas and calculate percentage difference.

Example comparison table:

| Metric | Antenna A (TC-01) | Antenna B (BFD-04) | Difference |
|---|---|---|---|
| Total unique BSSIDs | 121 | 103 | +17.5% |
| RSSI > -70 dBm | 22 | 21 | +4.8% |
| RSSI -70 to -80 dBm | 20 | 17 | +17.6% |
| RSSI < -80 dBm | 79 | 65 | +21.5% |
| Median RSSI (all networks) | -79 dBm | -82 dBm | +3 dBm |
| Minimum median RSSI | -94 dBm | -91 dBm | +3 dBm |

### BLE Antenna Comparison

The Biscuit Ultra also logs BLE devices (Type == BLE). For BLE antenna comparison on the WROOM/BT ports, the same methodology applies with the following modifications:

- Swap antenna on the BT SMA port under test
- Filter CSV to `Type == BLE` entries
- Same metrics apply — unique MAC count, sub -80 dBm count, median RSSI
- Note that BLE MAC addresses randomize on many devices — use RSSI distribution rather than unique MAC count as the primary metric for BLE

### Controls and Confounds

**Must maintain across all runs:**
- Same Biscuit Ultra device and firmware version
- Same RSSI threshold setting (default 5)
- 50-ohm terminator on WROOM port every run
- Same physical location and antenna orientation
- Same run duration (5 minutes)

**Known confounds to document:**
- Time of day — network activity varies, run tests within a 2-hour window
- AP power cycling — some APs restart periodically, introducing variance
- Nearby interference — microwave ovens, neighboring devices
- Weather — minor effect on marginal signal propagation

**Mitigation:**
The alternating A/B/A/B/A/B run sequence distributes time-of-day and interference effects equally between antennas, making the comparison fair even if conditions vary slightly between runs.

---

## Part 3: Combining the Results

### Interpretation Framework

| VNA Result | Field Result | Interpretation |
|---|---|---|
| PASS | Strong improvement | Antenna is well matched and efficient — deploy |
| PASS | Minimal improvement | Good match but other factor limiting (adapter sensitivity, location) |
| MARGINAL | Strong improvement | Antenna works despite poor match — check orientation/ground plane |
| MARGINAL | Minimal improvement | Poor match confirmed in field — consider alternatives |
| FAIL | Any | Confirmed failure — do not deploy |

### Reporting Format

For each antenna tested, document:

1. **VNA results** — resonant frequency, SWR at resonance, offset, per-band verdicts
2. **Field results** — mean metrics across 3 runs, percentage improvement vs reference antenna
3. **Ground plane notes** — tested with/without, effect observed
4. **Recommended use case** — based on combined VNA + field performance
5. **Overall verdict** — PASS / MARGINAL / FAIL / GRAVEYARD

---

## Appendix A: Band Reference

| Application | Frequency | Quarter-wave length | Half-wave length |
|---|---|---|---|
| 2.4 GHz WiFi center | 2450 MHz | 30.6 mm | 61.2 mm |
| 5 GHz WiFi low | 5150 MHz | 14.6 mm | 29.1 mm |
| 5 GHz WiFi center | 5500 MHz | 13.6 mm | 27.3 mm |
| ADS-B | 1090 MHz | 68.8 mm | 137.6 mm |
| UAT | 978 MHz | 76.7 mm | 153.4 mm |
| LoRa / ISM US | 915 MHz | 81.9 mm | 163.8 mm |
| GPS L1 | 1575 MHz | 47.6 mm | 95.2 mm |
| AIS | 162 MHz | 462.9 mm | 925.9 mm |
| FM radio center | 98 MHz | 765.3 mm | 1530.6 mm |

---

## Appendix B: Biscuit Ultra CSV Format Reference

The Biscuit Ultra outputs WigleWifi 1.6 format. Column reference:

| Column | Description | Notes |
|---|---|---|
| MAC | BSSID or BLE MAC address | Use as unique network identifier |
| SSID | Network name | May be empty (hidden networks) |
| AuthMode | Security type | WPA2_PSK, WPA3_PSK, OPEN, BLE, etc. |
| FirstSeen | Timestamp of this observation | ISO format UTC |
| Channel | WiFi channel number | 0 for BLE |
| Frequency | Center frequency in MHz | 0 for BLE |
| RSSI | Signal strength in dBm | Negative value — higher is stronger |
| Type | Entry type | WIFI or BLE |

**Filtering for analysis:**
```python
# WiFi only
wifi = df[df['Type'] == 'WIFI']

# Per-BSSID median RSSI
median_rssi = wifi.groupby('MAC')['RSSI'].median()

# Sub -80 dBm count
sub80 = (median_rssi < -80).sum()
```

---

*Methodology developed through empirical testing of 80+ antennas across 18 batches using LiteVNA 64 and Biscuit Ultra (firmware v1.4.1). Version 2.0.*
