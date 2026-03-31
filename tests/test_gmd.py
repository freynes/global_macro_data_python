import importlib

import pandas as pd
import pytest

from global_macro_data import (
    VALID_VARIABLES,
    get_available_versions,
    get_current_version,
    gmd,
    list_countries,
    list_variables,
)

gmd_module = importlib.import_module("global_macro_data.gmd")
GMDCommandError = gmd_module.GMDCommandError


def test_get_available_versions():
    versions = get_available_versions()
    assert isinstance(versions, list)
    assert len(versions) > 0
    assert "2025_12" in versions


def test_get_current_version():
    assert get_current_version() == get_available_versions()[0]


def test_list_variables(capsys):
    list_variables()
    out = capsys.readouterr().out
    assert "Available variables:" in out
    assert "Definition" in out
    assert "nGDP" in out


def test_list_countries(capsys):
    list_countries()
    out = capsys.readouterr().out
    assert "Available countries:" in out
    assert "ISO3 code" in out


def test_gmd_default(capsys):
    df = gmd()
    out = capsys.readouterr().out
    assert isinstance(df, pd.DataFrame)
    assert len(df) > 0
    assert {"countryname", "ISO3", "id", "year"}.issubset(df.columns)
    assert "Global Macro Database by Müller, Xu, Lehbib, and Chen (2025)" in out
    assert 'Website: {browse "https://www.globalmacrodata.com"}' in out


def test_gmd_version_and_country_filters():
    df = gmd(version="2025_12", country=["USA", "CHN"])
    assert isinstance(df, pd.DataFrame)
    assert set(df["ISO3"].unique()) == {"USA", "CHN"}


def test_gmd_variables_keep_order():
    df = gmd(variables=["rGDP", "infl"], version="2025_12")
    assert list(df.columns) == ["ISO3", "year", "id", "countryname", "rGDP", "infl"]


def test_gmd_raw(capsys):
    df = gmd(variables="rGDP", raw=True, version="2025_12")
    out = capsys.readouterr().out
    assert isinstance(df, pd.DataFrame)
    assert "Loaded raw data on rGDP" in out
    assert "rGDP" in df.columns


def test_gmd_vars_and_country_load():
    var_df = gmd(vars="load")
    cty_df = gmd(country="load")
    assert isinstance(var_df, pd.DataFrame)
    assert {"variables", "units", "definition"}.issubset(var_df.columns)
    assert isinstance(cty_df, pd.DataFrame)
    assert "ISO3" in cty_df.columns


def test_gmd_vars_list_follows_stata_column_expectation(capsys):
    var_df = gmd(vars="load")
    if "variable" in var_df.columns:
        result = gmd(vars="list")
        out = capsys.readouterr().out
        assert result is None
        assert "Available variables:" in out
    else:
        with pytest.raises(GMDCommandError) as exc:
            gmd(vars="list")
        assert exc.value.code == 111


def test_gmd_sources_load_and_list(capsys):
    source_df = gmd(sources="load")
    out = capsys.readouterr().out
    assert isinstance(source_df, pd.DataFrame)
    assert "source_name" in source_df.columns
    assert "Imported the list of sources." in out

    result = gmd(sources="list")
    out = capsys.readouterr().out
    assert result is None
    assert "IMF_IFS" in out


def test_gmd_sources_list_is_sorted(capsys):
    gmd(sources="list")
    out = capsys.readouterr().out
    lines = [line.strip() for line in out.splitlines() if line.strip()]
    assert lines == sorted(lines)


def test_gmd_sources_specific_query():
    df = gmd(sources="IMF_IFS", variables="rGDP", country="USA", version="2025_12")
    assert isinstance(df, pd.DataFrame)
    assert len(df) > 0
    assert "IMF_IFS_rGDP" in df.columns


def test_gmd_sources_specific_invalid_variable_exits_without_error(capsys):
    result = gmd(sources="IMF_IFS", variables="NOT_A_VAR", version="2025_12")
    out = capsys.readouterr().out
    assert result is None
    assert "This source doesn't have data on NOT_A_VAR." in out


def test_gmd_sources_specific_invalid_country_returns_empty():
    df = gmd(sources="IMF_IFS", variables="rGDP", country="XXX", version="2025_12")
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 0


def test_gmd_sources_cs_alias():
    df = gmd(sources="CS1_ARG", version="2025_12")
    assert isinstance(df, pd.DataFrame)
    assert len(df) > 0


def test_gmd_sources_cs_alias_rewrite_matches_stata_string_logic():
    assert gmd_module._normalize_source_name("CS1_ARG") == "ARG_1"
    assert gmd_module._normalize_source_name("CS1_arg") == "arg_1"


def test_gmd_cite_load_and_key(capsys):
    bib_df = gmd(cite="load")
    assert isinstance(bib_df, pd.DataFrame)
    assert "citation" in bib_df.columns

    if "source" in bib_df.columns:
        result = gmd(cite="GMD")
        out = capsys.readouterr().out
        assert result is None
        assert "@techreport" in out
    else:
        with pytest.raises(GMDCommandError) as exc:
            gmd(cite="GMD")
        assert exc.value.code == 111


