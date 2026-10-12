"""
plot_style.py
Shared colors and axis styling, so every results graph looks the same.
"""

# One color per line, in this order
COLORS = ["#2a78d6", "#eb6834", "#1baf7a", "#8a5cd1", "#d1a21b"]

# Census points and text notes
DARK = "#2b2a27"
GRAY = "#52514e"


def style_axes(ax):
    """Light gridlines behind the data, no top and right borders."""
    ax.grid(color="#e1e0d9", linewidth=0.8)
    ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
