import os
import pandas as pd
from fredapi import Fred

# load API key
fred_api_key = os.getenv("FRED_API_KEY")
fred = Fred(api_key=fred_api_key)

# define Start Date
start_date = "2020-01-01"

# define series and categories
data_series = {
    "Labor": {
        "series": ["UNRATE", "UNEMPLOY", "JTSJOL", "JTSQUL", "JTU5100JOL",
                   "JTU5200JOL", "JTS540099JOL", "JTU5100QUL", "JTU5200QUL", 
                   "JTS540099QUL", "LNU04032237", "LNU04032238", "LNU04032239", 
                   "FRBATLWGT12MMUMHGO", "FRBATLWGT12MMUMHWGJST", "FRBATLWGT12MMUMHWGJSW"],
        "names": ["US Unemployment Rate", "US Unemployment Level", "US Job Openings", 
                  "US Voluntary Separations (Quits)", "US Job Openings (Information)", 
                  "US Job Openings (Finance and Insurance)", "US Job Openings (Professional and Business Services)", 
                  "Quits (Information)", "Quits (Finance and Insurance)", "Quits (Professional and Business Services)", 
                  "Unemployment Rate (Information)", "Unemployment Rate (Finance and Insurance)", 
                  "Unemployment Rate (Professional and Business Services)", 
                  "12-Month Moving Average of Unweighted Median Hourly Wate Growth (Overall)",
                  "12-Month Moving Average of Unweighted Median Hourly Wage Growth (Stayer)",
                  "12-Month Moving Average of Unweighted Median Hourly Wate Growth (Switcher)"]
    },
    "Treasury": {
        "series": ["DGS10"],
        "names": ["10-Year Treasury Yields"]
    },
    "Risk": {
        "series": ["BAMLHYH0A0HYM2TRIV", "VIXCLS", "STLFSI4", "NFCI"],
        "names": ["ICE BofA US High Yield Index Total Return Index Value", "CBOE Volatility Index VIX",
                  "St Louis Fed Financial Stress Index", "Chicago Fed National Financial Conditions Index"]
    },
    "Econ": {
        "series": ["FEDFUNDS", "T10Y2Y", "MORTGAGE30US", "CPALTT01USM657N", "PPIACO", "A191RL1Q225SBEA"],
        "names": ["Federal Funds Effective Rate", 
                  "10-Year Treasury Constant Maturity Minus 2-Year Treasury Constant Maturity", 
                  "30-Year Fixed Rate Mortgage Average in the United States", 
                  "Consumer Price Index: All Items: Total for United States",
                  "Producer Price Index by Commodity: All Commodities", 
                  "Real Gross Domestic Product"]
    }
}

# fetch data from FRED
df = pd.DataFrame()

for category, details in data_series.items():
    for series, name in zip(details["series"], details["names"]):
        temp_data = fred.get_series(series, observation_start=start_date)
        temp_data = temp_data.to_frame(name)
        df = pd.merge(df, temp_data, left_index=True, right_index=True, how="outer")

# reset index to have 'Date' as a column
df.reset_index(inplace=True)
df.rename(columns={"index": "Date"}, inplace=True)

# transform data
multipliers = {
    "US Unemployment Level": 1000, "US Job Openings": 1000, "US Voluntary Separations (Quits)": 1000,
    "US Job Openings (Information)": 1000, "US Job Openings (Finance and Insurance)": 1000,
    "US Job Openings (Professional and Business Services)": 1000, "Quits (Information)": 1000,
    "Quits (Finance and Insurance)": 1000, "Quits (Professional and Business Services)": 1000
}
percentages = [
    "US Unemployment Rate", "Unemployment Rate (Information)", "Unemployment Rate (Finance and Insurance)",
    "Unemployment Rate (Professional and Business Services)", 
    "12-Month Moving Average of Unweighted Median Hourly Wate Growth (Overall)",
    "12-Month Moving Average of Unweighted Median Hourly Wage Growth (Stayer)",
    "12-Month Moving Average of Unweighted Median Hourly Wate Growth (Switcher)",
    "10-Year Treasury Yields"
]

# apply multipliers
for col, multiplier in multipliers.items():
    if col in df.columns:
        df[col] *= multiplier

# apply percentage conversions
for col in percentages:
    if col in df.columns:
        df[col] /= 100

# write dataframe to csv
df.to_csv("fred_consolidated_data.csv", index=False)
print("Saved consolidated data.")
