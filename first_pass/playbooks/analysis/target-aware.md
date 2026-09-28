---
id: target-aware
title: Target-aware analysis
applies_when:
  - user_text_mentions: target
tags: [target, predictive, correlation]
templates: [target_distribution, target_corr_ranked, mutual_info_ranked, target_rate_by_cat]
---
Use when the user explicitly mentions a target or outcome column they care about (e.g., "predict churn" or "focus on revenue"). Start with the target's distribution, then rank features by correlation or mutual information to find drivers. For categorical features, look at the target rate by category.
