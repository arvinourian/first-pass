import os

for fname in ['batch_run.py', 'first_pass/test_opa.py', 'first_pass/test_opa_forced.py']:
    if not os.path.exists(fname): continue
    with open(fname, 'r', encoding='utf-8') as f:
        text = f.read()

    text = text.replace('domain_pbs = idx.hybrid_search(domain_query, "domain", top_k=1)',
                        'domain_pbs = idx.hybrid_search(domain_query, "domain", top_k=1, stage="pass0")')

    text = text.replace('cleaning_pbs = idx.hybrid_search(query, "cleaning")',
                        'cleaning_pbs = idx.hybrid_search(query, "cleaning", stage="pass1")')

    text = text.replace('engineering_pbs = idx.hybrid_search(query_e, "engineering")',
                        'engineering_pbs = idx.hybrid_search(query_e, "engineering", stage="pass2")')

    text = text.replace('analysis_pbs = idx.hybrid_search("analysis " + user_instructions, "analysis")',
                        'analysis_pbs = idx.hybrid_search("analysis " + user_instructions, "analysis", stage="pass3")')

    with open(fname, 'w', encoding='utf-8') as f:
        f.write(text)
