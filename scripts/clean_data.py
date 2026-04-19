import pandas as pd
import numpy as np
import os
import re

ROOT     = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR  = os.path.join(ROOT, "data", "raw")
PROC_DIR = os.path.join(ROOT, "data", "processed")
os.makedirs(PROC_DIR, exist_ok=True)

XLS_FILE = os.path.join(RAW_DIR, "Monthly-AE-Time-Series-February-2026.xls")
CSV_FILE = os.path.join(RAW_DIR, "February-2026-AE-by-provider.csv")


def clean_numeric(series):
    if pd.api.types.is_numeric_dtype(series):
        return series.round(0).astype("Int64")
    else:
        return (
            series
            .astype(str)
            .str.replace(",", "", regex=False)
            .str.strip()
            .replace("", np.nan)
            .replace("nan", np.nan)
            .replace("-", np.nan)
            .pipe(pd.to_numeric, errors="coerce")
            .round(0)
            .astype("Int64")
        )


def snake_case(col):
    col = col.lower()
    col = col.replace("&", "and")
    col = re.sub(r"[^a-z0-9]+", "_", col)
    col = re.sub(r"_+", "_", col)
    col = col.strip("_")
    return col


# -- Activity sheet -----------------------------------------------------------

print("=" * 60)
print("Processing: Monthly A&E Time Series -- Activity sheet")
print("=" * 60)

df_activity = pd.read_excel(
    XLS_FILE,
    sheet_name="Activity",
    header=13,
    usecols="B:J",
    engine="xlrd"
)

df_activity = df_activity.dropna(how="all")

print("Rows loaded (before cleaning): {}".format(len(df_activity)))
print("Columns: {}".format(list(df_activity.columns)))

activity_rename = {
    "Period":                                           "period",
    "Type 1 Departments - Major A&E":                   "type1_attendances",
    "Type 2 Departments - Single Specialty":             "type2_attendances",
    "Type 3 Departments - Other A&E/Minor Injury Unit":  "type3_attendances",
    "Total Attendances":                                "total_attendances",
    "Emergency Admissions via Type 1 A&E":              "emerg_admissions_type1",
    "Emergency Admissions via Type 2 A&E":              "emerg_admissions_type2",
    "Emergency Admissions via Type 3 and 4 A&E":        "emerg_admissions_type3",
    "Total Emergency Admissions via A&E":               "total_emerg_admissions",
}
df_activity = df_activity.rename(columns=activity_rename)

df_activity["period"] = pd.to_datetime(df_activity["period"], format="%b-%y")

numeric_cols = [c for c in df_activity.columns if c != "period"]
for col in numeric_cols:
    df_activity[col] = clean_numeric(df_activity[col])

df_activity = df_activity.sort_values("period").reset_index(drop=True)

print("\nDate range: {} -> {}".format(
    df_activity["period"].min().strftime("%b %Y"),
    df_activity["period"].max().strftime("%b %Y")
))
print("Rows after cleaning: {}".format(len(df_activity)))
print("\nSample rows:")
print(df_activity.head(3).to_string())
print("\nNull counts:")
print(df_activity.isnull().sum().to_string())


# -- Performance sheet --------------------------------------------------------

print("\n" + "=" * 60)
print("Processing: Monthly A&E Time Series -- Performance sheet")
print("=" * 60)

df_perf = pd.read_excel(
    XLS_FILE,
    sheet_name="Performance",
    header=13,
    usecols="B:K",
    engine="xlrd"
)

df_perf = df_perf.dropna(how="all")
print("Rows loaded: {}".format(len(df_perf)))
print("Columns: {}".format(list(df_perf.columns)))

perf_rename = {
    "Period":                                                  "period",
    "Type 1 Departments - Major A&E":                          "type1_within_4hrs",
    "Type 2 Departments - Single Specialty":                   "type2_within_4hrs",
    "Type 3 Departments - Other A&E/Minor Injury Unit":        "type3_within_4hrs",
    "Total Attendances < 4 hours":                             "total_within_4hrs",
    "Type 1 Departments - Major A&E.1":                        "type1_over_4hrs",
    "Type 2 Departments - Single Specialty.1":                 "type2_over_4hrs",
    "Type 3 Departments - Other A&E/Minor Injury Unit.1":      "type3_over_4hrs",
    "Total Attendances > 4 hours":                             "total_over_4hrs",
}

df_perf = df_perf.rename(columns=perf_rename)
keep_cols = [c for c in df_perf.columns if c in perf_rename.values()]
df_perf = df_perf[keep_cols]

df_perf["period"] = pd.to_datetime(df_perf["period"], format="%b-%y")

numeric_cols = [c for c in df_perf.columns if c != "period"]
for col in numeric_cols:
    df_perf[col] = clean_numeric(df_perf[col])

