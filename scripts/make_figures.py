"""Build the README figures (bar charts only: the GPS file has inconsistent coordinates, so no geographic map) from the CSV files in data/ and results/.

Run from the repository root:  python scripts/make_figures.py
"""
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False})

edges = pd.read_csv("results/Overload_edges.csv")
crit = pd.read_csv("results/critical_intersections.csv")
# 1. Most loaded connections
t = edges.nlargest(10, "flow").iloc[::-1]
fig, ax = plt.subplots(figsize=(8, 4.2))
ax.barh(t.station1 + " – " + t.station2, t.flow / 1000, color="#c0392b")
ax.set_xlabel("Passengers (thousands)")
ax.set_title("Top 10 most loaded connections")
fig.tight_layout()
fig.savefig("images/top_flows.png", dpi=150)
plt.close(fig)

# 2. Most critical inter-stations
t = crit.nlargest(10, "avg_diff_distance %").iloc[::-1]
fig, ax = plt.subplots(figsize=(8, 4.2))
ax.barh(t.removed_edge, t["avg_diff_distance %"], color="#1f3b73")
ax.set_xlabel("Increase of the average travel distance (%)")
ax.set_title("Top 10 critical inter-stations (368 single removals tested)")
fig.tight_layout()
fig.savefig("images/critical_interstations.png", dpi=150)
plt.close(fig)
