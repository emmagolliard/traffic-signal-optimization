def webster_delay(flow, saturation, green, cycle):
    # Computes a simple delay proxy inspired by Webster's formula
    # flow and saturation are in veh/s, times are in seconds

    g_ratio = green / cycle                 # fraction of green time in the cycle
    capacity = saturation * g_ratio         # effective service capacity

    if capacity <= 1e-12:
        return 1e9                          

    x = flow / capacity                    # volume-to-capacity ratio

    if x >= 1:
        return 1e9                          # oversaturated traffic conditions

    # Webster-inspired delay approximation
    delay = (cycle * (1 - g_ratio) ** 2) / (2 * (1 - x))
    return delay                            # delay in seconds per vehicle


if __name__ == "__main__":
    # Simple test to verify the function behavior
    flow = 300 / 3600                       # traffic flow (veh/s)
    saturation = 0.5                        # saturation flow (veh/s)
    green = 30                              # green time (s)
    cycle = 90                              # cycle length (s)

    d = webster_delay(flow, saturation, green, cycle)
    print(f"Estimated delay proxy: {d:.2f} s/veh")
