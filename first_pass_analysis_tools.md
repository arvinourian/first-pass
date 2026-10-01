# First Pass — Analysis Tool Catalog

This file defines every analysis/visualization tool the First Pass RAG planner
(Pass 2) may select. Use it to build two things:

1. **Analysis templates** in `templates/analysis/` — one module per `template_id`,
   each with a Pydantic params schema and a function that returns notebook cells.
2. **Analysis playbooks** in `playbooks/analysis/` — Markdown files with YAML
   frontmatter that the retriever searches. Each playbook recommends one or more
   `template_id`s and describes when they apply.

## Implementation rules (apply to every template)

- Charts use matplotlib + seaborn, rendered as static images so they appear in
  the PDF export. Consistent styling, titles, axis labels, readable at PDF page
  width. Rotate or truncate long category labels.
- Each template emits: one markdown header cell (analysis title, the plan's
  rationale, source playbook IDs) followed by code cell(s). The notebook must NOT
  interpret or comment on the results.
- Generated code must be readable and runnable in the standalone `.py` export.
- Every template validates its preconditions at plan-validation time (column
  types, minimum rows, cardinality limits). If a precondition fails, the plan
  item is rejected before execution.
- If a template fails at execution time, catch the error, emit a markdown cell
  "This analysis failed: <error>", and continue.
- Statistical tests output numbers only (statistic, p-value, effect size) —
  no written conclusions.

## Tiers

- **v1** — implement first; covers most spreadsheets.
- **v2** — implement after the end-to-end pipeline works.

## Column type vocabulary (from the profiler)

`numeric`, `categorical`, `datetime`, `boolean`, `text`, `id`, `lat`, `lon`,
`region` (state/country/zip codes).

---

## 1. Data overview and quality

Always considered first. These orient the user before any analysis.

| template_id | Tool | Applies when | Key params | Tier |
|---|---|---|---|---|
| `summary_stats` | Summary statistics table | Always | `columns` (default: all) | v1 |
| `column_overview` | Column type overview (type, null %, unique count) | Always | — | v1 |
| `missing_bar` | Missing-value bar chart | Any column has nulls | `min_null_pct` | v1 |
| `missing_matrix` | Missingness matrix/heatmap | Nulls in 3+ columns | `max_rows_sampled` | v1 |
| `duplicate_summary` | Duplicate row summary | Duplicates detected | `subset_columns` | v1 |
| `cardinality_bar` | Unique-count bar chart per categorical | 3+ categorical columns | — | v1 |
| `outlier_flags` | Outlier flag table (IQR or z-score) | Numeric columns with long tails | `method` (`iqr`/`zscore`), `threshold` | v1 |

## 2. Single numeric column

| template_id | Tool | Applies when | Key params | Tier |
|---|---|---|---|---|
| `histogram_kde` | Histogram with KDE | Any numeric column | `column`, `bins` | v1 |
| `histogram_log` | Log-scale histogram | Strong right skew (skewness > ~2), all values > 0 | `column`, `bins` | v1 |
| `box_multi` | Box plots, multiple columns side by side | 2+ numeric columns on comparable scales | `columns` | v1 |
| `violin` | Violin plot | Distribution shape matters (e.g., suspected bimodality) | `column` | v1 |
| `ecdf` | ECDF plot | Skewed data; "what share falls below X" | `column` | v1 |
| `qq_plot` | Q-Q plot vs normal | Before any parametric test | `column` | v2 |

## 3. Single categorical column

| template_id | Tool | Applies when | Key params | Tier |
|---|---|---|---|---|
| `freq_bar` | Frequency bar chart, top-N + "Other" | Any categorical column | `column`, `top_n` (default 12) | v1 |
| `value_counts_table` | Value counts table with percentages | Exact counts needed | `column`, `top_n` | v1 |
| `pareto_chart` | Pareto chart (bars + cumulative % line) | Checking whether few categories dominate | `column`, `top_n` | v1 |

## 4. Numeric vs numeric

| template_id | Tool | Applies when | Key params | Tier |
|---|---|---|---|---|
| `corr_heatmap` | Correlation heatmap (Pearson + Spearman) | 3–25 numeric columns | `columns`, `methods` | v1 |
| `corr_ranked_bar` | Ranked correlation bar chart of top pairs | >25 numeric columns, or heatmap too dense | `top_k_pairs` | v1 |
| `scatter` | Scatter plot | Strongest correlated pairs | `x`, `y`, `hue` (optional categorical) | v1 |
| `scatter_regression` | Scatter with regression line | Relationship appears linear | `x`, `y` | v1 |
| `hexbin` | Hexbin / 2D density | Scatter candidate with > 5,000 rows | `x`, `y`, `gridsize` | v1 |
| `pair_plot` | Pair plot | 2–5 numeric columns only | `columns`, `hue` | v2 |

