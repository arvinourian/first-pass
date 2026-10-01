import re
import os

# 1. Fix categorical_vs_categorical.py (crosstab_table normalize parameter)
cat_path = 'first_pass/first_pass/templates/analysis/categorical_vs_categorical.py'
with open(cat_path, 'r', encoding='utf-8') as f:
    text = f.read()

# We want to map norm to a proper python literal or string.
# In CrosstabTable.generate_code:
# norm = params.get('normalize', False)
# if isinstance(norm, str):
#     if norm.lower() == 'false': norm = False
#     elif norm.lower() == 'true': norm = True
# return f"display(pd.crosstab(df['{row}'], df['{col}'], normalize={repr(norm)}))"

def replacement_crosstab(match):
    return """        norm = params.get('normalize', False)
        if isinstance(norm, str):
            if norm.lower() == 'false': norm = False
            elif norm.lower() == 'true': norm = True
        return f"display(pd.crosstab(df['{row}'], df['{col}'], normalize={repr(norm)}))\""""

text = re.sub(r"        norm = params\.get\('normalize', False\)\n        return f\"display\(pd\.crosstab\(df\['\{row\}'\], df\['\{col\}'\], normalize=\{norm\}\)\)\"",
              """        norm = params.get('normalize', False)
        if isinstance(norm, str):
            if norm.lower() == 'false': norm = False
            elif norm.lower() == 'true': norm = True
        return f"display(pd.crosstab(df['{row}'], df['{col}'], normalize={repr(norm)}))\"""", text)

with open(cat_path, 'w', encoding='utf-8') as f:
    f.write(text)

print('Updated crosstab_table normalization logic.')

# 2. Fix timeseries.py (datetime indexing)
ts_path = 'first_pass/first_pass/templates/analysis/timeseries.py'
with open(ts_path, 'r', encoding='utf-8') as f:
    ts_text = f.read()

ts_text = ts_text.replace("df.set_index('{d}')", "df.set_index(pd.to_datetime(df['{d}']))")
ts_text = ts_text.replace("df.set_index({repr(date)})", "df.set_index(pd.to_datetime(df[{repr(date)}]))")
ts_text = ts_text.replace("df.groupby('{d}')", "df.groupby(pd.to_datetime(df['{d}']))")

with open(ts_path, 'w', encoding='utf-8') as f:
    f.write(ts_text)

print('Updated timeseries.py datetime indexing.')
