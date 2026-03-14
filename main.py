import csv
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def load_data(csv_file):
    """Load the CSV file and parse dates and times"""
    def normalize_header(value):
        if value is None:
            return ""
        normalized = str(value).strip().replace('"', '').replace("'", '')
        return " ".join(normalized.split()).lower()

    def find_column(columns, required_tokens):
        for col in columns:
            normalized = normalize_header(col)
            if all(token in normalized for token in required_tokens):
                return col
        return None

    with open(csv_file, 'r', encoding='utf-8', newline='') as fh:
        rows = list(csv.reader(fh))

    if not rows:
        return pd.DataFrame(columns=['Date', 'Time', 'Consumption', 'DateTime', 'Hour', 'TimeOfDay', 'DayOfWeek', 'Date_Only'])

    max_cols = max(len(r) for r in rows)
    padded_rows = [r + [''] * (max_cols - len(r)) for r in rows]
    raw = pd.DataFrame(padded_rows)
    raw = raw.apply(lambda col: col.str.strip() if col.dtype == "object" else col)

    header_row_idx = None
    for idx in range(len(raw)):
        row_values = [normalize_header(v) for v in raw.iloc[idx].tolist() if pd.notna(v)]
        if not row_values:
            continue
        has_date = any('date' in v or 'תאריך' in v for v in row_values)
        has_time = any('time' in v or 'מועד תחילת הפעימה' in v for v in row_values)
        has_consumption = any('consumption' in v or 'צריכה' in v for v in row_values)
        if has_date and has_time and has_consumption:
            header_row_idx = idx
            break

    if header_row_idx is not None:
        extracted = raw.iloc[header_row_idx + 1:].copy()
        extracted.columns = raw.iloc[header_row_idx].tolist()

        date_col = find_column(extracted.columns, ['date']) or find_column(extracted.columns, ['תאריך'])
        time_col = find_column(extracted.columns, ['time']) or find_column(extracted.columns, ['מועד', 'תחילת', 'הפעימה'])
        consumption_col = (
            find_column(extracted.columns, ['consumption'])
            or find_column(extracted.columns, ['צריכה', 'ייצור'])
            or find_column(extracted.columns, ['צריכה'])
        )

        if not date_col or not time_col or not consumption_col:
            raise ValueError("Could not detect Date/Time/Consumption columns in meter.csv")

        df = extracted[[date_col, time_col, consumption_col]].copy()
        df.columns = ['Date', 'Time', 'Consumption']
    else:
        # Backward-compatible fallback for simple 3-column exports.
        df = pd.read_csv(csv_file, skiprows=10, quotechar='"').iloc[:, :3].copy()
        df.columns = ['Date', 'Time', 'Consumption']

    df = df[(df['Date'].notna()) & (df['Date'] != '') & (df['Time'].notna()) & (df['Time'] != '')]
    df = df.dropna(subset=['Consumption'])

    df['Consumption'] = pd.to_numeric(df['Consumption'], errors='coerce')
    df = df[df['Consumption'].notna()].copy()

    df['DateTime'] = pd.to_datetime(df['Date'] + ' ' + df['Time'], format='%d/%m/%Y %H:%M', errors='coerce')
    df = df[df['DateTime'].notna()].copy()

    # Extract time of day and day of week
    df['Hour'] = df['DateTime'].dt.hour
    df['TimeOfDay'] = df['DateTime'].dt.strftime('%H:%M')
    df['DayOfWeek'] = df['DateTime'].dt.day_name()
    df['Date_Only'] = df['DateTime'].dt.date

    return df

def analyze_by_time_of_day(df):
    """Analyze average consumption by time of day"""
    print("\n" + "="*60)
    print("ELECTRICITY USAGE BY TIME OF DAY")
    print("="*60)

    time_analysis = df.groupby('TimeOfDay')['Consumption'].agg(['mean', 'sum', 'count']).round(4)
    time_analysis.columns = ['Avg (kWh)', 'Total (kWh)', 'Count']

    print(time_analysis)
    return time_analysis

def analyze_by_day_of_week(df):
    """Analyze average consumption by day of week"""
    print("\n" + "="*60)
    print("ELECTRICITY USAGE BY DAY OF WEEK")
    print("="*60)

    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    day_analysis = df.groupby('DayOfWeek')['Consumption'].agg(['mean', 'sum', 'count']).round(4)
    day_analysis = day_analysis.reindex([d for d in day_order if d in day_analysis.index])
    day_analysis.columns = ['Avg (kWh)', 'Total (kWh)', 'Count']

    print(day_analysis)
    return day_analysis

def analyze_by_time_and_day(df):
    """Analyze consumption by both time of day and day of week"""
    print("\n" + "="*60)
    print("ELECTRICITY USAGE BY TIME OF DAY AND DAY OF WEEK")
    print("="*60)

    pivot_table = df.pivot_table(
        values='Consumption',
        index='TimeOfDay',
        columns='DayOfWeek',
        aggfunc='mean'
    )

    # Reorder columns by day of week
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    pivot_table = pivot_table[[col for col in day_order if col in pivot_table.columns]]

    print(pivot_table.round(4))
    return pivot_table