## 5. Numeric vs categorical

| template_id | Tool | Applies when | Key params | Tier |
|---|---|---|---|---|
| `grouped_box` | Grouped box plots | Numeric + categorical with ≤ 15 groups | `numeric`, `category`, `top_n_groups` | v1 |
| `grouped_violin` | Grouped violin plots | Same, where shape differs | `numeric`, `category` | v1 |
| `group_mean_ci` | Bar chart of group means with 95% CIs | Comparing averages across groups | `numeric`, `category` | v1 |
| `strip_swarm` | Strip/swarm plot | Small groups (≤ ~50 points each) | `numeric`, `category` | v1 |
| `group_summary_table` | Per-group count, mean, median, std | Any numeric + categorical pair | `numeric`, `category` | v1 |
| `group_diff_test` | ANOVA or Kruskal-Wallis (auto-select by normality) | 2+ groups each with ≥ 5 rows | `numeric`, `category` | v2 |

## 6. Categorical vs categorical

| template_id | Tool | Applies when | Key params | Tier |
|---|---|---|---|---|
| `crosstab_table` | Crosstab / contingency table | Two categoricals, each ≤ 15 levels | `row`, `col`, `normalize` | v1 |
| `crosstab_heatmap` | Crosstab heatmap | Same | `row`, `col`, `normalize` | v1 |
| `stacked_bar` | Stacked / 100% stacked bar | Composition of one category within another | `x`, `stack`, `percent` | v1 |
| `chi_square` | Chi-square test + Cramér's V | Expected cell counts mostly ≥ 5 | `row`, `col` | v2 |

## 7. Time series

Triggered by a `datetime` column. Often the most valuable group.

| template_id | Tool | Applies when | Key params | Tier |
|---|---|---|---|---|
| `line_time` | Line plot over time | datetime + numeric | `date`, `value`, `agg` | v1 |
| `resample_agg` | Resampled aggregation | Timestamps finer than the useful grain | `date`, `value`, `freq` (D/W/M/Q/Y), `agg` | v1 |
| `rolling_mean` | Rolling mean overlay | Noisy series | `date`, `value`, `window` | v1 |
| `small_multiples_time` | Small multiples by category | datetime + numeric + categorical (≤ 12 groups) | `date`, `value`, `category` | v1 |
| `stl_decompose` | Seasonal decomposition (STL, statsmodels) | ≥ 2 full seasonal cycles at a regular frequency | `date`, `value`, `period` | v2 |
| `seasonality_heatmap` | Month × year or weekday × hour heatmap | ≥ 1 year of data, or sub-daily timestamps | `date`, `value`, `layout` | v1 |
| `period_compare` | Period-over-period comparison (YoY, MoM) | ≥ 2 years or ≥ 2 months as appropriate | `date`, `value`, `period` | v1 |
| `pct_change` | Percent change / growth rate plot | Rate of change is meaningful | `date`, `value`, `freq` | v1 |
| `cumulative_sum` | Cumulative sum plot | Additive metric (revenue, signups) | `date`, `value` | v1 |
| `acf_plot` | Autocorrelation (ACF) plot | ≥ ~50 regular observations | `date`, `value`, `lags` | v2 |
| `timestamp_gaps` | Timestamp gap check | Any datetime column | `date`, `expected_freq` | v1 |
| `stacked_area_time` | Stacked area chart (composition over time) | datetime + numeric + categorical (≤ 8 groups) | `date`, `value`, `category`, `percent` | v1 |

## 8. Ranking and concentration

| template_id | Tool | Applies when | Key params | Tier |
|---|---|---|---|---|
| `top_bottom_n` | Top-N / bottom-N bar chart | Entity column (product, customer, store) + metric | `entity`, `value`, `n`, `agg` | v1 |
| `cumulative_share` | Cumulative share (Pareto) curve | Entity + additive metric | `entity`, `value` | v1 |
| `lorenz_gini` | Lorenz curve + Gini coefficient | Entity + non-negative additive metric | `entity`, `value` | v1 |

