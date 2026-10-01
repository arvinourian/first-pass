import re
import os

with open('first_pass/first_pass/llm/planner.py', 'r', encoding='utf-8') as f:
    text = f.read()

text = re.sub(r'5\. ADVANCED DOMAIN MODELING:.*?6\.', """5. BESPOKE & INTENTIONAL VISUALIZATIONS (CRITICAL): Basic templates (like simple bar charts) often lack analytical depth. You MUST use the `custom_code` template to generate highly intentional, consultant-grade Python code for complex plots. 
     - Example: If analyzing Sales over time, use `custom_code` to plot sales with a 13-week rolling average overlay, custom hex colors, and scatter points highlighting anomalies or holidays.
     - Example: If analyzing ROI by Major, use `custom_code` to sort by median, overlay error bars for variance, and add horizontal benchmark lines.
     - Use `custom_code` frequently to demonstrate deep analytical intention!
  6.""", text, flags=re.DOTALL)

with open('first_pass/first_pass/llm/planner.py', 'w', encoding='utf-8') as f:
    f.write(text)
