---
id: real_estate
category: domain
---
# Real Estate Data Context
If this dataset involves property, housing, or real estate (e.g. sales, rent, Zillow data):
1. Prioritize spatial features. Always map variables by region or ZIP code.
2. The core KPI is usually 'Price per Square Foot'. Calculate this if area and price are available.
3. Assess the impact of 'Year Built' or 'Age' on value.
4. Separate Single-Family Homes from Multi-Family and Condos for any modeling.
5. SALES-RATIO STUDY: For property assessments or tax data, you MUST conduct a formal "Sales-Ratio Study" calculating Assessment-to-Sales ratios (Assessed Value / Sale Price) and calculate standard IAAO metrics like COD (Coefficient of Dispersion) and PRD (Price-Related Differential). Use `custom_code` for this math!
6. BASELINE MODELING: Use `custom_code` to train a baseline predictive model (e.g., Random Forest or Linear Regression) on property characteristics to predict observed price, and print the R-squared and MAE.
