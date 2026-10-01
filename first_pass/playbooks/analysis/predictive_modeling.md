---
id: predictive-modeling
title: Predictive ML Modeling
category: analysis
applies_when: "The user mentions a specific target to predict, or there is a clear primary outcome variable (e.g. price, ROI, sales) that requires a formal Baseline ML Model."
templates:
  - train_rf
---
# Predictive ML Modeling
Use `train_rf` to train a baseline Random Forest regression model on numeric and categorical features to predict a target variable, and print the resulting R-squared, Mean Absolute Error (MAE), and Feature Importances.
