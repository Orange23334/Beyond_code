#!/usr/bin/env python3
"""Render Figure 2 as reproducible, publication-quality vector artwork.

The selection counts are archived review checkpoints, not execution statuses
or a reconciled ledger of nested subsets. Criteria and provenance are detailed
in the method table; comparison completion belongs in the figure caption.
Run from any directory with Python and matplotlib; no external assets needed.
"""

from pathlib import Path
import json

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyArrowPatch, FancyBboxPatch


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "figures" / "benchmark_audit_pipeline"
STUDY_N = str(json.loads((ROOT / "data/results_snapshot.json").read_text())["study_benchmarks"])

INK = "#18334A"
MUTED = "#526676"
LINE = "#B9C7D0"
BLUE = "#276493"
BLUE_PALE = "#EEF5FA"
TEAL = "#167E80"
TEAL_PALE = "#ECF7F5"
ORANGE = "#B56D2C"

plt.rcParams.update(
    {
        "font.family": "DejaVu Sans",
        "font.size": 16,
        "text.color": INK,
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
        "svg.fonttype": "path",
    }
)

fig, ax = plt.subplots(figsize=(14.4, 5.25))
fig.subplots_adjust(left=0, right=1, bottom=0, top=1)
ax.set_xlim(0, 14.4)
ax.set_ylim(0, 5.25)
ax.axis("off")


def text(x, y, label, size=18.5, color=INK, weight="normal", **kwargs):
    return ax.text(
        x, y, label, fontsize=size, color=color, weight=weight,
        va="center", **kwargs
    )


def line(x1, y1, x2, y2, color=LINE, width=1.3, **kwargs):
    ax.plot([x1, x2], [y1, y2], color=color, lw=width,
            solid_capstyle="round", **kwargs)


def arrow(x1, y1, x2, y2, color=MUTED):
    ax.add_patch(FancyArrowPatch(
        (x1, y1), (x2, y2), arrowstyle="-|>",
        mutation_scale=13, linewidth=1.5, color=color,
        shrinkA=0, shrinkB=0,
    ))


def rounded(x, y, w, h, fill, edge="none", radius=0.10, lw=1.2):
    ax.add_patch(FancyBboxPatch(
        (x, y), w, h,
        boxstyle=f"round,pad=0,rounding_size={radius}",
        facecolor=fill, edgecolor=edge, linewidth=lw,
    ))


def heading(x, number, title, width, color=BLUE):
    ax.add_patch(Circle((x + 0.16, 4.72), 0.16, facecolor=color, edgecolor="none"))
    text(x + 0.16, 4.72, str(number), size=14, color="white", weight="bold", ha="center")
    text(x + 0.44, 4.72, title, size=19, weight="bold")
    line(x, 4.36, x + width, 4.36, color="#DDE5EB", width=1.1)


# Five stages, with the two comparison arms given extra horizontal space.
heading(0.16, 1, "Select", 2.34)
heading(2.92, 2, "Verify SOTA", 2.20)
heading(5.57, 3, "Audit tasks", 2.18)
heading(8.26, 4, "Compare", 2.95, color=TEAL)
heading(11.81, 5, "Analyze", 2.37, color=ORANGE)

# Criteria-based review checkpoints. Equal-width tiles avoid presenting the
# dated inventories as a verified, strictly nested population funnel.
selection_center = 0.75
selection_rows = [
    (3.75, "554", "Candidate\npool", "#E1ECF5", BLUE),
    (2.99, "83", "Evidence\nscreen", "#C4D9E9", BLUE),
    (2.23, "30", "Feasibility\nreview", "#8AB5D1", INK),
    (1.47, STUDY_N, "Study\ninclusion", BLUE, "white"),
]
for cy, count, label, fill, number_color in selection_rows:
    rounded(selection_center - 0.53, cy - 0.32, 1.06, 0.64, fill, radius=0.06)
    text(selection_center, cy + 0.015, count, size=23, color=number_color,
         weight="bold", ha="center")
    text(1.42, cy, label, size=17.5, linespacing=1.08,
         weight="bold" if count == STUDY_N else "normal")

