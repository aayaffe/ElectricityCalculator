"""
Advanced Electricity Analysis

Additional utilities for deeper analysis of electricity consumption patterns.
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from main import load_data

def monthly_analysis(df):
    """Analyze consumption by month"""
    print("\n" + "="*80)
    print("MONTHLY CONSUMPTION ANALYSIS")
    print("="*80)

    df['Month'] = df['DateTime'].dt.to_period('M')

    monthly = df.groupby('Month')['Consumption'].agg(['sum', 'mean', 'max']).round(2)
    monthly.columns = ['Total (kWh)', 'Daily Avg (kWh)', 'Peak (kWh)']

    print(monthly)

    return monthly

def weekly_pattern_analysis(df):
    """Identify weekly patterns"""
    print("\n" + "="*80)
    print("WEEKLY PATTERN ANALYSIS")
    print("="*80)

    # Group by week
    df['Week'] = df['DateTime'].dt.to_period('W')
    weekly = df.groupby('Week')['Consumption'].sum()

    avg_weekly = weekly.mean()
    min_weekly = weekly.min()
    max_weekly = weekly.max()
    variance = weekly.std()

    print(f"Average Weekly Consumption: {avg_weekly:.2f} kWh")
    print(f"Min Weekly Consumption: {min_weekly:.2f} kWh")
    print(f"Max Weekly Consumption: {max_weekly:.2f} kWh")
    print(f"Standard Deviation: {variance:.2f} kWh")
    print(f"Variance Range: {((max_weekly - min_weekly) / avg_weekly * 100):.1f}%")

    return weekly

def hourly_savings_analysis(df, off_peak_rate, peak_rate):
    """Calculate potential savings for each hour"""
    print("\n" + "="*80)
    print("HOURLY SAVINGS ANALYSIS")
    print("="*80)

    hourly = df.groupby('Hour')['Consumption'].mean()

    print(f"\nAssuming:")
    print(f"  Peak Rate: {peak_rate} $/kWh")
    print(f"  Off-Peak Rate: {off_peak_rate} $/kWh")
    print(f"  Savings per kWh: {peak_rate - off_peak_rate:.4f} $/kWh\n")

    hourly_savings = []
    for hour, consumption in hourly.items():
        # Assume 365 days per year, 4 readings per hour
        annual_consumption = consumption * 365 * 4
        peak_cost = annual_consumption * peak_rate
        offpeak_cost = annual_consumption * off_peak_rate
        savings = peak_cost - offpeak_cost

        hourly_savings.append({
            'Hour': f"{hour:02d}:00",
            'Avg Consumption (kWh)': consumption,
            'Annual Usage (kWh)': annual_consumption,
            'Cost at Peak': peak_cost,
            'Cost at Off-Peak': offpeak_cost,
            'Potential Saving': savings
        })

    result_df = pd.DataFrame(hourly_savings)
    result_df = result_df.sort_values('Potential Saving', ascending=False)

    print(result_df[['Hour', 'Potential Saving']].to_string(index=False))

    total_potential = result_df['Potential Saving'].sum()
    print(f"\nTotal Potential Annual Saving: ${total_potential:.2f}")

    return result_df

def identify_anomalies(df, threshold_percentile=95):
    """Identify unusual consumption patterns"""
    print("\n" + "="*80)
    print(f"ANOMALY DETECTION (Top {100-threshold_percentile}% of consumption)")
    print("="*80)

    threshold = df['Consumption'].quantile(threshold_percentile / 100)
    anomalies = df[df['Consumption'] > threshold].sort_values('Consumption', ascending=False)

    print(f"\nThreshold: {threshold:.4f} kWh")
    print(f"Anomalies Found: {len(anomalies)}")

    if len(anomalies) > 0:
        print("\nTop 20 Anomalies:")
        for idx, (_, row) in enumerate(anomalies.head(20).iterrows(), 1):
            print(f"{idx:2d}. {row['DateTime']}: {row['Consumption']:.4f} kWh ({row['DayOfWeek']})")

    return anomalies

def daily_profile_analysis(df):
    """Analyze daily consumption profile"""
    print("\n" + "="*80)
    print("DAILY PROFILE ANALYSIS")
    print("="*80)

    daily = df.groupby('Date_Only')['Consumption'].sum()

    print(f"Average Daily Consumption: {daily.mean():.2f} kWh")
    print(f"Min Daily Consumption: {daily.min():.2f} kWh ({daily.idxmin()})")
    print(f"Max Daily Consumption: {daily.max():.2f} kWh ({daily.idxmax()})")
    print(f"Std Deviation: {daily.std():.2f} kWh")

    # Categorize days
    low = daily[daily < daily.quantile(0.25)].count()
    normal = daily[(daily >= daily.quantile(0.25)) & (daily <= daily.quantile(0.75))].count()
    high = daily[daily > daily.quantile(0.75)].count()

    print(f"\nDay Categories:")
    print(f"  Low Usage Days: {low} days ({low/len(daily)*100:.1f}%)")
    print(f"  Normal Usage Days: {normal} days ({normal/len(daily)*100:.1f}%)")
    print(f"  High Usage Days: {high} days ({high/len(daily)*100:.1f}%)")

    return daily

def load_shifting_potential(df):
    """Calculate potential savings from load shifting"""
    print("\n" + "="*80)
    print("LOAD SHIFTING POTENTIAL")
    print("="*80)

    # Identify what could be shifted
    appliances = {
        'Water Heating': 0.10,  # Assume 10% of consumption is water heating
        'Space Heating/Cooling': 0.35,  # Assume 35% is HVAC
        'Lighting': 0.15,  # Assume 15% is lighting
        'Refrigeration': 0.20,  # Assume 20% is always on
        'Other': 0.20  # Assume 20% is other
    }

    print("\nShiftable Load Analysis (estimates):")
    print("\nAssuming these loads could be shifted to off-peak:\n")

    total_consumption = df['Consumption'].sum()

    for appliance, percentage in appliances.items():
        if appliance != 'Refrigeration':  # Can't shift this
            shiftable = total_consumption * percentage
            print(f"{appliance:30s}: {shiftable:8.2f} kWh ({percentage*100:5.1f}%) - Shiftable: {'Yes' if appliance != 'Refrigeration' else 'No'}")

    shiftable_total = total_consumption * 0.50  # About 50% can be shifted
    print(f"\n{'Estimated Shiftable Load':30s}: {shiftable_total:8.2f} kWh ({50}%)")

    print("\nWith 30% cheaper off-peak rates:")
    savings_percent = 0.50 * 0.30
    estimated_annual_savings = total_consumption * savings_percent * 1.0  # Rough estimate
    print(f"Potential Annual Saving: ~{estimated_annual_savings:.2f} currency units")

def create_comparison_charts(df, monthly_data):
    """Create comparison charts"""
    try:
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('Advanced Electricity Analysis', fontsize=16, fontweight='bold')

        # 1. Monthly trend
        axes[0, 0].bar(range(len(monthly_data)), monthly_data['Total (kWh)'].values, color='steelblue')
        axes[0, 0].set_xlabel('Month')
        axes[0, 0].set_ylabel('Total Consumption (kWh)')
        axes[0, 0].set_title('Monthly Consumption Trend')
        axes[0, 0].set_xticks(range(len(monthly_data)))
        axes[0, 0].set_xticklabels([str(m) for m in monthly_data.index], rotation=45, ha='right')
        axes[0, 0].grid(True, alpha=0.3, axis='y')

        # 2. Daily distribution
        daily_consumption = df.groupby('Date_Only')['Consumption'].sum()
        axes[0, 1].hist(daily_consumption, bins=30, color='darkgreen', alpha=0.7, edgecolor='black')
        axes[0, 1].axvline(daily_consumption.mean(), color='red', linestyle='--', linewidth=2, label=f"Mean: {daily_consumption.mean():.2f}")
        axes[0, 1].set_xlabel('Daily Consumption (kWh)')
        axes[0, 1].set_ylabel('Frequency')
        axes[0, 1].set_title('Distribution of Daily Consumption')
        axes[0, 1].legend()
        axes[0, 1].grid(True, alpha=0.3, axis='y')

        # 3. Hourly consumption distribution
        hourly_consumption = df.groupby('Hour')['Consumption'].sum()
        axes[1, 0].bar(hourly_consumption.index, hourly_consumption.values, color='orange')
        axes[1, 0].set_xlabel('Hour of Day')
        axes[1, 0].set_ylabel('Total Consumption (kWh)')
        axes[1, 0].set_title('Hourly Consumption Distribution')
        axes[1, 0].grid(True, alpha=0.3, axis='y')

        # 4. Day of week consumption
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        daily_avg = df.groupby('DayOfWeek')['Consumption'].sum()
        daily_avg = daily_avg.reindex([d for d in day_order if d in daily_avg.index])
        axes[1, 1].bar(range(len(daily_avg)), daily_avg.values, color='purple')
        axes[1, 1].set_xticks(range(len(daily_avg)))
        axes[1, 1].set_xticklabels(daily_avg.index, rotation=45, ha='right')
        axes[1, 1].set_ylabel('Total Consumption (kWh)')
        axes[1, 1].set_title('Daily Total by Day of Week')
        axes[1, 1].grid(True, alpha=0.3, axis='y')

        plt.tight_layout()
        plt.savefig('advanced_analysis.png', dpi=300, bbox_inches='tight')
        print("\nAdvanced analysis visualization saved as 'advanced_analysis.png'")

    except Exception as e:
        print(f"\nWarning: Could not create advanced visualizations: {e}")

if __name__ == '__main__':
    csv_file = 'meter.csv'

    try:
        df = load_data(csv_file)

        # Monthly analysis
        monthly = monthly_analysis(df)

        # Weekly pattern
        weekly = weekly_pattern_analysis(df)

        # Daily profile
        daily = daily_profile_analysis(df)

        # Identify anomalies
        anomalies = identify_anomalies(df)

        # Load shifting potential
        load_shifting_potential(df)

        # Hourly savings analysis (example with 0.50 peak and 0.25 off-peak)
        hourly_savings = hourly_savings_analysis(df, off_peak_rate=0.25, peak_rate=0.50)

        # Create visualizations
        create_comparison_charts(df, monthly)

        print("\n" + "="*80)
        print("Advanced analysis complete!")
        print("="*80)

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

