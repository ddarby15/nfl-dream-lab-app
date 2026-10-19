from pathlib import Path

import pandas as pd
import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parents[4]
GOLD_ROOT = PROJECT_ROOT / "data" / "gold"

# Display name: (folder below data/gold, filename before _{season}.parquet)
GOLD_DATASETS = {
    "receiving_player_game": (
        "receiving/player_game",
        "gold_receiving_player_game",
    ),
    "receiving_player_team_season": (
        "receiving/player_team_season",
        "gold_receiving_player_team_season",
    ),
    "team_week_metrics": (
        "team_week_metrics",
        "gold_team_week_metrics",
    ),
    "wr_waiver": ("waiver/wr_weekly_trends", "wr_weekly_trends"),
    "rb_waiver": ("waiver/rb_weekly_trends", "rb_weekly_trends"),
    "qb_waiver": ("waiver/qb_weekly_trends", "qb_weekly_trends"),
    "wr_draft": ("draft/wr_season_features", "wr_season_features"),
    "rb_draft": ("draft/rb_season_features", "rb_season_features"),
    "qb_draft": ("draft/qb_season_features", "qb_season_features"),
}


@st.cache_data(ttl=300)
def load_gold_data(
    dataset: str,
    season: int | None = None,
) -> pd.DataFrame:
    if dataset not in GOLD_DATASETS:
        raise ValueError(
            f"Unknown Gold dataset: {dataset!r}. "
            f"Choose from {sorted(GOLD_DATASETS)}"
        )

    folder_name, file_stem = GOLD_DATASETS[dataset]
    dataset_dir = GOLD_ROOT / folder_name

    if season is None:
        paths = sorted(dataset_dir.glob(f"{file_stem}_*.parquet"))
    else:
        paths = [dataset_dir / f"{file_stem}_{season}.parquet"]

    missing_paths = [path for path in paths if not path.is_file()]
    if not paths or missing_paths:
        raise FileNotFoundError(
            f"No complete set of files found for {dataset!r}, "
            f"season={season!r}, in {dataset_dir}"
        )

    return pd.concat(
        [pd.read_parquet(path) for path in paths],
        ignore_index=True,
    )
    
