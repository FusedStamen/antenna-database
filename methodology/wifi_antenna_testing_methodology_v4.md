# WiFi Antenna Testing Methodology
### VNA Characterization + Fixed-Location Field Comparison + Open Field Range Comparison
*Developed for wardriving and WiFi monitoring antenna selection*

---

## Overview

This methodology combines three complementary evaluation approaches:

1. **Tier 1 — VNA Bench Testing** — objective electrical characterization of antenna impedance match using a LiteVNA 64
2. **Tier 2 — Fixed-Location Field Testing** — real-world comparative performance measurement using a Biscuit Ultra wardriving device in a controlled indoor environment
3. **Tier 3 — Open Field Range Comparison** — distance-normalized outdoor gain comparison using a controlled AP source for antennas requiring additional rigor

No single tier is sufficient alone. Tier 1 tells you how well the antenna converts electrical energy to RF radiation. Tier 2 tells you how that translates to actual network detection in a real environment. Tier 3 provides the most rigorous field gain comparison achievable without anechoic chamber equipment. Together they give a complete, honest picture.

**All three tiers are required for a complete antenna evaluation.** Tier 3 is applied selectively based on criteria in that section, but Tier 1 and Tier 2 are mandatory for every antenna that proceeds beyond initial screening.

---

## Part 1: VNA Bench Testing (Tier 1)

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

Recalibrate if the VNA is moved, the temperature changes significantly, or adapters are swapped. For large batch sessions, perform a verification sweep on TC-01 every 15–20 antennas. If TC-01 reads outside 0.05 SWR of baseline, recalibrate before continuing.

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

**Step 1 — Marker testing (initial screening):**
Before committing to a full S1P export, do a quick marker pass on each antenna. Load the calibration profile, connect the antenna, allow 3–5 scan cycles to stabilize, and place the marker at the SWR minimum. Record the resonant frequency and SWR at resonance. This screens obviously broken or out-of-band antennas before spending time on full exports.

**Step 2 — S1P export:**
For all antennas that pass initial screening, export S1P files per the naming convention in Appendix C. Export both bands for dual-band antennas. S1P timestamps serve as the test time record.

**Step 3 — Automated batch processing (sort_antennas.py):**
Run `sort_antennas.py` against the S1P folder to sort antennas into Good / Marginal / Do_Not_Use bins based on worst in-band SWR. This is the canonical Tier 1 pass/fail gate. Script available at:
`https://github.com/FusedStamen/antenna-database/blob/main/scripts/sort_antennas.py`

**Step 4 — Per-antenna deep analysis (analyze_antenna.py):**
Run `analyze_antenna.py` on the full S1P folder to generate resonant frequency, band-edge SWRs, resonance offset, mismatch loss, and per-file verdict. Results must agree with sort_antennas.py. Any disagreement between the three data sources (markers, sort script, analyze script) is a flag to investigate — bad connector seating, wrong calibration profile, or stray file. Script available at:
`https://github.com/FusedStamen/antenna-database/blob/main/scripts/analyze_antenna.py`

All three data sources must agree before a Tier 1 verdict is considered final.

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
| Worst in-band SWR | Maximum SWR within the band window — verdict basis |
| Verdict | Good / Marginal / Do_Not_Use per criteria below |

### Verdict Criteria

Verdicts are based on **worst in-band SWR** — the maximum SWR measured anywhere within the target band window, not SWR at resonance. This matches the sort_antennas.py and analyze_antenna.py verdict logic exactly.

| Worst in-band SWR | Reflected Power | Loss (dB) | Verdict |
|---|---|---|---|
| < 2.0 | < 11% | < 0.51 dB | **Good** |
| 2.0 – 3.0 | 11–25% | 0.51–1.25 dB | **Marginal** |
| > 3.0 | > 25% | > 1.25 dB | **Do_Not_Use** |

**For wardriving applications, SWR < 2.0 is a solid pass.** Reflected power under 11% and mismatch loss under 0.51 dB are not meaningful for passive receive use cases. The Good/Marginal distinction within the under-2.0 range is informational only — both proceed to Tier 2.

**Marginal antennas are noted by which band is weak** — e.g. "Marginal — 5G weak (max SWR 2.06), 2.4G good (1.22)". This is logged in the database notes column.

**Note:** Resonance offset matters in addition to SWR. An antenna with worst in-band SWR 1.8 but resonance centered on band is more useful than one with SWR 1.2 but resonance 150 MHz off-center. Always evaluate both.

### Cable-Affected Measurements

