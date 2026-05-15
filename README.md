# antenna-database

A systematic, empirically measured WiFi antenna database for wardriving and RF monitoring applications. All antennas characterized using a LiteVNA 64 vector network analyzer with standardized methodology, and field-tested using a Biscuit Ultra wardriving device.

> **By fusedstamen** — if you found this useful, check out [WDGoWars](https://github.com/fusedstamen/WDGoWars).

---

## Data Status

> **⚠️ Current database is Phase 1 — marker readings only.**

The antenna database currently contains results from an initial testing session conducted before this methodology was formalized. Measurements were taken by reading marker values directly from the NanoVNA-App display and logging them manually. No raw S1P files were exported during this session.

**Phase 2 testing is in progress.** Every antenna in the database will be retested using the full methodology documented here — S1P exports, CSV sweeps, and PNG plots per antenna per band, with the 6"x6" steel ground plane protocol applied consistently. Phase 2 results will be committed to `vna_data/` as they are completed.

**Phase 1 vs Phase 2 comparison is intentional.** Comparing the two datasets serves as a consistency check and adds rigor — if results align closely it validates both the original measurements and the methodology. Significant divergences will be documented and investigated. This cross-validation approach is part of the methodology and will be written up as part of the accompanying Medium article series.

**What this means for current database entries:**
- Resonant frequency and SWR values are accurate to within typical marker reading precision (~1-2 MHz, ~0.005 SWR)
- Verdicts (PASS/MARGINAL/FAIL) are reliable for antenna selection purposes
- Raw S1P data for independent verification is not yet available for Phase 1 entries
- Phase 2 entries will include full raw data and supersede Phase 1 entries where both exist

---

## What's in here

| Directory | Contents |
|---|---|
| `methodology/` | Full testing methodology documentation (VNA + field testing) |
| `vna_data/` | Raw S1P exports, CSV sweeps, and PNG plots per antenna |
| `wardriving_logs/` | Biscuit Ultra CSV logs from field comparison runs |
| `database/` | Master antenna database CSV with all results and verdicts |
| `scripts/` | Analysis scripts for S1P files and wardriving logs |

---

## Antennas tested

80+ antennas across 18 batches covering:

- 2.4 GHz single-band sticks (HF, TC, AL, SB batches)
- Dual-band 2.4+5 GHz sticks (BFD, BPi, RED, BF, PB, D3 batches)
- Tri-band 2.4+5+6 GHz (SF batch)
- LoRa 915 MHz (LR batch)
- LTE broadband (LTE batch)
- GPS L1 (GPS batch)
- Mag-mount cable antennas (BF-Cable batch)
- MIMO router arrays (MIMO2, MIMO3 batches)
- Specialty antennas (ZBM2 BLE/GPS, Bolton Dart, Bolton Technical)

---

## Quick start

### Analyze a VNA S1P export

```bash
pip install scikit-rf numpy pandas matplotlib

# Single file
python scripts/analyze_antenna.py vna_data/HF/HF-01_2400MHz.s1p --band 2.4 --plot

# Batch analyze a directory
python scripts/analyze_antenna.py --batch vna_data/HF/ --csv results.csv
```

### Analyze a Biscuit Ultra wardriving log

```bash
pip install pandas numpy

# Single run
python scripts/analyze_wardrive.py wardriving_logs/TC-01_run1.csv

# Compare two antennas (3 runs each)
python scripts/analyze_wardrive.py --compare \
    wardriving_logs/TC-01_run1.csv wardriving_logs/TC-01_run2.csv wardriving_logs/TC-01_run3.csv \
    wardriving_logs/BFD-04_run1.csv wardriving_logs/BFD-04_run2.csv wardriving_logs/BFD-04_run3.csv \
    --labels "TC-01 (TECHTOO 9dBi)" "BFD-04 (Bingfu 8dBi)"
```

---

## Key findings

**Best 2.4 GHz single-band:** TC-01 (TECHTOO 9dBi) — SWR 1.001, resonance at 2446 MHz, dead centered.

**Best 5 GHz coverage:** RED-01/RED-02 (flat paddle dipole) — broadest 5 GHz bandwidth of any antenna tested, good across entire 5150–5850 MHz range.

**Best dual-band stubby:** BPi-01 (Banana Pi router antenna) — SWR 1.026 at 2.4 GHz, 1.141 at 5 GHz.

**Best LoRa:** LR-02 (Slinkdsco 5dBi N-male) — SWR 1.012 at 898 MHz, meets spec.

**Notable failures:** D3 batch (3dBi dual-band stubs) — both bands miss target by 200+ MHz. Bolton Dart / Taoglas GW.05 — SWR 3.0 flat in free space, requires metal chassis ground plane.

**The Taoglas myth:** The Taoglas GW.05 and Bolton Dart (same antenna) are popular in the wardriving and pentesting community but measure SWR ~3.0 at 2.4 GHz and ~2.0 at 5 GHz in free space. They are designed for metal-chassis routers with a PCB ground plane. Taoglas's own spec sheet confirms this behavior. Generic BPi router antennas outperform them for portable wardriving use.

---

## Methodology

Full testing methodology is documented in [`methodology/wifi_antenna_testing_methodology_v2.md`](methodology/wifi_antenna_testing_methodology_v2.md).

Summary:

**VNA testing:**
- LiteVNA 64 with NanoVNA-App
- Separate calibration profiles per frequency range
- 6"x6" steel ground plane for monopole/stub antennas
- S1P + CSV + PNG exported per antenna per band

**Field testing:**
- Biscuit Ultra (firmware v1.4.1+), RSSI threshold default 5
- Antenna under test on ESP32-C5 SMA port
- 50-ohm terminator on ESP32-WROOM SMA port
- 5 minute runs, alternating A/B/A/B/A/B sequence
- Primary metric: unique BSSID count with median RSSI < -80 dBm

---

## VNA S1P file naming convention

```
{BATCH}-{ID}_{FREQ}MHz.s1p

Examples:
  HF-01_2400MHz.s1p
  BFD-04_2400MHz.s1p
  BFD-04_5000MHz.s1p
  LR-02_915MHz.s1p
  GPS-00_1575MHz.s1p
```

## Wardriving log naming convention

```
{ANTENNA_ID}_run{N}_{YYYYMMDD}_{HHMMSS}.csv

Examples:
  TC-01_run1_20260520_140000.csv
  TC-01_run2_20260520_140800.csv
  BFD-04_run1_20260520_140500.csv
```

---

## Hardware

- **VNA:** LiteVNA 64
- **VNA Software:** NanoVNA-App v1.1.208
- **Field test device:** Biscuit Ultra (firmware v1.4.1)
- **Ground plane:** 6" x 6" steel plate
- **Calibration kit:** SMA SOLT standards

---

## Contributing

If you've tested antennas using this methodology and want to contribute results, open a PR with:
- S1P files in the appropriate `vna_data/` subdirectory
- Wardriving logs in `wardriving_logs/`
- A row added to `database/antenna_master_database.csv`

Please follow the naming conventions above and document connector type, cable length, and ground plane configuration used.

---

## License

MIT — see [LICENSE](LICENSE). Attribution appreciated but not required.

If you use this data in a write-up or project, a mention of the repo is always welcome.