def test_gmd_version_list_and_print(capsys):
    result = gmd(version="list")
    out = capsys.readouterr().out
    assert result is None
    assert "2025_12" in out

    result = gmd(print_option="GMD")
    out = capsys.readouterr().out
    assert result is None
    assert "Müller, K., Xu, C., Lehbib, M., & Chen, Z. (2025)." in out


def test_gmd_version_list_is_sorted(capsys):
    gmd(version="list")
    out = capsys.readouterr().out
    lines = [line.strip() for line in out.splitlines() if line.strip()]
    assert lines == sorted(lines)


def test_gmd_version_current_uses_latest(capsys):
    gmd(version="current")
    out = capsys.readouterr().out
    assert f"Current version: {get_current_version()}" in out


def test_gmd_network_yes_loads_data():
    df = gmd(version="2025_12", network="yes")
    assert isinstance(df, pd.DataFrame)
    assert len(df) > 0


def test_gmd_fast_yes_saves_cache_files(tmp_path, monkeypatch):
    monkeypatch.setattr(gmd_module, "_CACHE_DIR", tmp_path / "gmd_cache")
    df = gmd(version="2025_12", fast="yes")
    assert isinstance(df, pd.DataFrame)
    assert (gmd_module._CACHE_DIR / "GMD_2025_12.dta").exists()
    assert (gmd_module._CACHE_DIR / "GMD.dta").exists()


def test_gmd_print_keyword_alias(capsys):
    result = gmd(**{"print": "Stata"})
    out = capsys.readouterr().out
    assert result is None
    assert "Lehbib, M. & Müller, K. (2025)." in out


def test_gmd_invalid_print_option():
    with pytest.raises(GMDCommandError):
        gmd(print_option="bad")


def test_gmd_invalid_version(capsys):
    with pytest.raises(GMDCommandError) as exc:
        gmd(version="invalid_version")
    out = capsys.readouterr().out
    assert "Error: Version invalid_version does not exist" in out
    assert "Available versions:" in str(exc.value)


def test_gmd_invalid_version_multiple_tokens_exits_without_error(capsys):
    result = gmd(version="2025_12 current")
    out = capsys.readouterr().out
    assert result is None
    assert "Version must either be one specific version" in out


def test_gmd_invalid_country():
    with pytest.raises(GMDCommandError):
        gmd(country="INVALID", version="2025_12")


def test_gmd_invalid_country_mixed_returns_partial_in_exception():
    with pytest.raises(GMDCommandError) as exc:
        gmd(country=["USA", "INVALID"], version="2025_12")
    assert exc.value.code == 498
    assert isinstance(exc.value.data, pd.DataFrame)
    assert set(exc.value.data["ISO3"].unique()) == {"USA"}


def test_gmd_invalid_variable():
    with pytest.raises(GMDCommandError):
        gmd(variables="INVALID", version="2025_12")


def test_gmd_raw_multiple_variables():
    with pytest.raises(GMDCommandError):
        gmd(variables=["rGDP", "infl"], raw=True, version="2025_12")


def test_gmd_raw_fallback_uses_stata_column_check(monkeypatch):
    original_read_csv_primary = gmd_module._read_csv_primary

    def _fake_read_csv_primary(path, **kwargs):
        if path.startswith("distribute/"):
            raise RuntimeError("forced failure")
        return original_read_csv_primary(path, **kwargs)

    def _fake_varlist_df():
        return pd.DataFrame(
            {
                "variables": ["rGDP", "infl"],
                "units": ["in LC", "in %"],
                "definition": ["Real GDP", "Inflation"],
            }
        )

    monkeypatch.setattr(gmd_module, "_read_csv_primary", _fake_read_csv_primary)
    monkeypatch.setattr(gmd_module, "_varlist_df", _fake_varlist_df)

    with pytest.raises(GMDCommandError) as exc:
        gmd(variables="rGDP", raw=True, version="2025_12")
    assert str(exc.value) == "Specified variable is not valid."


def test_gmd_variables_with_identifying_var_keeps_unique_columns():
    df = gmd(variables=["year", "rGDP"], version="2025_12")
    assert isinstance(df, pd.DataFrame)
    assert df.columns.tolist().count("year") == 1
    assert "rGDP" in df.columns


def test_gmd_raw_no_variable():
    with pytest.raises(GMDCommandError):
        gmd(raw=True, version="2025_12")


def test_summary_contains_stata_citation_lines(capsys):
    gmd(variables="rGDP", version="2025_12")
    out = capsys.readouterr().out
    assert "When using these data, please cite:" in out
    assert "{stata gmd, cite(GMD):[BibTeX code]}" in out
    assert "When using the gmd Stata command, please further cite:" in out


def test_valid_variables_contains_stata_additions():
    assert "cgovdebt" in VALID_VARIABLES
    assert "gen_govtax_GDP" in VALID_VARIABLES


def test_country_list_fast_yes_prints_when_cache_is_empty(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(gmd_module, "_CACHE_DIR", tmp_path / "gmd_cache")
    result = gmd(country="list", fast="yes")
    out = capsys.readouterr().out
    assert result is None
    assert "Saving countrylist dataframe locally" in out
    assert "Available countries:" in out
