import pandas as pd
import numpy as np
import argparse
from app.services.rul_engine import (
    MIN_HISTORY_FOR_PER_ASSET_FIT,
    SHORT_WINDOW,
    LONG_WINDOW,
    BLEND_SHORT_WEIGHT,
    BLEND_LONG_WEIGHT,
    FLAT_SLOPE_GUARD,
    SOH_EOL_THRESHOLD,
    RUL_CAP
)
from app.services.degradation_service import median_pairwise_slope

def run_backtest(csv_path: str):
    df = pd.read_csv(csv_path)
    
    errors = []
    
    for batt_id, group in df.groupby("battery_id"):
        group = group.sort_values("cycle").reset_index(drop=True)
        n = len(group)
        if n < 30:
            continue
            
        cycles = group["cycle"].tolist()
        soh = group["soh"].tolist()
        
        for i in range(MIN_HISTORY_FOR_PER_ASSET_FIT - 1, n):
            current_cycle = cycles[i]
            current_soh = soh[i]
            
            # Find EOL point after index i
            actual_eol_cycle = None
            for j in range(i + 1, n):
                if soh[j] <= SOH_EOL_THRESHOLD:
                    actual_eol_cycle = cycles[j]
                    break
                    
            if actual_eol_cycle is None:
                continue # Censored
                
            actual_rul = actual_eol_cycle - current_cycle
            
            hist_cycles = cycles[:i+1]
            hist_soh = soh[:i+1]
            
            short_c = hist_cycles[-SHORT_WINDOW:]
            short_s = hist_soh[-SHORT_WINDOW:]
            long_c = hist_cycles[-LONG_WINDOW:] if len(hist_cycles) >= LONG_WINDOW else hist_cycles
            long_s = hist_soh[-LONG_WINDOW:] if len(hist_soh) >= LONG_WINDOW else hist_soh
            
            slope_short = median_pairwise_slope(short_c, short_s)
            slope_long = median_pairwise_slope(long_c, long_s)
            slope_blend = BLEND_SHORT_WEIGHT * slope_short + BLEND_LONG_WEIGHT * slope_long
            
            if slope_blend >= FLAT_SLOPE_GUARD:
                pred_rul = float(RUL_CAP)
            else:
                pred_rul = (SOH_EOL_THRESHOLD - current_soh) / slope_blend
                pred_rul = max(0.0, min(pred_rul, float(RUL_CAP)))
                
            error = pred_rul - actual_rul
            errors.append(error)
            
    if not errors:
        print("No valid uncensored points found for backtesting.")
        return
        
    abs_errors = np.abs(errors)
    mae = np.mean(abs_errors)
    rmse = np.sqrt(np.mean(np.square(errors)))
    median_error = np.median(errors)
    within_20 = np.sum(abs_errors <= 20) / len(errors) * 100
    
    print(f"{'Metric':<30} | {'Value'}")
    print("-" * 45)
    print(f"{'n (count of scored points)':<30} | {len(errors)}")
    print(f"{'MAE (cycles)':<30} | {mae:.2f}")
    print(f"{'RMSE (cycles)':<30} | {rmse:.2f}")
    print(f"{'Median Error (cycles)':<30} | {median_error:.2f}")
    print(f"{'% within 20 cycles':<30} | {within_20:.1f}%")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", default="scripts/synthetic_battery_dataset.csv", help="Path to CSV dataset")
    args = parser.parse_args()
    run_backtest(args.csv)
