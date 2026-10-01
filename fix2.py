import re

f11 = 'first_pass/first_pass/templates/analysis/categorical_vs_categorical.py'
with open(f11, 'r', encoding='utf-8') as f:
    c11 = f.read()
c11 = c11.replace("f\"print(f\'CramAcr\'s V: {{cramer_v:.4f}}')\n\"", "f\"print(f\\\"Cramer's V: {{cramer_v:.4f}}\\\")\\n\"")
with open(f11, 'w', encoding='utf-8') as f:
    f.write(c11)

f22 = 'first_pass/first_pass/templates/analysis/text.py'
with open(f22, 'r', encoding='utf-8') as f:
    c22 = f.read()
c22 = c22.replace("f\"plt.title(f\'Text Length Distribution: {{{col}}}\')\n\"", "f\"plt.title('Text Length Distribution: {col}')\\n\"")
c22 = c22.replace("f\"plt.title(f\'Top {{min({top_k}, len(counts))}} {n}-grams in {{{col}}}\')\n\"", "f\"plt.title(f'Top {{min({top_k}, len(counts))}} {m}-grams in {col}')\\n\"")
with open(f22, 'w', encoding='utf-8') as f:
    f.write(c22)

print('Done')
