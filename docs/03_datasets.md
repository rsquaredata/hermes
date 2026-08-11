# Datasets

## Overview

HERMES integrates multiple official French open datasets to represent the
territorial, socioeconomic, mobility, topographic and climatic conditions
that may influence bicycle and electric bicycle adoption.

The datasets are processed independently before being combined into the
HERMES analytical framework.

A central principle is to preserve a clear distinction between:

- raw source data;
- prepared datasets;
- derived spatial indicators;
- modelling features.

This separation ensures traceability and reproducibility throughout the
pipeline.

---

# Data sources

HERMES currently relies primarily on data from:

- **INSEE** — demographic, socioeconomic, employment and commuting data;
- **IGN** — administrative geometries and high-resolution elevation data;
- **Météo-France** — climate observations;
- **Data.gouv.fr** and official public-data platforms — dataset distribution
  and metadata.

Additional sources may be incorporated as the cycling feasibility and
adoption models are developed.

---

# Population and socioeconomic data

## Source

**INSEE**

Population and socioeconomic datasets provide municipality-level information
describing the characteristics of the study territory and its inhabitants.

Depending on the source dataset, variables may include:

- population;
- age structure;
- employment;
- labour-force characteristics;
- socioeconomic indicators;
- other municipality-level characteristics relevant to mobility behaviour.

## Role in HERMES

These variables characterize the populations associated with origin and
destination municipalities.

They may subsequently contribute to bicycle-adoption modelling by describing
differences in territorial and socioeconomic context.

## Spatial unit

Municipality.

Municipalities are identified using official INSEE municipality codes.

---

# Employment data

## Source

**INSEE**

Employment datasets describe the spatial distribution and characteristics of
employment across municipalities.

## Role in HERMES

Employment data contribute to the representation of the territorial structure
underlying commuting patterns.

They complement origin-destination mobility flows by describing the
employment characteristics of municipalities.

---

# Commuting flows

## Source

**INSEE — Mobilités professionnelles**

Commuting data describe origin-destination relationships between residence
and workplace municipalities.

Each observation represents a flow between:

- an origin municipality;
- a destination municipality;
- a number of commuters.

Additional attributes may describe characteristics of the commuting
population or transport behaviour depending on the source dataset.

## Role in HERMES

Commuting flows form the core mobility representation of HERMES.

Unlike municipality-level datasets, they describe relationships between
territories rather than attributes of individual territories.

They are used to:

- identify observed commuting relationships;
- characterize the spatial structure of mobility;
- estimate trip distances and territorial constraints;
- identify flows potentially compatible with bicycle or electric bicycle;
- provide the basis for future modal-shift scenarios.

Origin-destination flows may also be represented as a directed weighted graph.

---

# Administrative geometries

## Source

**IGN**

Administrative boundary data provide the geometry of municipalities included
in the HERMES study area.

## Role in HERMES

Municipality geometries are used for:

- spatial joins;
- study-area construction;
- coordinate transformations;
- raster masking;
- spatial visualization;
- integration of raster-derived indicators with municipality and mobility
  data.

## Coordinate systems

HERMES uses coordinate reference systems appropriate to each processing
stage.

Geographic source data may initially use standard geographic coordinates,
while metric spatial analysis is performed in **Lambert-93 (EPSG:2154)**.

Using a projected metric CRS is particularly important for:

- distance calculations;
- raster processing;
- terrain analysis;
- spatial buffering.

---

# Elevation and terrain

## Source

**IGN RGE ALTI**

HERMES uses the IGN **RGE ALTI** digital elevation model to represent terrain
within the case-study area.

The current source product provides elevation data at a spatial resolution of
approximately **1 metre**.

RGE ALTI is distributed as tiled raster data in Lambert-93 coordinates with
elevations referenced to the French IGN69 vertical system.

## Role in HERMES

Topography is relevant to cycling because terrain affects the physical effort
required to travel by bicycle.

Its effect is particularly important when distinguishing between:

- conventional bicycle feasibility;
- electric bicycle feasibility.

Rather than assigning a single elevation value to each municipality, HERMES
retains the spatial structure of the terrain so that slope-related indicators
can be derived along relevant areas or mobility relationships.

---

## RGE ALTI processing

The source RGE ALTI product is substantially more detailed than required for
territorial mobility modelling.

HERMES therefore uses the 1 m source data to construct a common
**10 m digital elevation model (DEM)** for the case-study area.

The processing workflow includes:

