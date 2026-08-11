"""
Tests for population preprocessing.
"""

from hermes.preprocessing import prepare_population


def test_prepare_population_columns(raw_population):
    prepared = prepare_population(raw_population)

    assert list(prepared.columns) == [
        "insee_code",
        "population",
    ]


def test_prepare_population_key_unique(raw_population):
    prepared = prepare_population(raw_population)

    assert prepared["insee_code"].is_unique


def test_prepare_population_padding(raw_population):
    prepared = prepare_population(raw_population)

    assert prepared["insee_code"].iloc[0] == "01001"


def test_prepare_population_value(raw_population):
    prepared = prepare_population(raw_population)

    assert prepared["population"].iloc[0] == 1000


def test_prepare_population_filters_invalid_year(raw_population):
    raw_population.loc[0, "TIME_PERIOD"] = 2022

    prepared = prepare_population(raw_population)

    assert prepared.empty


def test_prepare_population_filters_invalid_status(raw_population):
    raw_population.loc[0, "OBS_STATUS"] = "E"

    prepared = prepare_population(raw_population)

    assert prepared.empty