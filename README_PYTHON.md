# The Global Macro Database (Python Package)

<a href="https://www.globalmacrodata.com" target="_blank" rel="noopener noreferrer">
    <img src="https://img.shields.io/badge/Website-Visit-blue?style=flat&logo=google-chrome" alt="Website Badge">
</a>

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

This package provides Python access to the Global Macro Database (GMD).

## Installation

```bash
pip install global_macro_data
```

## Stata-aligned API

The Python `gmd()` function is aligned with the Stata command options:

- `version("YYYY_MM" | "current" | "list")`
- `country("ISO3" | ["ISO3", ...] | "load" | "list")`
- `variables="var"` or `variables=[...]`
- `raw=True`
- `vars="load" | "list"`
- `sources="name" | "load" | "list"`
- `cite="key" | "load"`
- `print_option="GMD" | "Stata"`
- `fast="yes"` (cache locally)
- legacy compatibility: `iso=True`, `vars=True`

## Repository-Level Parity With Stata

This repository now mirrors the Stata repository assets as well:

- `data/clean/*`
- `data/final/*`
- `data/helpers/*`
- `code/*`
- `stata/*`
- `gmd_submission/*`
- root-level release files (`0_setup.do`, `versions.csv`, `stata.zip`, `gmd_submission.zip`, etc.)

Python equivalents of Stata helper-building scripts are provided:

- `scripts/source_list.py` (equivalent of `code/source_list.do`)
- `scripts/bib_to_df.py` (equivalent of `code/bib_to_df.do`)
- `scripts/setup_helpers.py` (equivalent of the helper branch in `0_setup.do`)
- `scripts/check_stata_parity.py` (file-level parity check against a Stata repo checkout)

Examples:

```bash
# Rebuild helper files from local data/
python scripts/setup_helpers.py

# Verify mirrored-file parity against sibling Stata repo
python scripts/check_stata_parity.py
```

## Examples

```python
from global_macro_data import gmd

# Latest dataset
full_df = gmd()

# Specific vintage
df_2025_12 = gmd(version="2025_12")

# Filter countries and variables
subset = gmd(
    version="2025_12",
    country=["USA", "CHN"],
    variables=["rGDP", "infl", "unemp"],
)

# Raw source-level data for one variable
raw_rgdp = gmd(variables="rGDP", raw=True, version="2025_12")

# Load helper tables
varlist_df = gmd(vars="load")
country_df = gmd(country="load")
source_df = gmd(sources="load")
bib_df = gmd(cite="load")

# Print citations
gmd(cite="GMD")
gmd(print_option="GMD")
```

## Citation

```bibtex
@techreport{mueller2025global,
    title = {The Global Macro Database: A New International Macroeconomic Dataset},
    author = {Mueller, Karsten and Xu, Chenzi and Lehbib, Mohamed and Chen, Ziliang},
    year = {2025},
    type = {Working Paper}
}
```