# Reference verification: compact hierarchy without a large enclosing box.
text(2.92, 3.80, "Find systems", size=18.5, weight="bold")
text(2.92, 3.40, "Citation + text", size=18.5, color=MUTED)
text(2.92, 3.10, "search", size=18.5, color=MUTED)
text(2.92, 2.56, "Verify scores", size=18.5, weight="bold")
text(2.92, 2.16, "Tables + splits", size=18.5, color=MUTED)
rounded(2.92, 1.18, 2.20, 0.53, BLUE_PALE)
text(4.02, 1.445, "Paper score", size=18.5, color=BLUE,
     weight="bold", ha="center")

# Executable audit: explicit checks and their reusable output.
text(5.57, 3.80, "Build tasks", size=18.5, weight="bold")
text(5.57, 3.40, "Inputs + tools", size=18.5, color=MUTED)
text(5.57, 3.10, "Grader controls", size=18.5, color=MUTED)
text(5.57, 2.56, "Validate runs", size=18.5, weight="bold")
text(5.57, 2.16, "Fidelity checks", size=18.5, color=MUTED)
rounded(5.57, 1.18, 2.18, 0.53, BLUE_PALE)
text(6.66, 1.445, "Run policy", size=18.5, color=BLUE,
     weight="bold", ha="center")

# The two arms answer different questions and are visually separate.
rounded(8.26, 2.94, 2.95, 1.14, BLUE_PALE, edge="#BDCEDC")
rounded(8.26, 1.29, 2.95, 1.14, TEAL_PALE, edge="#ACD2CE")
line(8.28, 3.94, 8.28, 3.08, BLUE, width=3)
line(8.28, 2.29, 8.28, 1.43, TEAL, width=3)
text(8.45, 3.81, "Published-score", size=18.5, color=BLUE, weight="bold")
text(8.45, 3.46, "Codex vs.", size=18.5, color=MUTED)
text(8.45, 3.15, "paper SOTA", size=18.5, color=MUTED)
text(8.45, 2.16, "Shared-backbone", size=18.5, color=TEAL, weight="bold")
text(8.45, 1.81, "Codex vs.", size=18.5, color=MUTED)
text(8.45, 1.50, "specialist rerun", size=18.5, color=MUTED)

# Analysis is an output, not another protocol-validation gate.
text(11.81, 3.80, "Paired estimates", size=18.5, weight="bold")
text(11.81, 3.41, "Effects + CIs", size=18.5, color=MUTED)
text(11.81, 2.85, "Domain patterns", size=18.5, weight="bold")
text(11.81, 2.46, "Task taxonomy", size=18.5, color=MUTED)
text(11.81, 1.90, "Trace analysis", size=18.5, weight="bold")
text(11.81, 1.51, "Wins and losses", size=18.5, color=MUTED)

# Thin connectors preserve the workflow without competing with the content.
arrow(2.53, 2.67, 2.80, 2.67)
arrow(5.19, 2.67, 5.47, 2.67)
line(7.80, 2.67, 8.02, 2.67)
line(8.02, 1.86, 8.02, 3.51)
arrow(8.02, 3.51, 8.19, 3.51, color=BLUE)
arrow(8.02, 1.86, 8.19, 1.86, color=TEAL)
line(11.25, 3.51, 11.46, 3.51, color=BLUE)
line(11.25, 1.86, 11.46, 1.86, color=TEAL)
line(11.46, 1.86, 11.46, 3.51)
arrow(11.46, 2.67, 11.71, 2.67)

# A supporting audit trail, rather than a sixth dominant stage.
rounded(0.16, 0.22, 14.02, 0.57, "#F2F5F7", radius=0.07)
text(0.37, 0.505, "AUDIT TRAIL", size=14, weight="bold", color=MUTED)
line(1.83, 0.36, 1.83, 0.65, color="#CBD5DD", width=1.0)
text(2.03, 0.505,
     "Source evidence   ·   Versioned artifacts   ·   Adversarial checks   ·   Human review",
     size=18.5, color=MUTED)

OUT.parent.mkdir(parents=True, exist_ok=True)
fig.savefig(OUT.with_suffix(".pdf"), facecolor="white", metadata={"Title": "Benchmark audit pipeline"})
fig.savefig(OUT.with_suffix(".svg"), facecolor="white")
fig.savefig(OUT.with_suffix(".png"), dpi=180, facecolor="white")
plt.close(fig)
print(f"Wrote {OUT}.{{pdf,svg,png}}")
