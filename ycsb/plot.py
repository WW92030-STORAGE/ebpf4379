import matplotlib.pyplot as plt
import numpy as np

# Example data: 6 experiments × 5 data points each
constant = 0.001
data = np.array([
    [25397.04704, 26075.00445], [37219.13203, 37986.75912]
]) * constant

stdevs = np.array([[2109.468417, 452.2817753], [162.2914176, 138.7438048]]) * constant

colors = ["#D5E8D4", "#FFE6CC", "#F8CECC", "#CDD9E9", "#F1E6C6", "#DBCFE1"]
edge_colors = ["#82B366", "#D79B00", "#B85450", "#6C8EBF", "#D6B656", "#9673A6"]
hatches = ["/", "x", "|", "\\", "+", "-"]
markers = ["o", "^", "P", "s", "v", "^"]

true_colors = [colors[2], colors[3]]
true_hatches = [hatches[0], hatches[3]]
true_edge_colors = [edge_colors[2], edge_colors[3]]

# String labels
methods = [
    "CBMM", "CBMM+Guardrail"
]

workloads = [
    "Workload A", "Workload D"
]

num_experiments = data.shape[0]
num_points = data.shape[1]

x = np.arange(num_experiments)
bar_width = 0.15

plt.rcParams["font.size"] = 20
plt.figure()

fig, ax = plt.subplots()

for i in range(num_points):
    offset = (i - num_points / 2) * bar_width + bar_width / 2
    ax.bar(x + offset, data[:, i], width=bar_width, label=methods[i], color = true_colors[i], hatch = true_hatches[i], edgecolor = true_edge_colors[i], yerr = stdevs[:, i], capsize = 4)

# Labels
plt.xlabel('Workload (YCSB mongodb)')
plt.ylabel('Throughput (kOps/s)')
plt.title('')

plt.xticks(x, workloads)
fig.legend(frameon=False, loc="upper center", ncol=2, bbox_to_anchor=(0.5, 0.95)) # Might need to change 1.06
plt.subplots_adjust(top=0.8, bottom=0.2, left=0.2, right=0.95) # Might need to adjust these numbers slightly; don't use tight_layout

plt.savefig("plot.pdf")
plt.savefig("plot.png")
plt.show()