For antennas with integral cables (mag-mounts, router arrays), full characterization is not possible without recalibrating at the cable end. For these antennas:

- Use the same sweep profile as direct-connect antennas
- Note that absolute SWR values are not meaningful due to standing wave ripple
- Compare **valley floor SWR** between units — the lowest dip visible on the ripple trace
- A lower valley floor indicates a better-matched antenna element regardless of cable
- Mark all results as "relative comparison only — cable-affected measurement"

### S1P File Export

Export S1P files for all Tier 1 measurements. File naming convention:

```
[BATCHID]-[UNITNUMBER]-[BAND].s1p
```

Examples:
- `TC-01-2.4ghz.s1p`
- `BD-01-2.4ghz.s1p`
- `ACC-3-5ghz.s1p`

Use lowercase band designations: `2.4ghz`, `5ghz`, `915mhz`, `1090mhz`, `gps`. Export both bands for dual-band antennas. S1P timestamps serve as the test time record — no separate time logging required.

---

## Part 2: Fixed-Location Field Testing (Tier 2)

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
Each antenna is tested independently with the WROOM port terminated. Run each antenna a minimum of 3 times:

```
Run 1: Antenna under test
Run 2: Antenna under test
Run 3: Antenna under test
```

Allow 2 minutes between runs for the radio to reset and cool. Run all sessions for a given antenna within a 2-hour window to minimize time-of-day variance.

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

---

## Part 3: Open Field Range Comparison (Tier 3)

### Purpose

Tier 3 provides distance-normalized real-world gain comparison between antennas that have already passed Tier 1 VNA characterization and Tier 2 fixed-location field testing. It does not produce absolute dBi ratings — it produces relative gain figures expressed in dB at a known distance under controlled outdoor conditions. This is intentional: absolute dBi measurement requires anechoic chamber equipment. Tier 3 provides the most rigorous field comparison achievable without that equipment while remaining honest about what it measures.

**Apply Tier 3 when:**
- Two antennas are close in Tier 1 and Tier 2 results and a tiebreaker is needed
- An antenna makes specific gain claims that warrant independent verification
- A new candidate antenna is being evaluated as a potential reference standard
- A marketing-heavy antenna (e.g. Bolton Dart) needs field verification against claims

---

### Equipment

- **uConsole** (CM4, AC1200 module) running Linux — AP platform
- **hostapd** for AP mode on AC1200
- **iw** for TX power and channel control
- **Reference antenna** on uConsole AC1200 external port — selected from Tier 1/2 results (see Reference Antenna Selection below)
- **Biscuit Ultra** (firmware v1.4.1+) as receive platform
- **50-ohm terminator** on WROOM port as per Tier 2 protocol
- **Antenna under test** on ESP32-C5 port
- **Tape measure** — minimum 50m
- **Tripod or monopod** for consistent AP height
- **analyze_wardrive.py** for post-processing

---

### Reference Antenna Selection

The Tier 3 reference antenna is selected from Tier 1 and Tier 2 results and mounted on the uConsole AC1200 AP side. It does not change within or between Tier 3 sessions unless explicitly cross-calibrated.

**Selection criteria:**
- Tier 1 worst in-band SWR < 1.5 across full target band
- Tier 2 consistent performance, low run-to-run variance
- Multiple units tested with low unit-to-unit variance — confirms manufacturing consistency

**Current reference standards:**
- 2.4 GHz reference: **TC-01** (TECHTOO 9dBi) — SWR 1.001 Phase 1 / 1.030 Phase 2
- Dual-band reference: **BPi-01** (Banana Pi R3 bundled) — SWR 1.026 / 1.141

If the reference antenna is replaced between sessions, run a cross-calibration comparison at P3 before publishing comparative results.

---

### Site Requirements

- Open flat ground with no large metal objects or structures within 20m of the test path
- Minimal foot traffic during test runs
- Low wind preferred — antenna orientation stability matters
- **Validated reference site: Gore Place field, Watertown MA**

---

### AP Setup Procedure

**1. Verify AC1200 interface name:**
```bash
iw dev
```

**2. Set fixed channel and TX power:**
```bash
sudo iw dev wlan1 set channel 6
sudo iw dev wlan1 set txpower fixed 1000  # 10 dBm — value is in mBm
```

**3. Verify TX power was accepted:**
```bash
iw dev wlan1 info
```

**4. hostapd configuration:**
```
# /etc/hostapd/tier3_test.conf
interface=wlan1
ssid=ANTENNATEST
channel=6
hw_mode=g
tx_power=10
beacon_int=100
```