## 9. Target-aware analysis

Only when the user's text names an outcome/target column (e.g., "I care about
churn"). The planner must map the user's wording to an actual column name.

| template_id | Tool | Applies when | Key params | Tier |
|---|---|---|---|---|
| `target_distribution` | Target distribution / class balance | Target identified | `target` | v2 |
| `target_corr_ranked` | Ranked correlation of features with target | Numeric target | `target`, `top_k` | v2 |
| `mutual_info_ranked` | Mutual information ranking | Mixed feature types or nonlinear relationships | `target`, `top_k` | v2 |
| `target_rate_by_cat` | Target rate by category | Binary target + categorical features | `target`, `category` | v2 |

## 10. Multivariate structure

Heavier; lower priority for a first pass. Label clearly as exploratory.

| template_id | Tool | Applies when | Key params | Tier |
|---|---|---|---|---|
| `pca_overview` | PCA scatter + explained variance plot | ≥ 5 numeric columns | `columns`, `n_components`, `hue` | v2 |
| `kmeans_explore` | K-means clusters with elbow plot | ≥ 3 numeric columns, ≥ 100 rows | `columns`, `k_range` | v2 |

## 11. Text columns

| template_id | Tool | Applies when | Key params | Tier |
|---|---|---|---|---|
| `text_length_dist` | Text length distribution | Free-text column | `column` | v2 |
| `top_ngrams` | Top words / n-grams bar chart | Free-text column | `column`, `n`, `top_k`, `stopwords` | v2 |

## 12. Geographic

| template_id | Tool | Applies when | Key params | Tier |
|---|---|---|---|---|
| `latlon_scatter` | Lat/long scatter plot | `lat` + `lon` columns | `lat`, `lon`, `hue` | v2 |
| `region_agg` | Aggregation by region (table + bar) | `region` column + metric | `region`, `value`, `agg` | v2 |
| `choropleth` | Choropleth map (geopandas) | `region` codes resolvable to boundaries | `region`, `value` | v2 (later) |

## 13. Domain-specific

Retrieved when the user's text or column names signal the domain.

| template_id | Tool | Applies when | Key params | Tier |
|---|---|---|---|---|
| `fin_returns` | Returns, rolling volatility, drawdown | datetime + price/close column | `date`, `price`, `window` | v2 |
| `cohort_retention` | Cohort retention heatmap | user ID + signup date + activity date | `user_id`, `signup_date`, `activity_date`, `freq` | v2 |
| `funnel` | Funnel chart | Ordered stage/step columns or stage labels | `stages`, `user_id` | v2 |
| `likert_diverging` | Diverging stacked bar | Likert-scale survey responses | `columns`, `scale_order` | v2 |
| `rfm_table` | RFM (recency, frequency, monetary) table | Transactions with customer ID, date, amount | `customer_id`, `date`, `amount` | v2 |

---

## Planner selection rules (include in the Pass 2 system prompt)

1. Always include `column_overview` and `summary_stats`. Include `missing_bar`
   if any nulls exist.
2. Prioritize analyses involving columns or goals the user mentioned in their
   text input.
3. Prefer breadth over depth: one analysis per distinct question, not multiple
   views of the same relationship.
4. Respect the analysis cap (default 8, configurable), not counting the
   always-included overview items. Rank candidates by expected usefulness for a
   first look.
5. List candidates that were considered but cut by the cap in a
   `further_analyses` field of the plan. The notebook renders these as a
   "Further analyses to consider" section — this is how First Pass points the
   user in the right direction.
6. Never select a template whose "Applies when" preconditions are not met.
   Only select v1 templates unless v2 templates are enabled in config.
7. Never use pie charts, 3D charts, dual-axis charts, or word clouds.
8. Every plan item must include `template_id`, `columns`, `params`,
   `rationale` (one sentence), and `playbook_ids`.

## Playbook frontmatter example

```yaml
---
id: timeseries-basic
title: Basic time series first look
applies_when:
  - has_type: datetime
  - has_type: numeric
tags: [time series, trend, seasonality]
templates: [line_time, resample_agg, rolling_mean, timestamp_gaps]
---
Use when the data has at least one datetime column and one numeric metric.
Start with timestamp_gaps to confirm regularity, then line_time at a sensible
grain (resample_agg if raw timestamps are finer than daily). Add rolling_mean
when the series is noisy. If there are 2+ years of data, consider
period_compare and seasonality_heatmap.
```

