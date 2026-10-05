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
when the series is noisy.
