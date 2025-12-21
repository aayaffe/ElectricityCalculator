# -*- coding: utf-8 -*-
"""
Electricity Supplier Comparison Tool

This script helps compare different electricity supplier plans based on your consumption patterns.
"""

import sys
import os

# Force UTF-8 encoding on Windows
if sys.platform == 'win32':
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    # Use UTF-8 for stdout
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

import pandas as pd
from main import load_data

# Try to import colorama for colored output
try:
    from colorama import Fore, Style, Back, init
    init(autoreset=True, convert=True)
    HAS_COLOR = True
except ImportError:
    # Fallback if colorama not installed
    class Fore:
        RED = GREEN = YELLOW = BLUE = CYAN = MAGENTA = WHITE = RESET = ''
    class Style:
        BRIGHT = DIM = NORMAL = RESET_ALL = ''
    class Back:
        BLACK = RED = GREEN = YELLOW = BLUE = MAGENTA = CYAN = WHITE = RESET = ''
    HAS_COLOR = False

# Icons (Unicode symbols)
ICON_BEST = "★★★"
ICON_MONEY = "₪"
ICON_UP = "↑"
ICON_DOWN = "↓"
ICON_LIGHTNING = "⚡"
ICON_CLOCK = "🕐"
ICON_CALENDAR = "📅"
ICON_CHECK = "✓"
ICON_INFO = "ℹ"
ICON_WARNING = "⚠"
ICON_CAR = "🚗"

# Configuration
BASE_RATE = 0.5425  # price per kWh before discounts; change to your actual base price
CURRENCY_UNIT = "NIS"  # e.g., "NIS", "USD", "EUR"

# Define work days and weekends (Israel: Sunday-Thursday work, Friday-Saturday weekend)
WORK_DAYS = {'Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday'}
WEEKEND_DAYS = {'Friday', 'Saturday'}


def _get_multiplier_for_hour(plan: dict, day: str, hour: int):
    """Return price multiplier (1.0 = full price, 0.2 = pay 20% of base)."""
    weekend_days = WEEKEND_DAYS
    day_key = 'weekend' if day in weekend_days and 'weekend' in plan else 'weekday'
    periods = plan.get(day_key, [])

    for period in periods:
        start = period.get('start')
        end = period.get('end')
        multiplier = period.get('multiplier')
        # Allow all-day entries with only multiplier
        if start is None and end is None and multiplier is not None:
            return multiplier
        if start is None or end is None or multiplier is None:
            continue
        # Handle wrap-around ranges (e.g., 22 -> 7)
        if start <= end:
            if start <= hour < end:
                return multiplier
        else:
            if hour >= start or hour < end:
                return multiplier

    # Fallback to flat multiplier if provided
    return plan.get('multiplier')


def calculate_cost_for_plan(df, plan_name, plan):
    """
    Calculate total cost using per-hour multipliers.

    Plan structure example:
    {
        # Optional override; if missing, BASE_RATE is used
        # 'base_rate': 0.52,
        'weekday': [
            {'start': 7, 'end': 22, 'multiplier': 1.0},   # pay 100% of base
            {'start': 22, 'end': 7, 'multiplier': 0.8},   # pay 80% of base (20% off)
        ],
        'weekend': [
            {'start': 8, 'end': 23, 'multiplier': 0.7},
            {'start': 23, 'end': 8, 'multiplier': 0.6},
        ],
        # Optional flat fallback if no period matches:
        # 'multiplier': 1.0
    }
    """
    base_rate = plan.get('base_rate', BASE_RATE)

    cost = 0

    for _, row in df.iterrows():
        hour = row['Hour']
        day = row['DayOfWeek']
        consumption = row['Consumption']

        multiplier = _get_multiplier_for_hour(plan, day, hour)
        if multiplier is None:
            raise ValueError(f"No multiplier found for {plan_name} on {day} at hour {hour}")

        effective_rate = base_rate * multiplier
        cost += consumption * effective_rate

    return cost

