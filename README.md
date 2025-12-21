# Electricity Usage Analyzer

A Python program to analyze electricity consumption patterns by time of day and day of the week. This tool helps you understand your electricity usage to select the best electricity supplier based on their time-of-use and day-of-week discounts.

## Features

- **Time-of-Day Analysis**: See your average consumption for each 15-minute interval throughout the day
- **Day-of-Week Analysis**: Compare consumption patterns across different days of the week
- **Combined Analysis**: View consumption patterns broken down by both time and day
- **Peak Hour Identification**: Automatically identify when you consume the most electricity
- **Summary Statistics**: Get overall consumption metrics including total, average, min, and max
- **Visual Representation**: Generate comprehensive charts and heatmaps to visualize patterns

## Output

The program generates:
1. **Console Output**: Detailed tables and statistics printed to the terminal
2. **Visualization**: `electricity_analysis.png` containing:
   - Line chart of average consumption by hour
   - Bar chart of consumption by day of week
   - Heatmap of consumption by hour and day of week
   - Trend chart of daily total consumption

## Supplier Comparison Tool

### Overview
The `supplier_comparison.py` script helps you find the best electricity supplier based on your actual consumption patterns and their pricing structures.

### How It Works

1. **Load Your Data**: Reads your electricity meter data
2. **Analyze Consumption Periods**: Breaks down your usage by:
   - Work days vs. weekends (configurable - defaults to Israeli calendar: Sunday-Thursday work, Friday-Saturday weekend)
   - Peak hours vs. off-peak hours
   - Evening hours
3. **Compare Plans**: Calculates your annual cost with each supplier plan
4. **What-If Analysis**: Shows how adding an EV charging scenario would change your costs

### Features

