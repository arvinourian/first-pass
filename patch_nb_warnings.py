import os

with open('first_pass/first_pass/notebook_builder.py', 'r', encoding='utf-8') as f:
    text = f.read()

patch = """        self.add_code(
            f"%matplotlib inline\\n"
            f"import pandas as pd\\n"
            f"import matplotlib.pyplot as plt\\n"
            f"import seaborn as sns\\n"
            f"import warnings\\n"
            f"warnings.filterwarnings('ignore')\\n"
            f"sns.set_theme(style='whitegrid', palette='deep')\\n" """

text = text.replace("""        self.add_code(
            f"%matplotlib inline\\n"
            f"import pandas as pd\\n"
            f"import matplotlib.pyplot as plt\\n"
            f"import seaborn as sns\\n"
            f"sns.set_theme(style='whitegrid', palette='deep')\\n" """, patch)

with open('first_pass/first_pass/notebook_builder.py', 'w', encoding='utf-8') as f:
    f.write(text)
