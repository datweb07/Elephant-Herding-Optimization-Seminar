def summarize_experiment_results(frame, tolerance=None):
    """Tóm tắt nhóm, độ lệch chuẩn và phương sai mẫu với ddof = 1."""
    grouped = frame.groupby("group", sort=False)
    summary = grouped.agg(
        runs=("fitness", "size"), minimum=("fitness", "min"), mean=("fitness", "mean"),
        median=("fitness", "median"), maximum=("fitness", "max"), std=("fitness", "std"),
        variance=("fitness", "var"), seconds=("seconds", "mean"), evaluations=("evaluations", "mean"),
        feasible_rate=("best_in_bounds", "mean"), violations=("violating_coordinates", "mean"),
    )
    if tolerance is not None:
        hits = frame["fitness"] <= tolerance
        summary["target_rate"] = hits.groupby(frame["group"]).mean()
    return summary
