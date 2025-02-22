import os
import requests
import pandas as pd
import pycountry

# Allowed quarters
VALID_QUARTERS = ["01", "03", "06", "09", "12"]

# Generate a complete ISO3 country code dictionary
COUNTRIES = {country.alpha_3: country.name for country in pycountry.countries}

def GMD(year=None, quarter=None, country=None):
    """
    Download and filter Global Macro Data.
    
    Parameters:
    - year (int): The desired year (e.g., 2025). If None, the latest dataset is used.
    - quarter (int): The quarter (1, 3, 6, 9, 12). If None, the latest dataset is used.
    - country (str): ISO3 country code (e.g., "CHN"). If None, returns all countries.
    
    Returns:
    - pd.DataFrame: The requested data.
    """
    base_url = "https://www.globalmacrodata.com"

    # Automatically select the latest available dataset
    if year is None or quarter is None:
        year, quarter = find_latest_data(base_url)

    # Ensure year and quarter are properly formatted
    if not (2020 <= year <= 2050):
        raise ValueError("Year must be between 2020 and 2050.")
    
    quarter = f"{quarter:02d}"  # Ensure two-digit format
    if quarter not in VALID_QUARTERS:
        raise ValueError("Quarter must be one of 1, 3, 6, 9, 12.")

    # Construct URL
    data_url = f"{base_url}/GMD_{year}_{quarter}.csv"
    print(f"Downloading: {data_url}")

    # Download data
    response = requests.get(data_url)
    if response.status_code != 200:
        raise FileNotFoundError(f"Error: Data file not found at {data_url}")

    # Read the data
    df = pd.read_csv(pd.compat.StringIO(response.text))

    # Ensure the required columns exist
    required_columns = ["year", "ISO3", "countryname"]
    if not all(col in df.columns for col in required_columns):
        raise ValueError("Required columns are missing in the dataset.")

    # Filter by country
    if country:
        country = country.upper()
        if country not in df["ISO3"].unique():
            raise ValueError(f"Invalid country code: {country}")
        df = df[df["ISO3"] == country]
        print(f"Filtered data for country: {COUNTRIES.get(country, country)}")

    print(f"Final dataset: {len(df)} observations of {len(df.columns)} variables")
    return df

def find_latest_data(base_url):
    """ Attempt to find the most recent available dataset """
    import datetime

    current_year = datetime.datetime.now().year
    for year in range(current_year, 2019, -1):  # Iterate backward by year
        for quarter in ["12", "09", "06", "03", "01"]:
            url = f"{base_url}/GMD_{year}_{quarter}.csv"
            if requests.head(url).status_code == 200:
                return year, int(quarter)
    
    raise FileNotFoundError("No available dataset found on the server.")
