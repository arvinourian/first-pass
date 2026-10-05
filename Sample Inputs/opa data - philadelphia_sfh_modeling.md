# Philadelphia single-family modeling handoff

Start with **philadelphia_sfh_modeling.csv**. It has 69,366 sale observations and 44 columns, exported from the active sfh-pwd-v4 pipeline without further cleaning or imputation. It contains the exact headline TY2027 modeling cohorts, not the full city inventory or every sale since 2020.

- Training: 64,336 sales, January 1, 2020–June 30, 2025.
- Holdout: 5,030 sales, January 1–June 30, 2026.
- July–December 2025 is deliberately absent in this particular assessment-cycle comparison.
- One retained sale per parcel within each window; 1,075 holdout parcels also appear in training. IDs are unique within split, not necessarily across the whole file. This is a time holdout, not an exclusively new-parcel holdout.
- No names of buyers/sellers, model predictions, or risk-classifier scores are included.

## How to start

Use observed_price for a dollar-price model or log_price for a log-price model. Never include the other target as a predictor. feature_lists.json lists the exact current headline property inputs. Include time_years_from_2027 for a direct-time model. The direct LightGBM recipe handles time separately; an ordinary tree with time as another input will not reproduce its extrapolation. Published assessments are optional benchmarks, not inputs to our headline models. Likewise exclude split, ID, address and parcel_in_training from features.

For a first benchmark, fit log_price on property features and time with numeric variables plus one-hot categorical variables. Train only on split=train; evaluate split=test at each observed sale month. For Jan2027 assessments set time to zero, but comparing those predictions to raw2026 sales mixes prediction error with the difference in dates. Preprocessing, category encoding and tuning should use training data only.

This export does not supply TASP: it would require an explicitly chosen index/anchor and training-only estimation. Neither observed_price nor log_price is time-adjusted. Demographic variables are not included in this basic handoff.

## Data provenance and limits

Sales come from the cached Philadelphia deed data; property characteristics and published assessments from OPA; selected lot measurements use PWD parcel checks; neighborhood categories use the project's Zillow boundary assignment. Features describe the current retained inventory and may postdate historical sales. This is not a collection of historical property snapshots.

The shared pipeline restricts records to supported single-family homes, excluding condos and unresolved property/measurement conflicts. It retains the latest transaction within each window before applying single-property, minimum-price, party/distress and measurement checks. It also applies training-derived 2nd/99.9th percentile price limits ($40,000–$2,475,000) to both cohorts. It is therefore a screened sample, not all transactions or a representative sample of every home. The cached records may be incomplete. These test periods have been inspected during prior research.

No new values were imputed in this export. Raw OPA area fields remain beside selected model area fields. Recorded numeric zeros remain zero. Categorical MISSING is an explicit category; blank CSV fields are missing values. Some source categories are numeric-looking codes—treat them as nominal. Read parcel identifiers as strings, preserving leading zeros. Square footage is square feet; prices are dollars. Do not assume OPA year built is historically accurate.

Published TY2027 assessments are retained for comparison; they are not observed ground truth. The CSV does not estimate taxes or contain the unsold-parcel prediction population.

## Reading in Python

```python
import json
import pandas as pd
d = pd.read_csv('philadelphia_sfh_modeling.csv',
                dtype={'opa_parcel_number': str},
                keep_default_na=False, na_values=[''])
d['document_date'] = pd.to_datetime(d['document_date'])
spec = json.load(open('feature_lists.json'))
for c in spec['categorical']:
    d[c] = d[c].astype('category')
train = d[d['split'] == 'train'].copy()
test = d[d['split'] == 'test'].copy()
```

## Column dictionary

| Column | Meaning |
|---|---|
| opa_parcel_number | OPA account identifier; read as text. Identifier, not a predictor. |
| split | train = Jan2020–Jun2025; test = Jan–Jun2026. Preserve for our chronological comparison. |
| document_date | Recorded transaction date, ISO YYYY-MM-DD. |
| observed_price | Observed deed consideration in USD after transaction screening. Not TASP and not a model prediction. |
| log_price | Natural log of observed_price. Alternative target; never a feature when predicting price. |
| log_livable_area | Natural log of model_livable_area. |
| log_land_area | Natural log of model_land_area. |
| garage_spaces | Recorded garage-space count. |
| number_of_bedrooms | Recorded bedroom count. |
| number_of_bathrooms | Recorded bathroom count. |
| number_stories | Recorded number of stories. |
| both_room_counts_zero | 1 when recorded bedrooms and bathrooms are both zero, else 0. Zeros were not imputed. |
| far | model_livable_area / model_land_area. Floor-area-ratio proxy. |
| building_code_description_new | Current OPA property-style description category. |
| era_built | Provisional construction-era category derived from OPA year built. |
| interior_condition | Normalized OPA interior condition category/code; nominal, not an ordinal numeric scale. |
| central_air | Normalized OPA central air category/code; nominal, not an ordinal numeric scale. |
| view_type | Normalized OPA view type category/code; nominal, not an ordinal numeric scale. |
| gma | Fine OPA Geographic Market Area category. |
| exterior_condition | Normalized OPA exterior condition category/code; nominal, not an ordinal numeric scale. |
| basements | Normalized OPA basements category/code; nominal, not an ordinal numeric scale. |
| type_heater | Normalized OPA type heater category/code; nominal, not an ordinal numeric scale. |
| general_construction | Normalized OPA general construction category/code; nominal, not an ordinal numeric scale. |
| parcel_shape | Normalized OPA parcel shape category/code; nominal, not an ordinal numeric scale. |
| topography | Normalized OPA topography category/code; nominal, not an ordinal numeric scale. |
| gma_group | Intermediate OPA GMA grouping category. |
| gma_zone | Broad OPA modeling zone category; used for stratification. |
| neighborhood_name | Zillow neighborhood category. |
| street_address | OPA location label; audit/reference only, not used as predictor. |
| land_area | Recorded OPA lot area, square feet; retained separately from selected model measurement. |
| livable_area | Recorded OPA living area, square feet. |
| model_land_area | Selected model lot area in square feet, including supported PWD corrections. |
| model_livable_area | Selected supported living area in square feet. |
| land_area_source | Provenance of selected land measurement. |
| land_area_check | Land measurement consistency classification. |
| year_built | Recorded OPA year built; often approximate; reference field, not our numeric predictor. |
| year_built_estimate | OPA construction-year estimate indicator, retained as recorded. |
| garage_type | Recorded garage type category; used in OPA-style comparisons, not headline direct model. |
| geocode_lat | Latitude supplied in inventory; not a current headline predictor. |
| geocode_long | Longitude supplied in inventory; not a current headline predictor. |
| time_years_from_2027 | ((year−2027)*12+month−1)/12. Monthly-resolution numeric trend; set to zero for Jan2027 predictions. |
| parcel_in_training | Whether this parcel appears in training; always true for training rows. Identifies repeat parcels in holdout. |
| published_opa_2025 | Published TY2025 assessment, USD. Optional benchmark; excluded from our predictors. |
| published_opa_2027 | Published TY2027 assessment, USD. Optional benchmark; excluded from our predictors and unavailable at historical cutoff. |
