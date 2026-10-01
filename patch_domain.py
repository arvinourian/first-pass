import re

with open('first_pass/app.py', 'r', encoding='utf-8') as f:
    text = f.read()

old_text = """            @st.cache_resource
            def get_index():
                index = PlaybookIndex()
                index.build(["playbooks/cleaning", "playbooks/analysis"])
                return index
            
            idx = get_index()"""

new_text = """            @st.cache_resource
            def get_index():
                index = PlaybookIndex()
                index.build(["playbooks/cleaning", "playbooks/analysis", "playbooks/domain"])
                return index
            
            idx = get_index()
            
            if enable_domain:
                my_bar.progress(15, text="Stage 2.5: RAG Pass 0 (Domain Context)...")
                domain_query = f"domain industry {raw_profile.row_count} rows " + " ".join([c.name for c in raw_profile.columns]) + combined_instructions
                domain_pbs = idx.hybrid_search(domain_query, "domain", top_k=1)
                if domain_pbs:
                    combined_instructions += f"\\n\\n--- Recommended Industry Best Practices ---\\n{domain_pbs[0].content}"
"""

text = text.replace(old_text, new_text)

with open('first_pass/app.py', 'w', encoding='utf-8') as f:
    f.write(text)
