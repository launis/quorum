def calculate_soft_waterfall_score(level_stats, scale_min, scale_max, threshold, base_forgiveness):
    achieved_score = float(scale_min)
    current_multiplier = 1.0
    prev_level = float(scale_min)
    
    sorted_levels = sorted(level_stats.keys())
    for level in sorted_levels:
        stats = level_stats[level]
        total = stats.get("total", 0)
        hits = stats.get("hits", 0)

        hit_rate = (hits / total) if total > 0 else 0.0
        step_value = level - prev_level

        if hit_rate >= threshold:
            achieved_score += step_value * current_multiplier
        else:
            achieved_score += step_value * hit_rate * current_multiplier
            current_multiplier *= base_forgiveness

        prev_level = level

    return float(max(scale_min, min(scale_max, achieved_score)))

def normalize_score_to_100(score, math_min, math_max):
    return ((score - math_min) / (math_max - math_min)) * 100

# Simulate sr_0f7947ec7007498c (75 atoms, 32 true -> 42.6%) distributed evenly across 3 levels
# Total hits = 32, Total atoms = 75
# Level 1: 11/25, Level 2: 11/25, Level 3: 10/25
stats_pass = {
    2.0: {"hits": 11, "total": 25}, # 44%
    3.0: {"hits": 11, "total": 25}, # 44%
    4.0: {"hits": 10, "total": 25}, # 40%
}
raw_pass = calculate_soft_waterfall_score(stats_pass, 1.0, 4.0, 0.40, 0.50)
print(f"Pass matrix Raw: {raw_pass}, Norm: {normalize_score_to_100(raw_pass, 1.0, 4.0)}")

# Simulate sr_02b7cc1e7c2a4a62 (123 atoms, 44 true -> 35.7%)
# Level 1: 15/41 (36.5%), Level 2: 15/41 (36.5%), Level 3: 14/41 (34.1%)
stats_fail = {
    2.0: {"hits": 15, "total": 41}, # 36.5%
    3.0: {"hits": 15, "total": 41}, # 36.5%
    4.0: {"hits": 14, "total": 41}, # 34.1%
}
raw_fail = calculate_soft_waterfall_score(stats_fail, 1.0, 4.0, 0.40, 0.50)
print(f"Fail matrix Raw: {raw_fail}, Norm: {normalize_score_to_100(raw_fail, 1.0, 4.0)}")

