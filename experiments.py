import os
import pandas as pd
import matplotlib.pyplot as plt

from baseline_webster import webster_delay
from model_lp import optimize_cycle

# Parameters
CYCLE = 90.0
SATURATION = 0.5

G_MIN = 25.0
G_MAX = 65.0

NS_SHARE = 0.6
EO_SHARE = 0.4

X_MAX = 0.90  # stability limit (keep x <= 0.90)

KAGGLE_CSV = "Metro_Interstate_Traffic_Volume.csv"


def avg_delay(flow_NS_vph, flow_EO_vph, g_NS, g_EO):
    """Average delay per vehicle (s/veh), weighted by flows."""
    f_ns = flow_NS_vph / 3600.0
    f_eo = flow_EO_vph / 3600.0

    d_ns = webster_delay(f_ns, SATURATION, g_NS, CYCLE)
    d_eo = webster_delay(f_eo, SATURATION, g_EO, CYCLE)

    total = flow_NS_vph + flow_EO_vph
    if total <= 1e-12:
        return 0.0

    return (flow_NS_vph * d_ns + flow_EO_vph * d_eo) / total


def main():
    scenarios = []

    # Toy scenarios
    scenarios += [
        ("toy", "toy_low", 600.0),
        ("toy", "toy_medium", 1200.0),
        ("toy", "toy_high", 1800.0),
    ]

    # Kaggle scenarios (if file exists)
    if os.path.exists(KAGGLE_CSV):
        df = pd.read_csv(KAGGLE_CSV)
        df["date_time"] = pd.to_datetime(df["date_time"])
        df["hour"] = df["date_time"].dt.hour

        for h in [3, 6, 8, 12, 17]:
            if h in df["hour"].unique():
                mean_total = float(df.loc[df["hour"] == h, "traffic_volume"].mean())
                scenarios.append(("kaggle", f"kaggle_hour_{h:02d}", mean_total))

    results = []

    for source, name, flow_total in scenarios:
        flow_NS = NS_SHARE * flow_total
        flow_EO = EO_SHARE * flow_total

        # Baseline (equal split)
        g_ns_base = CYCLE / 2.0
        g_eo_base = CYCLE / 2.0
        d_base = avg_delay(flow_NS, flow_EO, g_ns_base, g_eo_base)

        # Stability-based minimum green times
        gmin_ns = (flow_NS / 3600.0) * CYCLE / (X_MAX * SATURATION)
        gmin_eo = (flow_EO / 3600.0) * CYCLE / (X_MAX * SATURATION)

        gmin_eff = max(G_MIN, gmin_ns, gmin_eo)
        gmax_eff = min(G_MAX, CYCLE - gmin_eff)

        if gmin_eff > gmax_eff:
            gmin_eff, gmax_eff = G_MIN, G_MAX  # fallback

        # LP solution
        g_ns_lp, g_eo_lp = optimize_cycle(flow_NS, flow_EO, g_min=gmin_eff, g_max=gmax_eff, cycle=CYCLE)
        d_lp = avg_delay(flow_NS, flow_EO, g_ns_lp, g_eo_lp)

        # Improvement (%)
        imp = 100.0 * (d_base - d_lp) / d_base if d_base > 0 and d_base < 1e18 else None

        results.append({
            "source": source,
            "scenario": name,
            "flow_total_vph": flow_total,
            "flow_NS_vph": flow_NS,
            "flow_EO_vph": flow_EO,
            "g_NS_baseline": g_ns_base,
            "g_EO_baseline": g_eo_base,
            "delay_baseline_sveh": d_base,
            "g_NS_LP": g_ns_lp,
            "g_EO_LP": g_eo_lp,
            "delay_LP_sveh": d_lp,
            "improvement_pct": imp
        })

    out = pd.DataFrame(results)
    out.to_csv("results_summary.csv", index=False)
    print(out)

    # Plot
    plt.figure()
    plt.plot(out["scenario"], out["delay_baseline_sveh"], marker="o", label="Baseline")
    plt.plot(out["scenario"], out["delay_LP_sveh"], marker="o", label="LP")
    plt.xticks(rotation=45, ha="right")
    plt.xlabel("Scenario")
    plt.ylabel("Average delay (s/veh)")
    plt.title("Baseline vs LP (Toy + Kaggle)")
    plt.legend()
    plt.tight_layout()
    plt.savefig("delay_comparison.png", dpi=200)
    plt.close()

    print("Saved: results_summary.csv and delay_comparison.png")


if __name__ == "__main__":
    main()
