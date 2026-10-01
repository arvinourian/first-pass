with open('first_pass/app.py', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace('my_bar.progress(15, text="Stage 2.5: RAG Pass 0 (Domain Context)...")',
                    'my_bar.progress(15, text="Stage 2.5: RAG Pass 0 (Domain Context)...")') # Wait, it is already Pass 0
text = text.replace('my_bar.progress(30, text="Stage 3: RAG Pass 1 (Cleaning Plan)...")',
                    'my_bar.progress(30, text="Stage 3: RAG Pass 1 (Cleaning Plan)...")') # Pass 1
text = text.replace('my_bar.progress(60, text="Stage 4.5: RAG Pass 1.5 (Feature Engineering Plan)...")',
                    'my_bar.progress(60, text="Stage 4.5: RAG Pass 2 (Feature Engineering Plan)...")') # Pass 1.5 -> 2
text = text.replace('my_bar.progress(70, text="Stage 5: RAG Pass 2 (Analysis Plan)...")',
                    'my_bar.progress(70, text="Stage 5: RAG Pass 3 (Analysis Plan)...")') # Pass 2 -> 3
text = text.replace('my_bar.progress(95, text="Stage 7: RAG Pass 3 (Executive Synthesis)...")',
                    'my_bar.progress(95, text="Stage 7: RAG Pass 4 (Executive Synthesis)...")') # Pass 3 -> 4

with open('first_pass/app.py', 'w', encoding='utf-8') as f:
    f.write(text)