def identify_peak_hours(df, percentile=75):
    """Identify peak consumption hours"""
    print("\n" + "="*60)
    print(f"PEAK HOURS (Top {100-percentile}% Usage)")
    print("="*60)

    time_avg = df.groupby('TimeOfDay')['Consumption'].mean()
    threshold = time_avg.quantile(percentile/100)
    peak_hours = time_avg[time_avg >= threshold].sort_values(ascending=False)

    print(f"\nThreshold: {threshold:.4f} kWh")
    print(peak_hours.round(4))
    return peak_hours

def generate_summary_statistics(df):
    """Generate overall summary statistics"""
    print("\n" + "="*60)
    print("SUMMARY STATISTICS")
    print("="*60)

    total_consumption = df['Consumption'].sum()
    avg_consumption = df['Consumption'].mean()
    max_consumption = df['Consumption'].max()
    min_consumption = df['Consumption'].min()
    date_range = f"{df['Date_Only'].min()} to {df['Date_Only'].max()}"

    print(f"Date Range: {date_range}")
    print(f"Total Consumption: {total_consumption:.2f} kWh")
    print(f"Average Consumption (per 15-min): {avg_consumption:.4f} kWh")
    print(f"Max Consumption: {max_consumption:.4f} kWh")
    print(f"Min Consumption: {min_consumption:.4f} kWh")
    print(f"Total Records: {len(df)}")

def create_visualizations(df, pivot_table):
    """Create visualizations for the analysis"""
    try:
        # Set style
        sns.set_style("whitegrid")

        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('Electricity Consumption Analysis', fontsize=16, fontweight='bold')

        # 1. Average consumption by hour of day
        hourly_avg = df.groupby('Hour')['Consumption'].mean()
        axes[0, 0].plot(hourly_avg.index, hourly_avg.values, marker='o', linewidth=2, markersize=6)
        axes[0, 0].set_xlabel('Hour of Day')
        axes[0, 0].set_ylabel('Average Consumption (kWh)')
        axes[0, 0].set_title('Average Consumption by Hour')
        axes[0, 0].grid(True, alpha=0.3)

        # 2. Average consumption by day of week
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        daily_avg = df.groupby('DayOfWeek')['Consumption'].mean()
        daily_avg = daily_avg.reindex([d for d in day_order if d in daily_avg.index])
        axes[0, 1].bar(range(len(daily_avg)), daily_avg.values, color='steelblue')
        axes[0, 1].set_xticks(range(len(daily_avg)))
        axes[0, 1].set_xticklabels(daily_avg.index, rotation=45, ha='right')
        axes[0, 1].set_ylabel('Average Consumption (kWh)')
        axes[0, 1].set_title('Average Consumption by Day of Week')
        axes[0, 1].grid(True, alpha=0.3, axis='y')

        # 3. Heatmap of consumption by hour and day
        sns.heatmap(pivot_table.astype(float), annot=False, cmap='YlOrRd', ax=axes[1, 0], cbar_kws={'label': 'Avg Consumption (kWh)'})
        axes[1, 0].set_title('Heatmap: Consumption by Hour and Day of Week')
        axes[1, 0].set_ylabel('Time of Day')
        axes[1, 0].set_xlabel('Day of Week')

        # 4. Total daily consumption
        daily_total = df.groupby('Date_Only')['Consumption'].sum()
        axes[1, 1].plot(range(len(daily_total)), daily_total.values, marker='o', linewidth=2, markersize=4, color='darkgreen')
        axes[1, 1].set_xlabel('Date')
        axes[1, 1].set_ylabel('Total Consumption (kWh)')
        axes[1, 1].set_title('Total Daily Consumption Trend')
        axes[1, 1].grid(True, alpha=0.3)

        # Format x-axis to show fewer labels
        step = max(1, len(daily_total) // 10)
        axes[1, 1].set_xticks(range(0, len(daily_total), step))
        axes[1, 1].set_xticklabels([str(daily_total.index[i]) for i in range(0, len(daily_total), step)], rotation=45, ha='right', fontsize=8)

        plt.tight_layout()
        plt.savefig('electricity_analysis.png', dpi=300, bbox_inches='tight')
        print("\nVisualization saved as 'electricity_analysis.png'")
        plt.show()
    except Exception as e:
        print(f"\nWarning: Could not create visualizations: {e}")

if __name__ == '__main__':
    # Load data
    csv_file = 'meter.csv'

    try:
        df = load_data(csv_file)

        if df.empty:
            print("Error: No valid consumption records were parsed from meter.csv.")
            print("Please verify the CSV format includes Date, Time, and Consumption fields.")
            raise SystemExit(1)

        # Generate summary statistics
        generate_summary_statistics(df)

        # Analyze by time of day
        time_analysis = analyze_by_time_of_day(df)

        # Analyze by day of week
        day_analysis = analyze_by_day_of_week(df)

        # Analyze by both time and day
        pivot_table = analyze_by_time_and_day(df)

        # Identify peak hours
        peak_hours = identify_peak_hours(df, percentile=75)

        # Create visualizations
        create_visualizations(df, pivot_table)

        print("\n" + "="*60)
        print("Analysis complete!")
        print("="*60)

    except FileNotFoundError:
        print(f"Error: Could not find {csv_file}")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