def print_supplier_comparison(df, suppliers):
    """
    Print comparison of different electricity suppliers.

    Parameters:
    -----------
    df : DataFrame
        The loaded electricity data
    suppliers : dict
        Dictionary of supplier plans. Example:
        {
            'Supplier A': {
                'weekday': {'peak': 0.50, 'off_peak': 0.25},
                'weekend': {'peak': 0.40, 'off_peak': 0.20}
            },
            'Supplier B': {
                'weekday': {'peak': 0.48, 'off_peak': 0.30},
                'weekend': {'peak': 0.45, 'off_peak': 0.25}
            }
        }
    """
    print(f"\n{Fore.CYAN}{Style.BRIGHT}{'='*80}")
    print(f"{ICON_LIGHTNING}  ELECTRICITY SUPPLIER COMPARISON  {ICON_LIGHTNING}")
    print(f"{'='*80}{Style.RESET_ALL}")

    results = {}
    for supplier_name, plan in suppliers.items():
        cost = calculate_cost_for_plan(df, supplier_name, plan)
        results[supplier_name] = cost

    # Sort by cost
    sorted_results = sorted(results.items(), key=lambda x: x[1])

    print(f"\n{Fore.WHITE}{Style.DIM}Based on {len(df):,} consumption records{Style.RESET_ALL}\n")

    for i, (supplier, cost) in enumerate(sorted_results, 1):
        saving = results[sorted_results[0][0]] if i > 1 else 0
        saving_pct = ((cost - sorted_results[0][1]) / sorted_results[0][1] * 100) if i > 1 else 0

        if i == 1:
            # Best option - green and bright
            icon = ICON_BEST
            color = Fore.GREEN + Style.BRIGHT
            status = f"{Fore.GREEN}{Style.BRIGHT}★ BEST DEAL ★{Style.RESET_ALL}"
        elif saving_pct < 5:
            # Close competitor - yellow
            icon = ICON_CHECK
            color = Fore.YELLOW
            status = f"{Fore.YELLOW}+{saving_pct:.1f}%{Style.RESET_ALL}"
        else:
            # More expensive - red
            icon = ICON_UP
            color = Fore.RED
            status = f"{Fore.RED}+{saving_pct:.1f}%{Style.RESET_ALL}"

        print(f"{color}{i}. {icon:8s} {supplier:40s} {cost:10.2f} {ICON_MONEY}  {status}{Style.RESET_ALL}")

    print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}")

def analyze_consumption_by_period(df):
    """
    Analyze consumption by time period for better supplier selection.
    """
    print(f"\n{Fore.MAGENTA}{Style.BRIGHT}{'='*80}")
    print(f"{ICON_CLOCK} CONSUMPTION ANALYSIS BY PERIOD {ICON_CALENDAR}")
    print(f"{'='*80}{Style.RESET_ALL}")

    weekday_peak = df[(df['DayOfWeek'].isin(WORK_DAYS)) &
                      (df['Hour'] >= 7) & (df['Hour'] < 17)]
    print(f"\n{Fore.BLUE}{Style.BRIGHT}{ICON_LIGHTNING} Work Days Peak Hours (7:00-17:00, {', '.join(sorted(WORK_DAYS))}){Style.RESET_ALL}")
    print(f"  {Fore.CYAN}Total: {weekday_peak['Consumption'].sum():.2f} kWh ({weekday_peak['Consumption'].sum() / df['Consumption'].sum() * 100:.1f}%){Style.RESET_ALL}")

    weekday_offpeak = df[(df['DayOfWeek'].isin(WORK_DAYS)) &
                         ((df['Hour'] >= 23) | (df['Hour'] < 7))]
    print(f"\n{Fore.GREEN}{Style.BRIGHT}{ICON_DOWN} Work Days Off-Peak Hours (23:00-7:00, {', '.join(sorted(WORK_DAYS))}){Style.RESET_ALL}")
    print(f"  {Fore.CYAN}Total: {weekday_offpeak['Consumption'].sum():.2f} kWh ({weekday_offpeak['Consumption'].sum() / df['Consumption'].sum() * 100:.1f}%){Style.RESET_ALL}")

    weekday_evening = df[(df['DayOfWeek'].isin(WORK_DAYS)) &
                         ((df['Hour'] >= 14) & (df['Hour'] < 20))]
    print(f"\n{Fore.YELLOW}{Style.BRIGHT}{ICON_LIGHTNING} Work Days Evening Hours (14:00-20:00, {', '.join(sorted(WORK_DAYS))}){Style.RESET_ALL}")
    print(f"  {Fore.CYAN}Total: {weekday_evening['Consumption'].sum():.2f} kWh ({weekday_evening['Consumption'].sum() / df['Consumption'].sum() * 100:.1f}%){Style.RESET_ALL}")

    weekend_total = df[(df['DayOfWeek'].isin(WEEKEND_DAYS))]
    print(f"\n{Fore.MAGENTA}{Style.BRIGHT}{ICON_CALENDAR} Weekend Total ({', '.join(sorted(WEEKEND_DAYS))}){Style.RESET_ALL}")
    print(f"  {Fore.CYAN}Total: {weekend_total['Consumption'].sum():.2f} kWh ({weekend_total['Consumption'].sum()/df['Consumption'].sum()*100:.1f}%){Style.RESET_ALL}")

    print(f"\n{Fore.MAGENTA}{'='*80}{Style.RESET_ALL}")