**5. Start AP:**
```bash
sudo hostapd /etc/hostapd/tier3_test.conf
```

**6. Verify TX power against expected path loss** — before the first Tier 3 session, place the Biscuit Ultra at exactly 10m with a known reference antenna and confirm median RSSI is approximately -46 dBm. This is the expected free space received power at 10m with 10 dBm TX at 2.4 GHz. If the measured value differs by more than 3 dB, adjust TX power setting until the 10m reference reads correctly. Document the verified TX power setting.

**7. Mount uConsole on tripod at 1.5m height.** Mark the AP position with a stake or tape flag. AP position does not move for the duration of the session.

---

### Test Positions

Measure distance from AP position along a straight line perpendicular to the AP antenna axis:

| Position | Distance | Expected RSSI (10 dBm TX, free space) |
|---|---|---|
| P1 | 10m | ~-46 dBm |
| P2 | 25m | ~-54 dBm |
| P3 | 50m | ~-60 dBm |
| P4 | 100m | ~-66 dBm |

Mark each position with a stake or tape flag. The Biscuit Ultra sits on a non-conductive surface (foam pad) at each position. Antenna vertical, consistent orientation toward AP.

**Primary test distance is P3 (50m)** — far enough to show meaningful gain differences between well-matched antennas, close enough for reliable detection of marginal antennas. P4 is used for high-gain antenna evaluation or when P3 differences are too small to be conclusive.

---

### Test Procedure

**Before each session:**
- Confirm uConsole AP is running on correct channel at verified TX power
- Confirm reference antenna is mounted on AC1200 port
- Confirm Biscuit Ultra firmware version and RSSI threshold = 5
- Confirm 50-ohm terminator on WROOM port
- Note weather conditions, wind, time of day

**Per antenna at each position:**
1. Connect antenna under test to ESP32-C5 port
2. Place Biscuit at position marker on foam pad, antenna vertical
3. Run 3 minute wardrive capture
4. Export and label: `tier3_[BATCHID]_[position]_run[N]_[YYYYMMDD_HHMMSS].csv`
5. Swap to next antenna, repeat

**Run sequence at each position:**
```
Run 1: Antenna A
Run 2: Antenna B
Run 3: Antenna A
Run 4: Antenna B
Run 5: Antenna A
Run 6: Antenna B
```

Minimum 3 runs per antenna per position. Allow 1 minute between runs.

---

### Metrics

Filter to the ANTENNATEST SSID only — controlled AP signal, not ambient networks:

```python
import pandas as pd

df = pd.read_csv('tier3_file.csv', skiprows=1)

# Filter to test AP only
test_ap = df[df['SSID'] == 'ANTENNATEST']

# Median RSSI per run
median_rssi = test_ap['RSSI'].median()

# Observation count — lower means antenna is struggling
obs_count = len(test_ap)

# RSSI variance — high variance indicates multipath or instability
rssi_std = test_ap['RSSI'].std()
```

| Metric | Description | Notes |
|---|---|---|
| Median RSSI | Primary metric — median of all observations of test AP per run | Higher (less negative) is better |
| RSSI std deviation | Spread of readings | High variance indicates multipath or instability |
| Observation count | Number of beacon detections per run | Lower count means antenna is struggling at this distance |

**Mean median RSSI across 3 runs** is the final reported figure per antenna per position.

---

### Reporting

Express results as relative gain versus reference antenna. Do not express results as absolute dBi.

Example results table:

| Antenna | Tier 1 worst SWR (2.4G) | P3 Median RSSI | vs Reference | Relative Gain |
|---|---|---|---|---|
| TC-01 (reference) | 1.030 | -61 dBm | — | 0 dB |
| BPi-01 | 1.026 | -59 dBm | +2 dB | +2 dB |
| Bingfu 3dBi RP-SMA | ~1.4 | -62 dBm | -1 dB | -1 dB |
| Bolton Dart | ~2.3 | -67 dBm | -6 dB | -6 dB |

**Correct reporting format:** *"BPi-01 shows +2 dB relative gain vs TC-01 reference at 50m, verified 10 dBm TX, 2.4 GHz channel 6, Gore Place field, Watertown MA."*

**Incorrect:** *"BPi-01 measured 5.2 dBi."*

---

### Notes and Limitations

