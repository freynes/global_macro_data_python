import os
import requests
import pandas as pd
import pycountry

# Allowed quarters
VALID_QUARTERS = ["01", "03", "06", "09", "12"]

# Generate a complete ISO3 country code dictionary
COUNTRIES = {country.alpha_3: country.name for country in pycountry.countries}

from .gmd import GMD, find_latest_data

__all__ = ["GMD", "find_latest_data", "VALID_QUARTERS", "COUNTRIES"]
