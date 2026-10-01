import os
import glob
import re

replacements = [
    # geographic.py
    (
        'first_pass/first_pass/templates/analysis/geographic.py',
        r"plt\.title\(f'Top 20 Regions by \{agg\.capitalize\(\)\} of \{\{\{val\}\}\}'\)",
        r"plt.title(f'Top 20 Regions by {agg.capitalize()} of {val}')"
    ),
    # numeric.py
    (
        'first_pass/first_pass/templates/analysis/numeric.py',
        r"plt\.title\(f'Q-Q Plot: \{\{\{col\}\}\}'\)",
        r"plt.title(f'Q-Q Plot: {col}')"
    ),
    # target_aware.py
    (
        'first_pass/first_pass/templates/analysis/target_aware.py',
        r"plt\.title\(f'Target Distribution: \{\{\{target\}\}\}'\)",
        r"plt.title(f'Target Distribution: {target}')"
    ),
    (
        'first_pass/first_pass/templates/analysis/target_aware.py',
        r"plt\.title\(f'Top \{\{min\(\{top_k\}, len\(corrs\)\)\}\} Correlations with \{\{\{target\}\}\}'\)",
        r"plt.title(f'Top {{min({top_k}, len(corrs))}} Correlations with {target}')"
    ),
    (
        'first_pass/first_pass/templates/analysis/target_aware.py',
        r"plt\.title\(f'Top Mutual Information with \{\{\{target\}\}\}'\)",
        r"plt.title(f'Top Mutual Information with {target}')"
    ),
    (
        'first_pass/first_pass/templates/analysis/target_aware.py',
        r"plt\.title\(f'Mean \{\{\{target\}\}\} by \{\{\{cat\}\}\}'\)",
        r"plt.title(f'Mean {target} by {cat}')"
    ),
    # timeseries.py
    (
        'first_pass/first_pass/templates/analysis/timeseries.py',
        r"plt\.title\(f'Autocorrelation: \{\{\{val\}\}\}'\)",
        r"plt.title(f'Autocorrelation: {val}')"
    )
]

for file_path, old_pattern, new_repl in replacements:
    with open(file_path, 'r', encoding='utf-8') as f:
        text = f.read()
    
    # We use re.sub just in case
    # Actually wait, the old string has f"..." so the backslashes are for re.
    new_text = re.sub(old_pattern, new_repl.replace('\\', '\\\\'), text)
    
    if new_text != text:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_text)
        print(f"Updated {file_path}")
    else:
        print(f"Pattern not found in {file_path}")
