with open('first_pass/first_pass/templates/analysis/timeseries.py', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace("resample('{params.get('freq', 'D')}')", "resample('ME' if params.get('freq', 'D') == 'M' else params.get('freq', 'D'))")
text = text.replace("resample('{params.get('freq', 'M')}')", "resample('ME' if params.get('freq', 'ME') == 'M' else params.get('freq', 'ME'))")

with open('first_pass/first_pass/templates/analysis/timeseries.py', 'w', encoding='utf-8') as f:
    f.write(text)
