from pathlib import Path

import streamlit as st
import pandas as pd


@st.cache_data
def load_gold_data(
    # filename: str,
    # season_folder: int = 2026,
    # subdir: str = "transformed_data",
    verbose=False
) -> pd.DataFrame:
    
    PROJECT_ROOT = Path.cwd()
    if verbose:
        print(f"\nCurrent Working Directory: {PROJECT_ROOT}")
    
    # Search for ROADMAP.md which is at the level of our Data folder
    if not (PROJECT_ROOT / "ROADMAP.md").exists():
        # check each parent folder for ROADMAP.md
        for parent in PROJECT_ROOT.parents:
            if verbose:
                print(f"Parent: {parent}")
            if (parent / "ROADMAP.md").exists():
                # reset the project root
                PROJECT_ROOT = parent
                if verbose:
                    print(f"Root Dir: {parent}")
                break
        else:
            raise RuntimeError("Could not locate the repository root.")

    GOLD_OUTPUT_DIR = PROJECT_ROOT / "data/gold/waiver/wr_weekly_trends"
    
    wr_week_paths = sorted(GOLD_OUTPUT_DIR.glob("*.parquet"))
    if verbose:
        print(wr_week_paths)
    
    # loop through each file, load, and concatenate
    wr_week = pd.concat([pd.read_parquet(path) for path in wr_week_paths], 
                        ignore_index=True
                        )
    return wr_week
    
