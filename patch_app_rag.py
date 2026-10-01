with open('first_pass/app.py', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace('domain_pbs = idx.hybrid_search(domain_query, "domain", top_k=1)',
                    'domain_pbs = idx.hybrid_search(domain_query, "domain", top_k=1, stage="pass0")')

text = text.replace('cleaning_pbs = idx.hybrid_search(query, "cleaning")',
                    'cleaning_pbs = idx.hybrid_search(query, "cleaning", stage="pass1")')

text = text.replace('engineering_pbs = idx.hybrid_search(query_e, "engineering")',
                    'engineering_pbs = idx.hybrid_search(query_e, "engineering", stage="pass2")')

text = text.replace('analysis_pbs = idx.hybrid_search("analysis " + user_instructions, "analysis")',
                    'analysis_pbs = idx.hybrid_search("analysis " + user_instructions, "analysis", stage="pass3")')

with open('first_pass/app.py', 'w', encoding='utf-8') as f:
    f.write(text)