1. identifying the RGE ALTI tiles intersecting the study area;
2. extracting only the required elevation tiles from the source archives;
3. adding limited peripheral context for raster processing;
4. mosaicking the selected tiles;
5. resampling elevation from 1 m to 10 m;
6. masking the resulting DEM to the study-area geometry;
7. validating spatial coverage and elevation values.

The resulting DEM uses:

- **CRS:** EPSG:2154;
- **horizontal resolution:** 10 m;
- **elevation reference:** IGN69;
- **format:** GeoTIFF.

The 10 m resolution was selected as a compromise between terrain detail,
computational cost and the spatial scale required for mobility analysis.

---

## Terrain-derived indicators

Elevation itself is not the primary cycling variable.

HERMES derives terrain characteristics from the DEM, particularly **slope**.

Slope is computed from local elevation gradients and can subsequently be
summarized or associated with mobility relationships.

Potential terrain features include:

- mean slope;
- median slope;
- upper slope percentiles;
- maximum relevant slope;
- elevation gain;
- elevation loss;
- share of a route or area above defined slope thresholds.

The exact features used by the cycling feasibility model will be determined
during the modelling stage.

---

# Climate data

## Source

**Météo-France**

Climate observations provide information about environmental conditions in
and around the study territory.

Depending on station and temporal coverage, variables may include:

- temperature;
- precipitation;
- wind;
- other meteorological indicators.

## Role in HERMES

Climate may affect the attractiveness and practical feasibility of cycling.

Climate variables can therefore contribute to the territorial representation
used by cycling feasibility and adoption models.

The methodology distinguishes long-term climatic characteristics from
short-term weather conditions when relevant.

---

# Study area

The initial HERMES case study focuses on **Villefranche-sur-Saône and its
surrounding mobility system**.

The analytical territory extends beyond the municipality itself because
commuting relationships connect Villefranche-sur-Saône with surrounding
municipalities.

Consequently, the spatial extent of individual datasets may differ from the
administrative boundary of Villefranche-sur-Saône.

The study area is defined according to the requirements of the mobility
analysis rather than by a single municipality boundary.

---

# Data integration

Municipality-level datasets are primarily integrated using official INSEE
municipality codes.

Spatial datasets are linked through geographic operations where appropriate.

Mobility data require a different structure because each observation relates
two municipalities:

```text
origin municipality
        │
        ├──────── commuting flow ────────► destination municipality
        │
        └──────── territorial features
```

This allows characteristics of both the origin and destination territories to
be associated with mobility relationships.

Raster-derived variables, such as terrain indicators, are calculated through
spatial operations before being incorporated into modelling datasets.

---

# Data processing levels

HERMES distinguishes several levels of data transformation.

```mermaid
flowchart LR

    A["External source"]

    --> B["Raw data"]

    --> C["Prepared data"]

    --> D["Spatial / derived indicators"]

    --> E["Modelling features"]

    --> F["Simulation"]
```

### Raw data

Original downloaded files are preserved without analytical modification.

### Prepared data

Prepared datasets contain standardized and validated representations of the
source data.

Typical operations include:

- variable selection;
- type conversion;
- identifier harmonization;
- missing-value handling;
- coordinate-system harmonization.

### Derived indicators

Derived datasets contain variables calculated from prepared source data.

Examples include:

- mobility distances;
- terrain slope;
- climate summaries;
- origin-destination characteristics.

### Modelling features

Features combine relevant indicators into the analytical representation used
for cycling feasibility, adoption modelling and scenario simulation.

---

# Data quality and validation

Each dataset is validated before integration.

Validation may include:

- schema verification;
- identifier uniqueness;
- missing-value analysis;
- geographic coverage;
- coordinate reference systems;
- expected raster resolution;
- spatial coverage;
- value ranges;
- origin-destination consistency.

For raster datasets such as RGE ALTI, HERMES additionally verifies that the
constructed raster adequately covers the study-area geometry.

---

# Data provenance

HERMES maintains explicit provenance for each dataset through the project data
catalog.

Dataset metadata include information such as:

- source organization;
- source URL;
- local storage location;
- dataset format;
- preparation status;
- expected schema where applicable.

The objective is for every modelling variable to remain traceable to its
original source and transformation pipeline.

---

# Reproducibility

Raw data are never manually modified as part of the analytical workflow.

Transformations are implemented through version-controlled Python modules and
notebooks.

This makes it possible to regenerate prepared datasets and derived indicators
from the original sources and documented processing steps.