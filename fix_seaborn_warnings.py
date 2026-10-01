import os

replacements = [
    (
        'first_pass/templates/analysis/geographic.py',
        "sns.barplot(x=agg_df.values, y=agg_df.index, palette='viridis')",
        "sns.barplot(x=agg_df.values, y=agg_df.index, hue=agg_df.index, palette='viridis', legend=False)"
    ),
    (
        'first_pass/templates/analysis/target_aware.py',
        "sns.barplot(x=corrs.values, y=corrs.index, palette='coolwarm')",
        "sns.barplot(x=corrs.values, y=corrs.index, hue=corrs.index, palette='coolwarm', legend=False)"
    ),
    (
        'first_pass/templates/analysis/target_aware.py',
        "sns.barplot(x=mi_series.values, y=mi_series.index, palette='viridis')",
        "sns.barplot(x=mi_series.values, y=mi_series.index, hue=mi_series.index, palette='viridis', legend=False)"
    ),
    (
        'first_pass/templates/analysis/target_aware.py',
        "sns.barplot(x=rate.values, y=rate.index, palette='mako')",
        "sns.barplot(x=rate.values, y=rate.index, hue=rate.index, palette='mako', legend=False)"
    ),
    (
        'first_pass/templates/analysis/text.py',
        "sns.barplot(x=counts.values, y=counts.index, palette='Blues_r')",
        "sns.barplot(x=counts.values, y=counts.index, hue=counts.index, palette='Blues_r', legend=False)"
    )
]

for file, old, new in replacements:
    path = os.path.join('first_pass', file)
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    if old in content:
        content = content.replace(old, new)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        print('Updated', path)
    else:
        print('Not found in', path)
