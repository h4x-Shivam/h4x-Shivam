import os, requests, datetime, numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib.patches import FancyBboxPatch

USERNAME = os.environ.get("GH_USERNAME", "h4x-Shivam")
TOKEN    = os.environ.get("GITHUB_TOKEN", "")

headers = {"Authorization": f"bearer {TOKEN}", "Content-Type": "application/json"}

query = """
{
  user(login: "%s") {
    contributionsCollection {
      contributionCalendar {
        weeks { contributionDays { date contributionCount } }
      }
    }
  }
}
""" % USERNAME

r = requests.post("https://api.github.com/graphql", json={"query": query}, headers=headers)
weeks = r.json()["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]

days = []
for w in weeks:
    for d in w["contributionDays"]:
        days.append({"date": d["date"], "count": d["contributionCount"]})

days = days[-30:]
dates  = [d["date"][5:] for d in days]   # MM-DD
counts = [d["count"]    for d in days]

avg7 = [round(np.mean(counts[max(0,i-6):i+1]), 1) for i in range(len(counts))]

total  = sum(counts)
peak   = max(counts)
streak = 0
for c in reversed(counts):
    if c > 0: streak += 1
    else: break

# ── style ──────────────────────────────────────────────────
BG      = "#0d1117"
GRID    = "#21262d"
TEAL    = "#1D9E75"
CYAN    = "#00E5FF"
MUTED   = "#30363d"
TEXT    = "#e6edf3"
SUBTEXT = "#8b949e"

fig, ax = plt.subplots(figsize=(12, 4.2))
fig.patch.set_facecolor(BG)
ax.set_facecolor(BG)

bar_colors = [TEAL if c > 0 else MUTED for c in counts]
bars = ax.bar(range(len(counts)), counts, color=bar_colors,
              width=0.65, zorder=3, linewidth=0)
for bar in bars:
    bar.set_capstyle("round")

ax.plot(range(len(avg7)), avg7, color=CYAN, linewidth=1.4,
        linestyle=(0,(4,3)), zorder=4, alpha=0.75)

ax.set_xticks(range(0, len(dates), 3))
ax.set_xticklabels([dates[i] for i in range(0, len(dates), 3)],
                   fontsize=9, color=SUBTEXT, fontfamily="monospace")
ax.yaxis.set_major_locator(ticker.MaxNLocator(integer=True, nbins=5))
ax.tick_params(colors=SUBTEXT, length=0)
ax.yaxis.set_tick_params(labelsize=9, labelcolor=SUBTEXT)

ax.grid(axis="y", color=GRID, linewidth=0.5, zorder=0)
ax.set_axisbelow(True)
for spine in ax.spines.values(): spine.set_visible(False)

# stat annotations top-right
stats = [
    (f"{total}", "total commits"),
    (f"{peak}", "peak day"),
    (f"{streak}d", "current streak"),
]
for i, (val, lbl) in enumerate(stats):
    x = 0.99 - i * 0.13
    ax.text(x, 1.12, val, transform=ax.transAxes, ha="right",
            fontsize=15, fontweight="bold", color=TEXT, fontfamily="monospace")
    ax.text(x, 1.02, lbl, transform=ax.transAxes, ha="right",
            fontsize=8, color=SUBTEXT, fontfamily="monospace")

ax.text(0.0, 1.12, f"h4x-Shivam", transform=ax.transAxes,
        fontsize=12, fontweight="bold", color=TEAL, fontfamily="monospace")
ax.text(0.0, 1.02, "contribution activity · last 30 days",
        transform=ax.transAxes, fontsize=8, color=SUBTEXT, fontfamily="monospace")

plt.tight_layout(pad=1.2)
os.makedirs("assets", exist_ok=True)
plt.savefig("assets/contribution-chart.png", dpi=160,
            bbox_inches="tight", facecolor=BG)
print(f"saved · {total} commits · peak {peak} · streak {streak}d")
