import io
from datetime import datetime
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


def build_chart(runs: list[dict]) -> io.BytesIO:
    dates = [datetime.strptime(r["date"], "%Y-%m-%d") for r in runs]
    distances = [r["distance_km"] for r in runs]
    paces = [r["pace_sec_per_km"] / 60 for r in runs]

    fig, ax1 = plt.subplots(figsize=(10, 5))
    fig.patch.set_facecolor("#1a1a2e")
    ax1.set_facecolor("#16213e")

    bars = ax1.bar(dates, distances, color="#0f3460", width=0.6, zorder=2)
    for bar, val in zip(bars, distances):
        ax1.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.05,
            f"{val:.1f}",
            ha="center", va="bottom", fontsize=8, color="white",
        )

    ax1.set_xlabel("Дата", color="white")
    ax1.set_ylabel("Дистанция, км", color="#e94560")
    ax1.tick_params(axis="y", labelcolor="#e94560")
    ax1.tick_params(axis="x", labelcolor="white", rotation=30)
    ax1.xaxis.set_major_formatter(mdates.DateFormatter("%d.%m"))
    ax1.yaxis.grid(True, linestyle="--", alpha=0.3, color="white")
    ax1.set_axisbelow(True)

    ax2 = ax1.twinx()
    ax2.plot(dates, paces, color="#e94560", marker="o", linewidth=2, markersize=5, zorder=3)
    ax2.set_ylabel("Темп, мин/км", color="#e94560")
    ax2.tick_params(axis="y", labelcolor="#e94560")
    ax2.invert_yaxis()

    ax1.set_title("Пробежки за последние 30 дней", color="white", fontsize=13, pad=12)

    for spine in ax1.spines.values():
        spine.set_edgecolor("#333")
    for spine in ax2.spines.values():
        spine.set_edgecolor("#333")

    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=120, facecolor=fig.get_facecolor())
    plt.close(fig)
    buf.seek(0)
    return buf
