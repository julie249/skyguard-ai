import time, sys

def edge_detect(temp, pressure, humidity, temp_mean=28.0, temp_std=4.0, p_mean=1013.0, p_std=5.0, h_mean=65.0, h_std=10.0):
    z_temp = abs((temp - temp_mean) / max(temp_std, 0.001))
    z_p = abs((pressure - p_mean) / max(p_std, 0.001))
    z_h = abs((humidity - h_mean) / max(h_std, 0.001))
    max_z = max(z_temp, z_p, z_h)
    is_anomaly = max_z > 3.0
    return is_anomaly, round(max_z, 4)

N = 10000
start = time.perf_counter()
for _ in range(N):
    edge_detect(28.5, 1013.2, 65.0)
elapsed = time.perf_counter() - start
per_call_ms = (elapsed / N) * 1000
print(f"Platform: Python {sys.version}")
print(f"Runs: {N}")
print(f"Total: {elapsed*1000:.2f}ms")
print(f"Per-call avg: {per_call_ms:.4f}ms")

anomaly, z = edge_detect(55.0, 1013.2, 65.0)
print(f"Spike 55C -> is_anomaly={anomaly}, max_z={z}")
