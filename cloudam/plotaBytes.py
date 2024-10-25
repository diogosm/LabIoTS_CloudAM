import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
from sklearn.linear_model import LinearRegression
import numpy as np

def read_log_data(log_file):
    timestamps = []
    tx_bytes = []
    
    with open(log_file, 'r') as file:
        for line in file:
            if 'INFO' in line and 'TX:' in line:
                parts = line.split(" - ")
                timestamp_str = parts[0]
                tx_str = parts[2].split(", TX: ")[1]
                print(tx_str, flush=True)
                if( "0B" in tx_str ):
                    print("HERE!", flush=True)
                    continue
                print("THERE!", flush=True)

                timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S,%f")
                tx_value = float(tx_str.replace('kB', ''))  # Leave TX in kilobytes
                
                timestamps.append(timestamp)
                tx_bytes.append(tx_value)
    
    return timestamps, tx_bytes

log_file = "container_monitor.log"  
timestamps, tx_bytes = read_log_data(log_file)

# timestamps to numerical p linear regression
timestamps_numeric = mdates.date2num(timestamps).reshape(-1, 1)

# Time ranges
start_time = timestamps[0]
# 2024-10-24 22:19:26,230 - INFO - Running delay.sh to start pumba with 90% network loss                                │
pumba_start = datetime(2024, 10, 24, 22, 19, 26, 230)
# 2024-10-24 22:21:26,241 - INFO - Pumba finished                                                                       │
pumba_stop = datetime(2024, 10, 24, 22, 21, 26, 241)
after_pumba_stop = pumba_stop + (pumba_stop - pumba_start)

# segmentos do pumba
before_pumba_idx = np.where(np.array(timestamps) <= pumba_start)[0]
during_pumba_idx = np.where((np.array(timestamps) > pumba_start) & (np.array(timestamps) <= pumba_stop))[0]
after_pumba_idx = np.where(np.array(timestamps) > pumba_stop)[0]

# regressao nos 2 primeiros
# antes do Pumba
timestamps_before = np.array(timestamps_numeric[before_pumba_idx]).reshape(-1, 1)
tx_before = np.array(tx_bytes)[before_pumba_idx]
model_before = LinearRegression()
model_before.fit(timestamps_before, tx_before)
trend_line_before = model_before.predict(timestamps_before)
r_squared_before = model_before.score(timestamps_before, tx_before)
coef_before = model_before.coef_[0]
intercept_before = model_before.intercept_

# durante o Pumba
timestamps_during = np.array(timestamps_numeric[during_pumba_idx]).reshape(-1, 1)
tx_during = np.array(tx_bytes)[during_pumba_idx]
model_during = LinearRegression()
model_during.fit(timestamps_during, tx_during)
trend_line_during = model_during.predict(timestamps_during)
r_squared_during = model_during.score(timestamps_during, tx_during)
coef_during = model_during.coef_[0]
intercept_during = model_during.intercept_

# Fit a linear regression 
# model = LinearRegression()
# model.fit(timestamps_numeric, tx_bytes)
# trend_line = model.predict(timestamps_numeric)

# # Calculate the R-squared value
# r_squared = model.score(timestamps_numeric, tx_bytes)

plt.figure(figsize=(10, 6), dpi=300)
plt.plot(timestamps, tx_bytes, label="TX Bytes (kB)", marker='o', color='#1f77b4', linewidth=2)
plt.plot([timestamps[i] for i in before_pumba_idx], trend_line_before, 
         label=f"Before Pumba Starts (R² = {r_squared_before:.2f}, y={coef_before:.2f}x + {intercept_before:.2f})", linestyle='--', color='green', linewidth=2)

plt.plot([timestamps[i] for i in during_pumba_idx], trend_line_during, 
         label=f"During Pumba run (R² = {r_squared_during:.2f}), y={coef_during:.2f}x + {intercept_during:.2f})", linestyle='--', color='red', linewidth=2)

plt.axvline(pumba_start, color='green', linestyle='--', label='Pumba network loss started')
plt.axvline(pumba_stop, color='red', linestyle='--', label='Pumba network loss stopped')

# Formatting the plot for clarity
plt.xlabel("Timestamp")
plt.ylabel("TX Bytes (in kB)")
# plt.title("TX Bytes Over Time with Pumba Events")
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
plt.gca().xaxis.set_major_locator(mdates.MinuteLocator(interval=1))
plt.xticks(rotation=45)
plt.grid(True)

plt.legend()

plt.tight_layout()
plt.savefig("container_monitor_plot.png")

plt.show()
