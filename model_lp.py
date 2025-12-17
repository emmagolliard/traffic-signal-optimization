import pulp


def optimize_cycle(flow_NS, flow_EO, g_min=10, g_max=60, cycle=90):
    """LP optimization of green times."""

    # Basic checks
    if cycle <= 0:
        raise ValueError("cycle must be > 0")
    if g_min < 0 or g_max < 0:
        raise ValueError("g_min and g_max must be non-negative")
    if g_min > g_max:
        raise ValueError("g_min must be <= g_max")

    # Feasible bounds for g_NS (because g_EO = cycle - g_NS)
    lower = max(g_min, cycle - g_max)
    upper = min(g_max, cycle - g_min)
    if lower > upper:
        raise ValueError(f"Infeasible bounds: [{lower}, {upper}]")

    # LP model
    model = pulp.LpProblem("TrafficLightOptimization", pulp.LpMinimize)

    # Decision variables
    g_NS = pulp.LpVariable("g_NS", lowBound=lower, upBound=upper)
    g_EO = pulp.LpVariable("g_EO", lowBound=g_min, upBound=g_max)

    # Cycle constraint
    model += g_NS + g_EO == cycle

    # Linear objective: flow-weighted red time
    red_NS = cycle - g_NS
    red_EO = cycle - g_EO
    main_obj = flow_NS * red_NS + flow_EO * red_EO

    # Tie-break variable (for equal flows)
    mid = 0.5 * (lower + upper)
    t = pulp.LpVariable("t", lowBound=0.0)

    # Absolute value linearization
    model += g_NS - mid <= t
    model += mid - g_NS <= t

    # Small epsilon to keep main optimum unchanged
    eps = 1e-6
    model += main_obj + eps * t

    # Solve LP
    model.solve(pulp.PULP_CBC_CMD(msg=False))

    return float(g_NS.value()), float(g_EO.value())


if __name__ == "__main__":
    # Simple tests
    for ns, eo in [(200, 300), (300, 200), (250, 250)]:
        gNS, gEO = optimize_cycle(ns, eo, g_min=10, g_max=80, cycle=90)
        print(f"flows NS={ns}, EO={eo} -> g_NS={gNS:.1f}s, g_EO={gEO:.1f}s")

