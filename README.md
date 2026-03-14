# Electricity Usage Analyzer

Analyze household electricity usage and compare supplier plans by hour and day.

## What this project does

- Reads `meter.csv` and builds usage analysis by time of day and day of week
- Prints summary stats and peak usage windows
- Generates `electricity_analysis.png`
- Compares supplier plans in `supplier_comparison.py`
- Supports EV what-if charging scenarios

## Quick start

```bash
pip install -r requirements.txt
python main.py
python supplier_comparison.py
```

## Input data

Expected data fields:
- Date (`DD/MM/YYYY`)
- Time (`HH:MM`)
- Consumption (`kWh`)

`load_data()` supports:
- IEC-style exports (Hebrew headers + metadata rows)
- Simple 3-column CSV (`Date,Time,Consumption`)

Invalid rows are skipped automatically.

## Main analysis (`main.py`)

Outputs:
- Summary statistics (date range, total, avg, min, max, count)
- Average usage by 15-minute time slot
- Average usage by day of week
- Time/day pivot table
- Peak hours (top percentile)
- Chart file: `electricity_analysis.png`

Run:

```bash
python main.py
```

## Supplier comparison (`supplier_comparison.py`)

The script calculates cost as:

`cost = consumption * BASE_RATE * multiplier`

Where:
- `BASE_RATE` is the shared pre-discount price
- `multiplier` is supplier discount logic (`1.0` = full price, `0.8` = 20% off, `0.2` = 80% off)

It supports:
- Flat plans (`multiplier`)
- Hour-based plans (`weekday` / `weekend` with `start`, `end`, `multiplier`)
- Optional per-plan `base_rate` override
- Date filtering from a start date
- EV charging what-if (weekday nightly sessions)

Run:

```bash
python supplier_comparison.py
```

## Supplier config (edit at top of `supplier_comparison.py`)

```python
BASE_RATE = 0.6402
CURRENCY_UNIT = "NIS"
ANALYSIS_START_DATE = "2026-01-01"  # None = all data

WORK_DAYS = {'Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday'}
WEEKEND_DAYS = {'Friday', 'Saturday'}

ENABLE_EV_SCENARIO = False
EV_KWH_PER_SESSION = 12.0
EV_CHARGE_HOUR = 2
```

## Plan format example

```python
suppliers = {
    "Supplier Name": {
        "multiplier": 0.94,
        "weekday": [
            {"start": 7, "end": 17, "multiplier": 0.85},
            {"start": 17, "end": 7, "multiplier": 1.0},
        ],
        "weekend": [
            {"multiplier": 1.0}
        ]
    }
}
```

If no hourly period matches, the script falls back to the plan's flat `multiplier` (if present).

## Notes

- Install `colorama` for colored output: `pip install colorama`
- Use real supplier discounts and hour windows before making decisions
