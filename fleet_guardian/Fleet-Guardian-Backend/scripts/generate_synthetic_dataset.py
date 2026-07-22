import pandas as pd
import numpy as np
import random
import os

RANDOM_SEED = 42

def generate_synthetic_data():
    np.random.seed(RANDOM_SEED)
    random.seed(RANDOM_SEED)

    battery_ids = [f"SYN{i:04d}" for i in range(1, 21)]
    
    # Bucket allocation
    # 6 < 10 cycles, 10 >= 30 cycles, 4 in between (10-29)
    cycle_counts = []
    for _ in range(6):
        cycle_counts.append(random.randint(5, 9))
    for _ in range(10):
        cycle_counts.append(random.randint(30, 160))
    for _ in range(4):
        cycle_counts.append(random.randint(10, 29))
    random.shuffle(cycle_counts)
    
    # Anomaly assignments
    temp_anomaly_batteries = set(random.sample(battery_ids, 2))
    remaining = list(set(battery_ids) - temp_anomaly_batteries)
    voltage_anomaly_batteries = set(random.sample(remaining, 2))
    
    records = []
    
    for batt_id, max_cycles in zip(battery_ids, cycle_counts):
        start_cap = random.uniform(1.8, 2.2)
        true_fade_rate = random.uniform(-0.006, -0.0005)
        temp_baseline = random.uniform(10.0, 45.0)
        
        temps = [temp_baseline]
        for _ in range(1, max_cycles):
            temps.append(temps[-1] + random.uniform(-1.0, 1.0))
            
        capacities = []
        for c in range(1, max_cycles + 1):
            noise = np.random.normal(0, start_cap * 0.005)
            cap = start_cap * (1 + true_fade_rate * c) + noise
            cap = max(0.3, min(cap, start_cap))
            capacities.append(cap)
            
        soh_values = [cap / capacities[0] for cap in capacities]
        
        voltages = []
        for soh in soh_values:
            v_noise = np.random.normal(0, 0.01)
            v = 3.7 - (1 - soh) * 0.6 + v_noise
            voltages.append(v)
            
        # Inject anomalies on final cycle
        if batt_id in temp_anomaly_batteries:
            mean_t = np.mean(temps)
            std_t = np.std(temps)
            temps[-1] = mean_t + 3.0 * std_t + 5.0 # Ensure > 2 std dev
            
        if batt_id in voltage_anomaly_batteries:
            mean_v = np.mean(voltages)
            std_v = np.std(voltages)
            voltages[-1] = mean_v - 3.0 * std_v - 0.2 # Ensure > 2 std dev (sag)
            
        for i in range(max_cycles):
            records.append({
                "battery_id": batt_id,
                "cycle": i + 1,
                "voltage": round(voltages[i], 4),
                "temperature": round(temps[i], 2),
                "capacity": round(capacities[i], 4),
                "soh": round(soh_values[i], 4),
                "rul": max_cycles - (i + 1)
            })
            
    df = pd.DataFrame(records)
    out_path = os.path.join(os.path.dirname(__file__), "synthetic_battery_dataset.csv")
    df.to_csv(out_path, index=False)
    
    # Print summary
    print(f"Generated 20 synthetic batteries.")
    print(f"Total rows: {len(df)}")
    print(f"Min cycles: {min(cycle_counts)}, Max cycles: {max(cycle_counts)}")
    print(f"Batteries with <10 cycles: {sum(1 for c in cycle_counts if c < 10)}")
    print(f"Batteries with 10-29 cycles: {sum(1 for c in cycle_counts if 10 <= c < 30)}")
    print(f"Batteries with >=30 cycles: {sum(1 for c in cycle_counts if c >= 30)}")
    print(f"Temperature anomaly batteries: {temp_anomaly_batteries}")
    print(f"Voltage anomaly batteries: {voltage_anomaly_batteries}")
    print(f"Saved to {out_path}")

if __name__ == "__main__":
    generate_synthetic_data()
