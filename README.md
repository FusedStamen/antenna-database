# antenna-database

A systematic, empirically measured WiFi antenna database for wardriving and RF monitoring applications. All antennas characterized using a LiteVNA 64 vector network analyzer with standardized methodology, and field-tested using a Biscuit Ultra wardriving device.


---

## Data Status

**Tier 1 (VNA) testing is complete for the current antenna inventory.** All antennas have been characterized using the full methodology - S1P exports, automated batch processing via `sort_antennas.py` and `analyze_antenna.py`, and marker readings cross-validated against script output. Results are in `database/`.

**Tier 2 (field testing) is in progress.** Good and Marginal antennas from Tier 1 proceed to Biscuit Ultra fixed-location field testing. Results will be committed to `wardriving_logs/` as sessions are completed.

**Tier 3 (open field range comparison)** is applied selectively for tiebreakers and gain claim verification. Site: Gore Place field, Watertown MA.

---

## What's in here

| Directory | Contents |
|---|---|
| `methodology/` | Full testing methodology documentation (v4) |
| `vna_data/` | Raw S1P exports per antenna per band |
| `wardriving_logs/` | Biscuit Ultra CSV logs from field comparison runs |
| `database/` | Master antenna database CSV with all results and verdicts |
| `scripts/` | Analysis scripts for S1P files and wardriving logs |

---

## Antennas tested

130+ antennas across 20+ batches covering:

- 2.4 GHz single-band sticks (HF, TC, AL, SB batches)
- Dual-band 2.4+5 GHz sticks (BF3R, BF3S, BF8, BFD, BPi, ACM, ACH batches)
- Dual-band paddles (BFD batch)
- Dual-band magmounts with cable (BFCable batch)
- MIMO router arrays (AccelTex4, AccelTex6, MIMO2, MIMO3 batches)
- Tri-band 2.4+5+6 GHz (SF batch)
- LoRa 915 MHz (LR, Gizont, Muzi, MakerHawk)
- LTE broadband (LTE batch — Sixfab blade, Spypoint trail cam)
- ADS-B 1090 MHz (HzFitInc, RatlSnake M6 telescopic)
- GPS L1 (ZBM2 GPS stubby)
- BLE/2.4 GHz (ZBM2 BLE stubby)
- Specialty and graveyard (D3, EW, RED, TAO05/Bolton Dart, yagi)

---

## Current Tier 1 standings

**130+ antennas tested. 118 Good / 57 Marginal / 60 Do_Not_Use.**

Verdicts are based on **worst in-band SWR** within the target band window - not SWR at resonance. Threshold: < 2.0 = Good, 2.0–3.0 = Marginal, > 3.0 = Do_Not_Use. For wardriving passive receive applications, SWR < 2.0 represents under 11% reflected power and under 0.51 dB mismatch loss — not meaningful in practice.

### Top 10 dual-band (2.4 + 5 GHz), ranked by average worst in-band SWR

| Rank | Unit | Description | Connector | 2.4G worst | 5G worst | Avg |
|---|---|---|---|---|---|---|
| 1 | MIMO2-02 | Unknown dual-band MIMO panel | RP-SMA Male | 1.140 | 1.116 | 1.128 |
| 2 | BFCable-01 | Bingfu 9dBi dual-band magmount | SMA Male | 1.141 | 1.250 | 1.196 |
| 3 | BFCable-02 | Bingfu 9dBi dual-band magmount | SMA Male | 1.217 | 1.284 | 1.251 |
| 4 | MIMO3-02 | Unknown 3-port MIMO panel | RP-SMA Male | 1.227 | 1.429 | 1.328 |
| 5 | MIMO3-01 | Unknown 3-port MIMO panel | RP-SMA Male | 1.329 | 1.342 | 1.336 |
| 6 | MIMO2-01 | Unknown dual-band MIMO panel | RP-SMA Male | 1.268 | 1.424 | 1.346 |
| 7 | BF3R-01 | Bingfu 3dBi RP-SMA dual-band | RP-SMA Male | 1.468 | 1.228 | 1.348 |
| 8 | BF3R-04 | Bingfu 3dBi RP-SMA dual-band | RP-SMA Male | 1.510 | 1.211 | 1.361 |
| 9 | ACC-05 | AccelTex 4-element MIMO panel port | RP-SMA Male | 1.444 | 1.411 | 1.428 |
| 10 | BF3R-02 | Bingfu 3dBi RP-SMA dual-band | RP-SMA Male | 1.617 | 1.246 | 1.432 |

**Best conventional buyable RP-SMA stick: BF3R-01.** The MIMO panels and magmounts rank higher but are not practical as individual wardriving sticks.

### Notable findings

**MIMO panels (Facebook Marketplace, unknown brand):** Cleanest results in the entire database. MIMO2-02 is the best single antenna measured - SWR 1.140 / 1.116 across both bands. No buy link available.

**Bingfu BF vs BFD — same brand, different antenna:** BF paddles (claimed 8dBi dual-band) are effectively 2.4 GHz only - 5G SWR 4.25–6.09. BFD paddles (same claimed spec) are functional dual-band with 5G SWR under 2.0. Same Bingfu branding, clearly different internal designs.

**Bolton Dart / Taoglas GW.05:** SWR 4.2–4.5 at 2.4 GHz in free space. Designed for metal-chassis routers with a PCB ground plane - not for portable wardriving use. Do_Not_Use verdict confirmed across both units.

