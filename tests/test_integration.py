"""
Tests for municipality integration.
"""

import pandas as pd

from hermes.integration import build_municipality_table


def test_build_municipality_table():

    population = pd.DataFrame(
        {
            "insee_code": ["01001"],
            "population": [1000],
        }
    )

    employment = pd.DataFrame(
        {
            "insee_code": ["01001"],
            "employed": [450],
        }
    )

    workplace = pd.DataFrame(
        {
            "insee_code": ["01001"],
            "total_jobs": [500],
        }
    )

    boundaries = pd.DataFrame(
        {
            "insee_code": ["01001"],
            "municipality": ["Commune"],
            "department_code": ["01"],
            "region_code": ["84"],
            "geometry": [None],
        }
    )

    topography = pd.DataFrame(
        {
            "insee_code": ["01001"],
            "area_hectares": [500],
            "mean_elevation": [250],
            "min_elevation": [200],
            "max_elevation": [300],
            "latitude": [46.1],
            "longitude": [5.1],
        }
    )

    municipality = build_municipality_table(
        population=population,
        employment=employment,
        workplace_employment=workplace,
        municipality_boundaries=boundaries,
        topography=topography,
    )

    assert municipality.shape[0] == 1
    assert municipality["insee_code"].is_unique

    assert "population" in municipality.columns
    assert "employed" in municipality.columns
    assert "total_jobs" in municipality.columns
    assert "area_hectares" in municipality.columns