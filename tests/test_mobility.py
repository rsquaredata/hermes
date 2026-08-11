"""
Tests for mobility preprocessing.
"""

import pandas as pd

from hermes.preprocessing import prepare_mobility


def test_prepare_mobility_columns(raw_mobility):
    prepared = prepare_mobility(raw_mobility)

    assert list(prepared.columns) == [
        "origin_insee",
        "origin_name",
        "destination_insee",
        "destination_name",
        "commuters",
    ]


def test_prepare_mobility_values(raw_mobility):
    prepared = prepare_mobility(raw_mobility)

    row = prepared.iloc[0]

    assert row["origin_insee"] == "01001"
    assert row["destination_insee"] == "01002"
    assert row["commuters"] == 42