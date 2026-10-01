import os

with open('first_pass/first_pass/notebook_builder.py', 'r', encoding='utf-8') as f:
    text = f.read()

patch = """        # Post-execution Synthesis Pass
        if enable_observer:
            from first_pass.llm.synthesis import generate_key_takeaways, generate_interpretations
            
            print("  Generating Interpretations...")
            interpretations = generate_interpretations(output_path, self.user_text)
            
            # Insert interpretations bottom-up to preserve indices
            for interp in sorted(interpretations, key=lambda x: x.cell_index, reverse=True):
                idx = interp.cell_index
                if 0 <= idx < len(nb.cells):
                    interp_cell = nbf.v4.new_markdown_cell(f"**Insight:** {interp.markdown}")
                    nb.cells.insert(idx + 1, interp_cell)
            
            takeaways = generate_key_takeaways(output_path, self.user_text)
            
            # Insert at the top (index 1, right after the title)
            takeaway_cell = nbf.v4.new_markdown_cell(takeaways)
            nb.cells.insert(1, takeaway_cell)
            
            # Save again
            with open(output_path, 'w', encoding='utf-8') as f:
                nbf.write(nb, f)"""

text = text.replace("""        # Post-execution Synthesis Pass
        if enable_observer:
            from first_pass.llm.synthesis import generate_key_takeaways
            takeaways = generate_key_takeaways(output_path, self.user_text)
            
            # Insert at the top (index 1, right after the title)
            takeaway_cell = nbf.v4.new_markdown_cell(takeaways)
            nb.cells.insert(1, takeaway_cell)
            
            # Save again
            with open(output_path, 'w', encoding='utf-8') as f:
                nbf.write(nb, f)""", patch)

with open('first_pass/first_pass/notebook_builder.py', 'w', encoding='utf-8') as f:
    f.write(text)