- **Time-of-Use Pricing**: Supports different rates for different times of day (e.g., 7am-5pm, 5pm-11pm, 11pm-7am)
- **Weekday/Weekend Rates**: Different pricing for work days and weekends
- **Flat Rate Plans**: Support for suppliers with uniform pricing
- **EV Charging Scenarios**: See how adding electric vehicle charging (If you don't already have one) at specific times affects your total cost
- **Cost Per kWh Analysis**: Get the effective rate you'd pay for EV charging

### Usage

```bash
python supplier_comparison.py
```

### Configuration

At the top of `supplier_comparison.py`, modify these settings:

```python
BASE_RATE = 0.50              # Base price per kWh before discounts
CURRENCY_UNIT = "NIS"          # Your currency (NIS, USD, EUR, etc.)

ENABLE_EV_SCENARIO = True      # Enable/disable electric car scenario
EV_KWH_PER_SESSION = 12.0      # kWh per charging session
EV_CHARGE_HOUR = 2             # Hour of day to charge (24-hour format)
```

### Adding Suppliers

Define suppliers in the `suppliers` dictionary with their pricing structure:

```python
suppliers = {
    'Supplier Name': {
        'multiplier': 0.94,  # For flat rates: 0.94 = 6% discount on base
        
        # For time-of-use rates:
        'weekday': [
            {'start': 7, 'end': 17, 'multiplier': 0.85},   # 7am-5pm: 15% off
            {'start': 17, 'end': 7, 'multiplier': 1.0},    # 5pm-7am: full price
        ],
        'weekend': [
            {'multiplier': 1.0},  # Full price all day
        ],
    }
}
```

**Multiplier Explanation:**
- `1.0` = full price (no discount)
- `0.94` = pay 94% of base (6% discount)
- `0.85` = pay 85% of base (15% discount)
- `0.5` = pay 50% of base (50% discount)

### Example Output

```
⚡ CONSUMPTION ANALYSIS BY PERIOD ⚡
================================================

🕐 Work Days Peak Hours (7:00-17:00, Sunday, Monday, Tuesday, Wednesday, Thursday)
  Total: 1717.27 kWh (36.5%)

↓ Work Days Off-Peak Hours (23:00-7:00, ...)
  Total: 606.38 kWh (12.9%)

⚡ Work Days Evening Hours (14:00-20:00, ...)
  Total: 1092.17 kWh (23.2%)

📅 Weekend Total (Friday, Saturday)
  Total: 1349.79 kWh (28.7%)

================================================
⚡ ELECTRICITY SUPPLIER COMPARISON ⚡
================================================

1. ★★★ SuperPower - Daily (6.5%)     ₪ 2388.05 NIS  ★ BEST DEAL ★
2. ✓ Cellcom - Daily (Up to 299)      ₪ 2400.83 NIS  +0.5%
3. ✓ SuperPower - Day (16%)           ₪ 2405.01 NIS  +0.7%
4. ↑ Cellcom - Night (20%)            ₪ 2488.28 NIS  +4.2%

================================================
🚗 EV SCENARIO: Weekday nightly charging (12.0 kWh at 02:00)
================================================

With EV Charging Analysis:
  Additional annual cost: +1439.23 NIS
  Total EV consumption: 3132.00 kWh
  Effective rate: 0.4595 NIS/kWh
```

### Tips for Configuration

1. **Get Real Rates**: Contact your local electricity suppliers for their current rates and time periods
2. **Match Your Schedule**: Adjust work days/weekends if different from Israeli calendar
3. **Test Scenarios**: Try different EV charging hours to find the cheapest option
4. **Compare Multiple Plans**: Add all available plans to find the best match for your usage pattern

## Usage

### Requirements

Install the required Python packages:
```bash
pip install -r requirements.txt
```

### Running the Program

```bash
python main.py
```

The program expects a CSV file named `meter.csv` in the same directory.

## CSV File Format

The input CSV file should contain electricity meter data with the following structure:
- **Date Column**: Date in DD/MM/YYYY format
- **Time Column**: Time in HH:MM format (15-minute intervals)
- **Consumption Column**: Consumption in kWh

Example:
```
11/12/2024,00:00,.027
11/12/2024,00:15,.023
11/12/2024,00:30,.040
```

## Key Insights

The program provides insights to help you:

1. **Identify Peak Usage Hours**: See when you consume the most electricity and plan accordingly
2. **Understand Day-of-Week Patterns**: Identify which days have higher or lower consumption
3. **Optimize Supplier Selection**: Use the data to compare discounts from different suppliers:
   - Some suppliers offer off-peak discounts (typically night hours)
   - Others offer weekend discounts
   - Some have time-of-use pricing with multiple tiers

## Example Output

```
============================================================
SUMMARY STATISTICS
============================================================
Date Range: 2024-12-11 to 2025-12-10
Total Consumption: 4707.96 kWh
Average Consumption (per 15-min): 0.1345 kWh
Max Consumption: 1.9310 kWh
Min Consumption: 0.0000 kWh
Total Records: 35008

============================================================
PEAK HOURS (Top 25% Usage)
============================================================
TimeOfDay
07:30    0.2270    <- Morning peak
07:15    0.2210
07:45    0.2191
...
19:15    0.2096    <- Evening peak
19:30    0.2090
19:00    0.2024
```

## Functions

### `load_data(csv_file)`
Loads and parses the CSV file, extracts date/time components, and prepares the data for analysis.

### `analyze_by_time_of_day(df)`
Calculates average, total, and count of consumption for each 15-minute time slot.

### `analyze_by_day_of_week(df)`
Calculates average, total, and count of consumption for each day of the week.

### `analyze_by_time_and_day(df)`
Creates a pivot table showing consumption patterns by both time and day.

### `identify_peak_hours(df, percentile=75)`
Identifies the top 25% consumption hours (by default) and their consumption values.

### `generate_summary_statistics(df)`
Prints overall statistics about the dataset.

### `create_visualizations(df, pivot_table)`
Generates and saves the visualization plots to `electricity_analysis.png`.

## Tips for Electricity Supplier Selection

Based on your analysis data:

1. **For Off-Peak Discounts**: Look at the percentage of consumption during night hours (e.g., 22:00-06:00)
2. **For Peak Hour Surcharges**: Note the hours with highest consumption that might have surcharges
3. **For Weekend Rates**: Compare weekend vs. weekday consumption to assess weekend discounts
4. **For Time-of-Use Plans**: Match supplier tiers to your consumption patterns

## Author

Created for analyzing personal electricity consumption data to optimize supplier selection.
