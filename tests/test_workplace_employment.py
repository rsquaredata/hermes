"""
Tests for workplace employment preprocessing.
"""

import pandas as pd

from hermes.preprocessing import prepare_workplace_employment


def test_prepare_workplace_values(raw_workplace_employment):
    prepared = prepare_workplace_employment(
        raw_workplace_employment
    )

    row = prepared.iloc[0]

    assert row["total_jobs"] == 100
    assert row["salaried_jobs"] == 80
    assert row["self_employed_jobs"] == 20
    assert row["full_time_jobs"] == 75
    assert row["part_time_jobs"] == 25
