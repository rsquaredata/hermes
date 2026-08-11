"""
Tests for employment preprocessing.
"""

import pandas as pd

from hermes.preprocessing import prepare_employment


def test_prepare_employment_columns(raw_employment):
    prepared = prepare_employment(raw_employment)

    assert list(prepared.columns) == [
        "insee_code",
        "population_15_64",
        "active_population",
        "employed",
        "unemployed",
        "inactive",
        "students",
        "retired",
        "homemakers",
        "other_inactive",
    ]


def test_prepare_employment_values(raw_employment):
    prepared = prepare_employment(raw_employment)

    row = prepared.iloc[0]

    assert row["population_15_64"] == 100
    assert row["active_population"] == 60
    assert row["employed"] == 55
    assert row["unemployed"] == 5