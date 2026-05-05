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

stats_fail = {
    2.0: {"hits": 22, "total": 61}, # 36%
    3.0: {"hits": 22, "total": 62}, # 35%
}
raw_fail = calculate_soft_waterfall_score(stats_fail, 1.0, 3.0, 0.40, 0.0) # What if strictness_level = 100, so base_forgiveness = 0.0?
print(f"Fail matrix Raw (Strictness 100): {raw_fail}")

stats_fail2 = {
    2.0: {"hits": 22, "total": 61}, # 36%
    3.0: {"hits": 22, "total": 62}, # 35%
}
raw_fail2 = calculate_soft_waterfall_score(stats_fail2, 1.0, 3.0, 0.40, 0.5) # What if strictness_level = 50, so base_forgiveness = 0.5?
print(f"Fail matrix Raw (Strictness 50): {raw_fail2}")
