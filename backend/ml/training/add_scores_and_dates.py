

import sys, os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
sys.path.append(PROJECT_ROOT)

import pandas as pd
from backend.ml.pipeline import add_comfort_scores, add_dates



def main():
    """Load historical weather data, add comfort scores, and save the output."""

    base_dir = os.path.dirname(os.path.abspath(__file__))   
    data_path = os.path.join(base_dir, "..", "data", "historical_weather_master.csv")

    # Normalize path
    data_path = os.path.normpath(data_path)

    print(f"Loading dataset from: {data_path}")
    master_df = pd.read_csv(data_path)

    scored_df = add_comfort_scores(master_df)
    scored_df = add_dates(scored_df)
    # Save output
    output_path = os.path.join(base_dir, "..", "data", "historical_weather_scored.csv")
    output_path = os.path.normpath(output_path)

    scored_df.to_csv(output_path, index=False)
    print(f"Saved comfort-scored dataset to: {output_path}")


if __name__ == "__main__":
    main()