df_perf["total_all"] = df_perf["total_within_4hrs"] + df_perf["total_over_4hrs"]
df_perf["pct_within_4hrs"] = (
    df_perf["total_within_4hrs"] / df_perf["total_all"] * 100
).round(1)

df_perf = df_perf.sort_values("period").reset_index(drop=True)

print("\nDate range: {} -> {}".format(
    df_perf["period"].min().strftime("%b %Y"),
    df_perf["period"].max().strftime("%b %Y")
))
print("Rows after cleaning: {}".format(len(df_perf)))
print("\n4-hour performance range: {}% -- {}%".format(
    df_perf["pct_within_4hrs"].min(),
    df_perf["pct_within_4hrs"].max()
))
print("Most recent month: {} -> {}%".format(
    df_perf.iloc[-1]["period"].strftime("%b %Y"),
    df_perf.iloc[-1]["pct_within_4hrs"]
))


# -- Provider CSV (February 2026) ---------------------------------------------

print("\n" + "=" * 60)
print("Processing: February 2026 -- Provider-level CSV")
print("=" * 60)

df_provider = pd.read_csv(CSV_FILE)
print("Rows loaded: {}".format(len(df_provider)))
print("Columns: {}".format(list(df_provider.columns)))

# Standardise column names
df_provider.columns = [snake_case(c) for c in df_provider.columns]
print("\nRenamed columns: {}".format(list(df_provider.columns)))

df_provider["period"] = (
    df_provider["period"]
    .str.replace("MSitAE-", "", regex=False)
    .str.title()
)
df_provider["period"] = pd.to_datetime(df_provider["period"], format="%B-%Y")

text_cols = {"period", "org_code", "parent_org", "org_name"}
numeric_cols = [c for c in df_provider.columns if c not in text_cols]

for col in numeric_cols:
    df_provider[col] = df_provider[col].replace("-", np.nan)
    df_provider[col] = clean_numeric(df_provider[col])

df_provider["type1_total_attendances"] = (
    df_provider["aande_attendances_type_1"].fillna(0) +
    df_provider["aande_attendances_booked_appointments_type_1"].fillna(0)
).astype("Int64")

df_provider["type1_total_over_4hrs"] = (
    df_provider["attendances_over_4hrs_type_1"].fillna(0) +
    df_provider["attendances_over_4hrs_booked_appointments_type_1"].fillna(0)
).astype("Int64")

df_provider["type1_pct_within_4hrs"] = (
    (df_provider["type1_total_attendances"] - df_provider["type1_total_over_4hrs"])
    / df_provider["type1_total_attendances"] * 100
).round(1)

mask_zero = df_provider["type1_total_attendances"] == 0
df_provider.loc[mask_zero, "type1_pct_within_4hrs"] = np.nan

print("\nNull counts per column:")
print(df_provider.isnull().sum().to_string())

df_provider_type1 = df_provider[
    df_provider["type1_total_attendances"] > 0
].copy().reset_index(drop=True)

print("\nAll providers: {}".format(len(df_provider)))
print("Type 1 providers: {}".format(len(df_provider_type1)))

if len(df_provider_type1) > 0:
    print("\nType 1 performance range: {}% -- {}%".format(
        df_provider_type1["type1_pct_within_4hrs"].min(),
        df_provider_type1["type1_pct_within_4hrs"].max()
    ))
    print("Mean 4-hour performance: {:.1f}%".format(
        df_provider_type1["type1_pct_within_4hrs"].mean()
    ))


# -- Save ---------------------------------------------------------------------

print("\n" + "=" * 60)
print("Saving cleaned files to data/processed/")
print("=" * 60)

df_activity["period"] = df_activity["period"].dt.strftime("%Y-%m-%d")
df_perf["period"] = df_perf["period"].dt.strftime("%Y-%m-%d")
df_provider["period"] = df_provider["period"].dt.strftime("%Y-%m-%d")
df_provider_type1["period"] = df_provider_type1["period"].dt.strftime("%Y-%m-%d")

out_activity = os.path.join(PROC_DIR, "ae_timeseries_activity.csv")
out_perf     = os.path.join(PROC_DIR, "ae_timeseries_performance.csv")
out_provider = os.path.join(PROC_DIR, "ae_provider_feb2026.csv")
out_type1    = os.path.join(PROC_DIR, "ae_provider_type1_feb2026.csv")

df_activity.to_csv(out_activity, index=False)
df_perf.to_csv(out_perf, index=False)
df_provider.to_csv(out_provider, index=False)
df_provider_type1.to_csv(out_type1, index=False)

print("  ae_timeseries_activity.csv     -> {} rows".format(len(df_activity)))
print("  ae_timeseries_performance.csv  -> {} rows".format(len(df_perf)))
print("  ae_provider_feb2026.csv        -> {} rows".format(len(df_provider)))
print("  ae_provider_type1_feb2026.csv  -> {} rows".format(len(df_provider_type1)))
print("\nData cleaning complete.")
