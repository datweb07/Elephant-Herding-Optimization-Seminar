import json
import os
from pathlib import Path

import matplotlib.pyplot as plt

from objectives.data_loader import DATA_DIR


def save_experiment_artifacts(experiment, section, mode, seeds, runs, summary):
    """Lưu bảng, cấu hình và hình khi đặt EHO_SAVE_RESULTS=1."""
    if os.getenv("EHO_SAVE_RESULTS") != "1":
        return
    directory = DATA_DIR.parent / "outputs" / mode.lower() / experiment / section
    directory.mkdir(parents=True, exist_ok=True)
    runs.to_csv(directory / "runs.csv", index=False, encoding="utf-8-sig")
    summary.to_csv(directory / "summary.csv", encoding="utf-8-sig")
    metadata = {"mode": mode, "seeds": list(seeds), "runs": len(runs)}
    (directory / "metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    for index, figure_number in enumerate(plt.get_fignums(), 1):
        plt.figure(figure_number).savefig(directory / f"figure-{index}.png", dpi=120)