def apply_ev_scenario(df, kwh_per_session=14.0, charge_hour=2, weekdays_only=True):
    """Return a new DataFrame with extra EV charging sessions added.
    Adds one session per date (weekday-only by default) at the specified hour."""
    dates = df['Date_Only'].unique()
    new_rows = []
    for d in dates:
        weekday_name = pd.to_datetime(d).day_name()
        if weekdays_only and weekday_name in WEEKEND_DAYS:
            continue
        dt = pd.to_datetime(f"{d} {charge_hour:02d}:00")
        new_rows.append({
            'Date': dt.strftime('%d/%m/%Y'),
            'Time': dt.strftime('%H:%M'),
            'Consumption': kwh_per_session,
            'DateTime': dt,
            'Hour': charge_hour,
            'TimeOfDay': dt.strftime('%H:%M'),
            'DayOfWeek': weekday_name,
            'Date_Only': dt.date()
        })
    if not new_rows:
        return df
    return pd.concat([df, pd.DataFrame(new_rows)], ignore_index=True)

if __name__ == '__main__':
    # Load data
    csv_file = 'meter.csv'
    df = load_data(csv_file)

    # What-if: enable EV charging scenario (one nightly weekday session, 14 kWh)
    ENABLE_EV_SCENARIO = True
    EV_KWH_PER_SESSION = 12.0
    EV_CHARGE_HOUR = 2  # 2:00 AM


    # Example supplier plans (REPLACE MULTIPLIERS WITH ACTUAL DISCOUNTS)
    # Multipliers: 1.0 = full price, 0.2 = pay 20% of base price (80% off).
    suppliers = {
        'Cellcom - Daily (Up to 299 NIS consumption)': {
            'multiplier': 0.94
        },
        'Cellcom - Day workers (15%)': {
            'weekday': [
                {'start': 7, 'end': 17, 'multiplier': 0.85},
                {'start': 17, 'end': 7, 'multiplier': 1.0},
            ],
            'weekend': [
                {'multiplier': 1.0},
            ],
        },
        'Cellcom - Evenings (18%)': {
            'weekday': [
                {'start': 14, 'end': 20, 'multiplier': 0.82},
                {'start': 20, 'end': 14, 'multiplier': 1.0},
            ],
            'weekend': [
                {'multiplier': 1.0},
            ],
        },
        'Cellcom - Night (20%)': {
            'weekday': [
                {'start': 23, 'end': 7, 'multiplier': 0.8},
                {'start': 7, 'end': 23, 'multiplier': 1.0},
            ],
            'weekend': [
                {'multiplier': 1.0},
            ],
        },
        'SuperPower - Daily (6.5%)': {
            'multiplier': 0.935
        },
        'SuperPower - Day (16%)': {
            'weekday': [
                {'start': 7, 'end': 17, 'multiplier': 0.84},
                {'start': 17, 'end': 7, 'multiplier': 1.0},
            ],
            'weekend': [
                {'multiplier': 1.0},
            ],
        },
        'SuperPower - Night (21%)': {
            'weekday': [
                {'start': 23, 'end': 7, 'multiplier': 0.79},
                {'start': 7, 'end': 23, 'multiplier': 1.0},
            ],
            'weekend': [
                {'multiplier': 1.0},
            ],
        },
        'Original - IEC': {
            'multiplier': 1.0,
        },
    }

    # Analyze consumption by period
    analyze_consumption_by_period(df)

    # Baseline comparison
    print_supplier_comparison(df, suppliers)

    # EV scenario comparison
    if ENABLE_EV_SCENARIO:
        df_ev = apply_ev_scenario(df, kwh_per_session=EV_KWH_PER_SESSION, charge_hour=EV_CHARGE_HOUR, weekdays_only=True)
        print(f"\n{Fore.CYAN}{Style.BRIGHT}{'='*80}")
        print(f"{ICON_CAR} EV SCENARIO: Weekday nightly charging added ({EV_KWH_PER_SESSION} kWh at {EV_CHARGE_HOUR:02d}:00)")
        print(f"{'='*80}{Style.RESET_ALL}")

        # Show before/after comparison
        results_baseline = {}
        results_ev = {}
        for supplier_name, plan in suppliers.items():
            results_baseline[supplier_name] = calculate_cost_for_plan(df, supplier_name, plan)
            results_ev[supplier_name] = calculate_cost_for_plan(df_ev, supplier_name, plan)

        print_supplier_comparison(df_ev, suppliers)

        # Show savings summary
        print(f"\n{Fore.YELLOW}{Style.BRIGHT}{'='*80}")
        print(f"{ICON_INFO} EV CHARGING IMPACT SUMMARY")
        print(f"{'='*80}{Style.RESET_ALL}")

        sorted_baseline = sorted(results_baseline.items(), key=lambda x: x[1])
        sorted_ev = sorted(results_ev.items(), key=lambda x: x[1])

        best_baseline = sorted_baseline[0]
        best_ev = sorted_ev[0]

        print(f"\n{Fore.WHITE}Without EV:{Style.RESET_ALL}")
        print(f"  {Fore.GREEN}Best: {best_baseline[0]}{Style.RESET_ALL}")
        print(f"  Cost: {Fore.CYAN}{best_baseline[1]:.2f} {CURRENCY_UNIT}{Style.RESET_ALL}")

        print(f"\n{Fore.WHITE}With EV Charging:{Style.RESET_ALL}")
        print(f"  {Fore.GREEN}Best: {best_ev[0]}{Style.RESET_ALL}")
        print(f"  Cost: {Fore.CYAN}{best_ev[1]:.2f} {CURRENCY_UNIT}{Style.RESET_ALL}")

        ev_added_cost = best_ev[1] - best_baseline[1]
        ev_kwh_total = EV_KWH_PER_SESSION * len([d for d in df['Date_Only'].unique() if pd.to_datetime(d).day_name() in WORK_DAYS])
        cost_per_kwh_ev = ev_added_cost / ev_kwh_total if ev_kwh_total > 0 else 0

        print(f"\n{Fore.YELLOW}EV Charging Analysis:{Style.RESET_ALL}")
        print(f"  Additional annual cost: {Fore.RED}+{ev_added_cost:.2f} {CURRENCY_UNIT}{Style.RESET_ALL}")
        print(f"  Total EV consumption: {Fore.CYAN}{ev_kwh_total:.2f} kWh{Style.RESET_ALL}")
        print(f"  Effective rate: {Fore.CYAN}{cost_per_kwh_ev:.4f} {CURRENCY_UNIT}/kWh{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}{'='*80}{Style.RESET_ALL}")

    print(f"\n{Fore.YELLOW}{Style.BRIGHT}{ICON_WARNING} IMPORTANT:{Style.RESET_ALL}")
    print(f"{Fore.WHITE}Set BASE_RATE (top of file), CURRENCY_UNIT, and update per-hour 'multiplier' values")
    print(f"with the actual discounts from your electricity suppliers!{Style.RESET_ALL}")

    if not HAS_COLOR:
        print(f"\n{ICON_INFO} TIP: Install 'colorama' for colored output: pip install colorama")
