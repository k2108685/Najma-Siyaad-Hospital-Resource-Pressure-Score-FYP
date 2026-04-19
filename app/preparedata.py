from pathlib import Path
import pandas as pd


BASE_DIR = Path(__file__).resolve().parent

AE_FILE = BASE_DIR / "data" / "raw" / "aemonthly.xls"
BEDS_FILE = BASE_DIR / "data" / "raw" / "Beds-publication-Timeseries-March-2020-February-2026.xlsx"
OUTPUT_FILE = BASE_DIR / "data" / "processed" / "ae_pressure_with_score.csv"

#Converting indicator to a 0-1 scale
def scale_values(series):
    series = pd.to_numeric(series, errors="coerce")
    minimum = series.min()
    maximum = series.max()

    if pd.isna(minimum) or pd.isna(maximum) or minimum == maximum:
        return pd.Series([0.0] * len(series), index=series.index)

    return (series - minimum) / (maximum - minimum)

#checks for a list of possible names 

def find_column(df, candidates):
    for column in candidates:
        if column in df.columns:
            return column
    return None


def main():
    print("Loading A&E data...")
#Load the A&E file and identify the columns needed
    df = pd.read_excel(AE_FILE, header=13)
    df.columns = df.columns.str.strip()

    period_col = find_column(df, ["Period", "Date", "Month"])
    attendances_col = find_column(df, ["Total Attendances"])
    admissions_col = find_column(df, [
        "Total Emergency Admissions",
        "Total Emergency Admissions via A&E"
    ])
    delay_col = find_column(df, [
        "Patients Waiting Over 4 Hours for Admission",
        "Number of patients spending >4 hours from decision to admit to admission"
    ])
    four_hour_col = find_column(df, [
        "Percentage of Patients Seen Within 4 Hours",
        "Operational standard (Performance)",
        "% within 4 hours",
        "4 hour performance"
    ])
    #Stops if some columns are missing 
    if None in [period_col, attendances_col, admissions_col, delay_col]:
        raise KeyError(f"Missing columns. Available columns are: {list(df.columns)}")

    rename_map = {
        period_col: "Period",
        attendances_col: "Total Attendances",
        admissions_col: "Total Emergency Admissions",
        delay_col: "Patients Waiting Over 4 Hours for Admission"
    }

    if four_hour_col:
        rename_map[four_hour_col] = "Percentage of Patients Seen Within 4 Hours"

    df = df.rename(columns=rename_map)
    #converts dates into the right data types
    df["Period"] = pd.to_datetime(df["Period"], errors="coerce")
    df["Total Attendances"] = pd.to_numeric(df["Total Attendances"], errors="coerce")
    df["Total Emergency Admissions"] = pd.to_numeric(df["Total Emergency Admissions"], errors="coerce")
    df["Patients Waiting Over 4 Hours for Admission"] = pd.to_numeric(
        df["Patients Waiting Over 4 Hours for Admission"], errors="coerce"
    )

    if "Percentage of Patients Seen Within 4 Hours" in df.columns:
        df["Percentage of Patients Seen Within 4 Hours"] = pd.to_numeric(
            df["Percentage of Patients Seen Within 4 Hours"], errors="coerce"
        )

    df = df.dropna(subset=[
        "Period",
        "Total Attendances",
        "Total Emergency Admissions",
        "Patients Waiting Over 4 Hours for Admission"
    ]).sort_values("Period").reset_index(drop=True)
    #Load bed occupancy data and merge it with the a&e data
    if BEDS_FILE.exists():
        try:
            beds = pd.read_excel(
                BEDS_FILE,
                sheet_name="Timeseries all acute trusts",
                header=12
            )

            beds.columns = [str(col).strip() for col in beds.columns]

            beds_period = find_column(beds, ["Month", "Period"])
            occupancy = find_column(beds, ["G&A occupancy rate", "Occupancy Rate"])

            if beds_period and occupancy:
                beds = beds[[beds_period, occupancy]].rename(columns={
                    beds_period: "Period",
                    occupancy: "Occupancy Rate"
                })

                beds["Period"] = pd.to_datetime(beds["Period"], format="%B %Y", errors="coerce")
                beds["Occupancy Rate"] = pd.to_numeric(beds["Occupancy Rate"], errors="coerce")
                beds = beds.dropna()

                df = pd.merge(df, beds, on="Period", how="left")
                print("Beds data merged")

        except Exception as e:
            print(f"Could not load beds data: {e}")
            
    df["Attendances Score"] = scale_values(df["Total Attendances"])
    df["Admissions Score"] = scale_values(df["Total Emergency Admissions"])
    df["Delay Score"] = scale_values(df["Patients Waiting Over 4 Hours for Admission"])

    if "Percentage of Patients Seen Within 4 Hours" in df.columns:
        df["Four Hour Score"] = 1 - scale_values(
            df["Percentage of Patients Seen Within 4 Hours"]
        )
#combine all the scores into a single pressure score 
    score_parts = [
        df["Attendances Score"],
        df["Admissions Score"],
        df["Delay Score"]
    ]

    if "Percentage of Patients Seen Within 4 Hours" in df.columns:
        if df["Percentage of Patients Seen Within 4 Hours"].nunique(dropna=True) > 1:
            score_parts.append(df["Four Hour Score"])

    if "Occupancy Rate" in df.columns and df["Occupancy Rate"].notna().any():
        df["Occupancy Score"] = scale_values(
            df["Occupancy Rate"].fillna(df["Occupancy Rate"].mean())
        )
        score_parts.append(df["Occupancy Score"])

    df["Pressure Score"] = sum(score_parts) / len(score_parts)
    #saves the cleaned columns 
    columns_to_keep = [
        "Period",
        "Total Attendances",
        "Total Emergency Admissions",
        "Patients Waiting Over 4 Hours for Admission",
        "Pressure Score"
    ]

    if "Percentage of Patients Seen Within 4 Hours" in df.columns:
        columns_to_keep.append("Percentage of Patients Seen Within 4 Hours")

    if "Occupancy Rate" in df.columns:
        columns_to_keep.append("Occupancy Rate")

    df[columns_to_keep].to_csv(OUTPUT_FILE, index=False)

    print(f"Saved {len(df)} rows to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()