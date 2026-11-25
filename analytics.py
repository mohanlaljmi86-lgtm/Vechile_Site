
import matplotlib.pyplot as plt
import pandas as pd


def monthly_expense_chart(trips):
    df = trips.copy()

    df["created_at"] = pd.to_datetime(
        df["created_at"],
        errors="coerce"
    )

    df = df.dropna(subset=["created_at"])

    monthly = df.groupby(
        df["created_at"].dt.to_period("M")
    )["total_cost"].sum()

    fig, ax = plt.subplots(figsize=(9, 4))

    if monthly.empty:
        ax.text(
            0.5, 0.5,
            "No monthly trip data",
            ha="center",
            va="center"
        )
    else:
        monthly.index = monthly.index.astype(str)
        monthly.plot(kind="bar", ax=ax)

    ax.set_title("Monthly Travel Expenses")
    ax.set_xlabel("Month")
    ax.set_ylabel("Expense (₹)")

    fig.tight_layout()

    return fig


def vehicle_cost_chart(
    cost_a,
    cost_b,
    label_a,
    label_b
):
    fig, ax = plt.subplots(figsize=(7, 3.5))

    ax.bar(
        [label_a[:24], label_b[:24]],
        [cost_a, cost_b]
    )

    ax.set_ylabel("Estimated Cost (₹)")
    ax.set_title("Vehicle Running Cost Comparison")

    fig.tight_layout()

    return fig
