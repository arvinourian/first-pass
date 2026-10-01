import os

with open('first_pass/first_pass/notebook_builder.py', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Add Synthesis step to end of execute_notebook
synthesis_patch = """        with open(output_path, 'w', encoding='utf-8') as f:
            nbf.write(nb, f)
            
        # Post-execution Synthesis Pass
        if enable_observer:
            from first_pass.llm.synthesis import generate_key_takeaways
            takeaways = generate_key_takeaways(output_path, self.user_text)
            
            # Insert at the top (index 1, right after the title)
            takeaway_cell = nbf.v4.new_markdown_cell(takeaways)
            nb.cells.insert(1, takeaway_cell)
            
            # Save again
            with open(output_path, 'w', encoding='utf-8') as f:
                nbf.write(nb, f)
                
        return output_path"""

text = text.replace("""        with open(output_path, 'w', encoding='utf-8') as f:
            nbf.write(nb, f)
            
        return output_path""", synthesis_patch)

# 2. Add Schema / Data Quality to build_notebook
quality_patch = """        # 2. Raw data profile
        self.add_markdown("## 1. Schema: Inputs vs. Derived Outcomes")
        schema_md = "| Column | Type | Missing % | Unique | Flags |\\n|---|---|---|---|---|\\n"
        for col in profile.columns:
            flags = ", ".join(col.flags) if col.flags else "-"
            schema_md += f"| `{col.name}` | {col.inferred_type} | {col.null_percent:.1f}% | {col.unique_count} | {flags} |\\n"
        self.add_markdown(schema_md)
        
        self.add_markdown("## 2. Data-Quality Notes")
        dq_md = ""
        for col in profile.columns:
            if col.null_percent > 10: dq_md += f"* `{col.name}` has high missingness ({col.null_percent:.1f}%).\\n"
            if 'mixed_types' in col.flags: dq_md += f"* `{col.name}` contains mixed data types.\\n"
            if 'high_cardinality' in col.flags: dq_md += f"* `{col.name}` is high-cardinality categorical data.\\n"
        if not dq_md: dq_md = "* No major data quality issues detected in raw profile.\\n"
        self.add_markdown(dq_md)
        
        # 3. Cleaning plan"""

text = text.replace("""        # 2. Raw data profile
        self.add_markdown("## Raw Data Profile")
        profile_json = profile.model_dump_json(indent=2)
        # We can add a simple table instead of raw json
        table_md = "| Column | Type | Missing % | Unique |\\n|---|---|---|---|\\n"
        for col in profile.columns:
            table_md += f"| `{col.name}` | {col.inferred_type} | {col.null_percent:.1f}% | {col.unique_count} |\\n"
        self.add_markdown(table_md)
        
        # 3. Cleaning plan""", quality_patch)

with open('first_pass/first_pass/notebook_builder.py', 'w', encoding='utf-8') as f:
    f.write(text)
