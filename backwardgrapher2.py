import os
import matplotlib.pyplot as plt

# ================== USER PARAMETERS =====================
BASE_DIR = "/home/aubrey/PycharmProjects/PythonProject/back_ward_test_data"
RESULTS_PREFIX = "results_steps_"
DATASET_SIZE = 50  # always divide by 50

INVERTIBLE_STEPS_RANGE = range(1, 28)
x_values = list(INVERTIBLE_STEPS_RANGE)

# ================== INITIALIZE DATA =====================
avg_time = []
avg_size = []
avg_deg = []
avg_terms = []

# ================== PROCESS FILES =======================
for steps in x_values:
    file_path = os.path.join(BASE_DIR, f"{RESULTS_PREFIX}{steps}.txt")

    total_time = 0
    total_size = 0
    total_deg = 0
    total_terms = 0

    if not os.path.isfile(file_path):
        print(f"Warning: {file_path} does not exist, skipping.")
        avg_time.append(0)
        avg_size.append(0)
        avg_deg.append(0)
        avg_terms.append(0)
        continue

    with open(file_path, "r") as f:
        next(f)  # skip header
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split(",")

            # handle TIMEOUT rows or malformed rows
            try:
                t = float(parts[0])
                s = float(parts[1])
                d = float(parts[2])
                terms = float(parts[3])

                # ignore negative times (possible data errors)
                if t < 0:
                    t = 0

            except (ValueError, IndexError):
                # TIMEOUT or bad row → treat time as 0, but still count others if numeric
                t = 0
                s = float(parts[1]) if len(parts) > 1 and parts[1] else 0
                d = float(parts[2]) if len(parts) > 2 and parts[2] else 0
                terms = float(parts[3]) if len(parts) > 3 and parts[3] else 0

            total_time += t
            total_size += s
            total_deg += d
            total_terms += terms

    # strict average by dataset size
    avg_time.append(total_time / DATASET_SIZE)
    avg_size.append(total_size / DATASET_SIZE)
    avg_deg.append(total_deg / DATASET_SIZE)
    avg_terms.append(total_terms / DATASET_SIZE)

# ================== PLOTTING ============================
metrics = {
    "Time (s)": avg_time,
    "Groebner Size": avg_size,
    "Max Degree": avg_deg,
    "Total Terms": avg_terms
}

for i, (label, data) in enumerate(metrics.items(), 1):
    plt.figure(i, figsize=(8, 5))
    plt.plot(x_values, data, marker='o', linestyle='-', color='tab:blue')
    plt.xlabel("Number of Invertible Steps")
    plt.ylabel(f"Average {label}")
    plt.title(f"{label} vs Invertible Steps")
    plt.xticks(x_values)
    plt.grid(True)
    plt.tight_layout()
    plt.show()