- Results are valid for the stated conditions only — distance, TX power, site, frequency, AP reference antenna
- Ground reflections are not zero in field conditions — results are not true free-space measurements
- TX power accuracy depends on AC1200 chipset firmware — verify against expected path loss before each session and document the verified value
- Weather and wind affect marginal signal propagation — document conditions for each session
- Run all tests within a 1-hour window to minimize time-of-day variance
- Tier 3 complements but does not replace Tier 1 and Tier 2 — an antenna that fails Tier 1 should not proceed to Tier 3

---

## Part 4: Combining the Results

### Interpretation Framework

| Tier 1 | Tier 2 | Tier 3 | Interpretation |
|---|---|---|---|
| Good | Strong improvement | — | Well matched and efficient — deploy |
| Good | Minimal improvement | — | Good match, other factor limiting — check location or adapter |
| Good | Strong improvement | High relative gain | Confirmed high performer — reference candidate |
| Good | Close to reference | Lower relative gain | Tier 1 passes but real-world gain limited — check radiation pattern |
| Marginal | Strong improvement | — | Works despite weak band — check orientation/ground plane |
| Marginal | Minimal improvement | — | Weak match confirmed in field — consider alternatives |
| Do_Not_Use | Any | — | Confirmed failure — do not proceed to Tier 2 or 3 |

### Reporting Format

For each antenna tested, document:

1. **Tier 1 results** — resonant frequency, SWR at resonance, worst in-band SWR, resonance offset, per-band verdicts, S1P file reference
2. **Tier 2 results** — mean metrics across 3 runs, percentage improvement vs reference antenna
3. **Tier 3 results** — relative gain vs reference at stated distance and conditions *(if conducted)*
4. **Ground plane notes** — tested with/without, effect observed
5. **Recommended use case** — based on combined tier performance
6. **Overall verdict** — Good / Marginal / Do_Not_Use

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

**Filtering for Tier 2 analysis:**
```python
# WiFi only
wifi = df[df['Type'] == 'WIFI']

# Per-BSSID median RSSI
median_rssi = wifi.groupby('MAC')['RSSI'].median()

# Sub -80 dBm count
sub80 = (median_rssi < -80).sum()
```

**Filtering for Tier 3 analysis:**
```python
# Test AP only
test_ap = df[df['SSID'] == 'ANTENNATEST']

# Median RSSI and variance
median_rssi = test_ap['RSSI'].median()
rssi_std = test_ap['RSSI'].std()
obs_count = len(test_ap)
```

---

## Appendix C: S1P File Naming Convention

```
[BATCHID]-[UNITNUMBER]-[BAND].s1p
```

| Component | Format | Example |
|---|---|---|
| BATCHID | Uppercase batch code from master database | TC, BD, BF3R, ACC |
| UNITNUMBER | Sequential integer, no zero-padding required | 1, 2, 12 |
| BAND | Lowercase frequency designation | 2.4ghz, 5ghz, 915mhz, gps |

**Examples:**
- `TC-01-2.4ghz.s1p`
- `BD-2-5ghz.s1p`
- `ACC-6-2.4ghz.s1p`
- `TG05-1-2.4ghz.s1p`

S1P file timestamps serve as the test time record. No separate time logging is required for Tier 1 measurements.

---

## Appendix D: Tier 1 Processing Scripts

Two scripts handle automated Tier 1 processing. Both must produce consistent verdicts — any disagreement between them or with marker readings is a flag to investigate.

**sort_antennas.py** — batch sorts all S1P files in a folder into Good / Marginal / Do_Not_Use subdirectories based on worst in-band SWR. Run this first after completing a batch of S1P exports.

```
python sort_antennas.py
```

Source: `https://github.com/FusedStamen/antenna-database/blob/main/scripts/sort_antennas.py`

**analyze_antenna.py** — per-antenna deep analysis. Outputs resonant frequency, band-edge SWRs, worst in-band SWR, resonance offset, mismatch loss dB, and verdict. Supports single file, batch directory, optional SWR plot PNG, and CSV append mode.

```
# Single antenna with plot
python analyze_antenna.py BF3R-01-2.4ghz.s1p --band 2.4 --plot

# Full batch with CSV output
python analyze_antenna.py --batch .\antennas_raw\ --csv batch_results.csv
```

Source: `https://github.com/FusedStamen/antenna-database/blob/main/scripts/analyze_antenna.py`

Both scripts use the same verdict thresholds: worst in-band SWR < 2.0 = Good, 2.0–3.0 = Marginal, > 3.0 = Do_Not_Use.

---

*Methodology developed through empirical testing of 130+ antennas across multiple batches using LiteVNA 64, Biscuit Ultra (firmware v1.4.1), and uConsole AC1200. Version 4.0.*
