import matplotlib.pyplot as plt

# x-axis values
x = [10, 12, 14, 16, 18, 20]

# Data
avg_time = [0.0015, 0.0070, 0.0916, 0.2864, 0.1480, 0.3341]
avg_size = [6.18, 6.35, 6.12, 6.23, 6.05, 6.17]
avg_degree = [2.51, 2.37, 2.57, 2.35, 2.64, 2.36]
avg_terms = [21.65, 23.53, 21.65, 22.26, 21.05, 21.72]

# ------------------ Average Time ------------------
plt.figure()
plt.plot(x, avg_time, marker='o')
plt.xlabel("Parameter value")
plt.ylabel("Average time (s)")
plt.title("Average Groebner Basis Computation Time")
plt.show()

# ------------------ Average Size ------------------
plt.figure()
plt.plot(x, avg_size, marker='o')
plt.xlabel("Parameter value")
plt.ylabel("Average basis size")
plt.title("Average Groebner Basis Size")
plt.show()

# ------------------ Average Degree ------------------
plt.figure()
plt.plot(x, avg_degree, marker='o')
plt.xlabel("Parameter value")
plt.ylabel("Average max degree")
plt.title("Average Maximum Degree of Groebner Basis")
plt.show()

# ------------------ Average Terms ------------------
plt.figure()
plt.plot(x, avg_terms, marker='o')
plt.xlabel("Parameter value")
plt.ylabel("Average number of terms")
plt.title("Average Number of Terms in Groebner Basis")
plt.show()
