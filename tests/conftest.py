"""
Pytest fixtures for HERMES.
"""

import pandas as pd
import pytest


# ============================================================================
# Population
# ============================================================================

@pytest.fixture
def raw_population():
    return pd.DataFrame(
        {
            "GEO_OBJECT": ["COM"],
            "TIME_PERIOD": [2023],
            "SEX": ["_T"],
            "AGE": ["_T"],
            "OBS_STATUS": ["A"],
            "GEO": ["01001"],
            "OBS_VALUE": [1000],
        }
    )


# ============================================================================
# Employment
# ============================================================================

@pytest.fixture
def raw_employment():
    return pd.DataFrame(
        {
            "GEO_OBJECT": ["COM"] * 9,
            "TIME_PERIOD": [2023] * 9,
            "SEX": ["_T"] * 9,
            "AGE": ["Y15T64"] * 9,
            "EDUC": ["_T"] * 9,
            "OBS_STATUS": ["A"] * 9,
            "GEO": ["01001"] * 9,
            "EMPSTA_ENQ": [
                "_T",
                "1T2",
                "1",
                "2",
                "3",
                "31",
                "33",
                "35",
                "36",
            ],
            "OBS_VALUE": [
                100,
                60,
                55,
                5,
                40,
                10,
                20,
                5,
                5,
            ],
        }
    )


# ============================================================================
# Workplace employment
# ============================================================================

@pytest.fixture
def raw_workplace_employment():
    return pd.DataFrame(
        {
            "GEO_OBJECT": ["COM"] * 5,
            "TIME_PERIOD": [2023] * 5,
            "OBS_STATUS": ["A"] * 5,
            "RP_MEASURE": ["NBEMP"] * 5,
            "SEX": ["_T"] * 5,
            "AGE": ["_T"] * 5,
            "EMPFORM": [
                "_T",
                "2",
                "1",
                "_T",
                "_T",
            ],
            "WKTIME": [
                "_T",
                "_T",
                "_T",
                "FT",
                "PT",
            ],
            "GEO": ["01001"] * 5,
            "OBS_VALUE": [
                100,
                80,
                20,
                75,
                25,
            ],
        }
    )


# ============================================================================
# Mobility
# ============================================================================

@pytest.fixture
def raw_mobility():
    return pd.DataFrame(
        {
            "CODGEO": ["01001"],
            "LIBGEO": ["Commune A"],
            "DCLT": ["01002"],
            "L_DCLT": ["Commune B"],
            "NBFLUX_C23_ACTOCC15P": [42],
        }
    )