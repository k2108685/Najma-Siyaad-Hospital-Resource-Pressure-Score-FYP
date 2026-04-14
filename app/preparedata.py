from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent

AE_FILE = BASE_DIR / "data/raw/aemonthly.xls"
BEDS_FILE = BASE_DIR / "data/raw/Beds-publication-Timeseries-March-2020-February-2026.xlsx"
OUTPUT_FILE = BASE_DIR / "data/processed/ae_pressure_with_score.csv"

def scale_values(series):
    series = pd.to_numeric(series, errors="coerce")
    min_value = series.min()
    max_value = series.max()

    if pd.isna(min_value) or pd.isna(max_value) or min_value == max_value:
        return pd.Series(0.0, index=series.index)

    return (series - min_value) / (max_value - min_value)


def find_column(df, candidates):
    return next((column for column in candidates if column in df.columns), None)


def main():
    print("Loading A&E data...")

    df = pd.read_excel(AE_FILE, header=13)
    df.columns = df.columns.str.strip()

    period_col = find_column(df, ["Period", "Date", "Month"])
    attendances_col = find_column(df, ["Total Attendances", "Attendances"])
    admissions_col = find_column(df, ["Total Emergency Admissions", "Total Emergency Admissions via A&E", "Admissions"])
    delay_col = find_column(df, [
    "Patients Waiting Over 4 Hours for Admission",
    "Number of patients spending more than 4 hours from decision to admit to admission",
    "Delayed 4 hours"
])

    if None in [period_col, attendances_col, admissions_col, delay_col]:
        raise KeyError(f"Missing columns. Available columns are: {list(df.columns)}")

    df = df.rename(columns={
        period_col: "Period",
        attendances_col: "Total Attendances",
        admissions_col: "Total Emergency Admissions",
        delay_col: "Patients Waiting Over 4 Hours for Admission"
    })

    df["Period"] = pd.to_datetime(df["Period"], errors="coerce")

    numeric_columns = [
        "Total Attendances",
        "Total Emergency Admissions",
        "Patients Waiting Over 4 Hours for Admission"
    ]
    for column in numeric_columns:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    df = df.dropna(subset=["Period"] + numeric_columns).sort_values("Period").reset_index(drop=True)

    df["Occupancy Rate"] = pd.NA

    if BEDS_FILE.exists():
        try:
            beds = pd.read_excel(BEDS_FILE, sheet_name="Timeseries all acute trusts", header=12)
            beds.columns = beds.columns.astype(str).str.strip()

            beds_period_col = find_column(beds, ["Month", "Period"])
            occupancy_col = find_column(beds, ["G&A occupancy rate", "Occupancy Rate"])

            if beds_period_col and occupancy_col:
                beds = beds[[beds_period_col, occupancy_col]].rename(columns={
                    beds_period_col: "Period",
                    occupancy_col: "Occupancy Rate"
                })
                beds["Period"] = pd.to_datetime(beds["Period"], format="%B %Y", errors="coerce")
                beds["Occupancy Rate"] = pd.to_numeric(beds["Occupancy Rate"], errors="coerce")
                beds = beds.dropna()
                df = df.merge(beds, on="Period", how="left")
                print("Beds data merged successfully.")

        except Exception as error:
            print(f"Could not load beds data: {error}")

    score_map = {
        "Attendances Score": "Total Attendances",
        "Admissions Score": "Total Emergency Admissions",
        "Delay Score": "Patients Waiting Over 4 Hours for Admission"
    }

    score_parts = []
    for score_name, source_column in score_map.items():
        df[score_name] = scale_values(df[source_column])
        score_parts.append(df[score_name])

    if df["Occupancy Rate"].notna().any():
        df["Occupancy Score"] = scale_values(df["Occupancy Rate"].fillna(df["Occupancy Rate"].mean()))
        score_parts.append(df["Occupancy Score"])

    df["Pressure Score"] = sum(score_parts) / len(score_parts)

    columns_to_keep = [
        "Period",
        "Total Attendances",
        "Total Emergency Admissions",
        "Patients Waiting Over 4 Hours for Admission",
        "Pressure Score",
        "Occupancy Rate"
    ]

    df[columns_to_keep].to_csv(OUTPUT_FILE, index=False)
    print(f"Saved {len(df)} rows to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()