import os

with open('first_pass/first_pass/templates/analysis/timeseries.py', 'r', encoding='utf-8') as f:
    text = f.read()

old_resample = "resample('ME' if params.get('freq', 'D') == 'M' else params.get('freq', 'D')).{params.get('agg', 'sum')}("
freq = "{params.get('freq', 'D')}"
new_resample = f"resample('ME' if '{freq}' == 'M' else '{freq}').{{params.get('agg', 'sum')}}("

text = text.replace(old_resample, new_resample)

with open('first_pass/first_pass/templates/analysis/timeseries.py', 'w', encoding='utf-8') as f:
    f.write(text)