**HzFitInc ADS-B 1090 MHz:** SWR 1.020 exactly at 1090 MHz. Best single spot reading in the database.

**RatlSnake M6 telescopic at optimal length (3 sections collapsed):** SWR 1.200 at 1090 MHz - competitive with the dedicated ADS-B stubby. Detailed length-vs-SWR sweep documented in database.

---

## Quick start

### Analyze a VNA S1P export

```bash
pip install scikit-rf numpy pandas matplotlib

# Single file with plot
python scripts/analyze_antenna.py vna_data/BF3R-01-2.4ghz.s1p --band 2.4 --plot

# Batch analyze a directory
python scripts/analyze_antenna.py --batch vna_data/ --csv batch_results.csv
```

### Sort antennas into Good / Marginal / Do_Not_Use

```bash
python scripts/sort_antennas.py
# Reads from ./antennas_raw/, writes to ./antennas_sorted/Good|Marginal|Do_Not_Use/
```

### Analyze a Biscuit Ultra wardriving log

```bash
pip install pandas numpy

# Single run
python scripts/analyze_wardrive.py wardriving_logs/BF3R-01_run1.csv

# Compare two antennas (3 runs each)
python scripts/analyze_wardrive.py --compare \
    wardriving_logs/TC-01_run1.csv wardriving_logs/TC-01_run2.csv wardriving_logs/TC-01_run3.csv \
    wardriving_logs/BF3R-01_run1.csv wardriving_logs/BF3R-01_run2.csv wardriving_logs/BF3R-01_run3.csv \
    --labels "TC-01 (TECHTOO 9dBi)" "BF3R-01 (Bingfu 3dBi)"
```

---

## Methodology

Full testing methodology is documented in [`methodology/wifi_antenna_testing_methodology_v4.md`](methodology/wifi_antenna_testing_methodology_v4.md).

**Tier 1 - VNA bench testing:**
- LiteVNA 64 with NanoVNA-App
- Three-step process: marker screening → S1P export → automated processing
- Separate calibration profiles per frequency range
- 6"x6" steel ground plane for monopole/stub antennas
- All three data sources (markers, sort_antennas.py, analyze_antenna.py) must agree
- Verdict based on worst in-band SWR, not SWR at resonance

**Tier 2 - Fixed-location field testing:**
- Biscuit Ultra (firmware v1.4.1+), RSSI threshold default 5
- Antenna under test on ESP32-C5 SMA port
- 50-ohm terminator on ESP32-WROOM SMA port (eliminates WROOM as a confound)
- 3 runs per antenna, 5 minutes each
- Primary metric: unique BSSID count with median RSSI < -80 dBm

**Tier 3 - Open field range comparison:**
- uConsole (CM4, AC1200) as controlled AP at verified TX power
- Biscuit Ultra as receiver at measured distances (P3 = 50m primary)
- Results expressed as relative gain vs TC-01 reference — no absolute dBi claims
- Applied selectively for tiebreakers and gain claim verification

---

## S1P file naming convention

```
{BATCHID}-{UNIT}-{band}.s1p

Examples:
  TC-01-2.4ghz.s1p
  BF3R-04-5ghz.s1p
  LR-02-lora.s1p
  HzFitInc-01-1090mhz.s1p
```

Lowercase band designations: `2.4ghz`, `5ghz`, `915mhz`, `1090mhz`, `gps`, `uhf`.

## Wardriving log naming convention

```
{ANTENNA_ID}_run{N}_{YYYYMMDD}_{HHMMSS}.csv

Examples:
  TC-01_run1_20260520_140000.csv
  BF3R-01_run2_20260520_140800.csv
```

---

## Hardware

- **VNA:** LiteVNA 64
- **VNA Software:** NanoVNA-App
- **Field test device:** Biscuit Ultra (firmware v1.4.1)
- **Ground plane:** 6" x 6" steel plate
- **Calibration kit:** SMA SOLT standards
- **Field AP:** uConsole CM4 with AC1200 module

---

## Community submissions

This database grows through outside contributions. Everyone who submits a tested antenna gets credited here - thank you!

| Antenna | Batch | Submitted by | Verdict |
|---|---|---|---|
| [Seeed 2.4G/5G RP-SMA, 1.13mm coax, 130mm](https://www.seeedstudio.com/2-4G-5G-External-Antenna-with-RP-SMA-Male-Connector-and-1-13-Coaxial-Cable-130mm-Set-p-6316.html) | — | FifeZaro (Discord) | Pending |
| [Seeed 2.4GHz 2.81dBi for XIAO ESP32C3](https://www.seeedstudio.com/2-4GHz-2-81dBi-Antenna-for-XIAO-ESP32C3-p-5475.html) | — | FifeZaro (Discord) | Pending |

Want to see your antenna (and name) added to this table? Test it using the methodology below and open a PR - or just send a link our way:
- **Discord:** FusedStamen
- **Email:** antennas@fusedstamen.com

---

## Contributing

If you've tested antennas using this methodology and want to contribute results, open a PR with:
- S1P files in `vna_data/` following the naming convention above
- Wardriving logs in `wardriving_logs/`
- A row added to `database/antenna_master_database.csv`
- A row added to the [Community submissions](#community-submissions) table above, with your name/handle in the "Submitted by" column

Please document connector type, ground plane configuration, and which methodology version was used.

---

## License

MIT - see [LICENSE](LICENSE). Attribution appreciated but not required.

If you use this data in a write-up or project, a mention of the repo is always welcome.
