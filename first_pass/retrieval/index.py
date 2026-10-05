import os
import yaml
import numpy as np
import faiss
from rank_bm25 import BM25Okapi
from typing import List
from first_pass.llm.client import get_embedding

class Playbook:
    def __init__(self, category: str, file_path: str):
        self.category = category
        self.file_path = file_path
        self.content = ""
        self.metadata = {}
        self.parse_markdown()
        
    def parse_markdown(self):
        with open(self.file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        if lines and lines[0].strip() == '---':
            end_idx = 1
            while end_idx < len(lines) and lines[end_idx].strip() != '---':
                end_idx += 1
            if end_idx < len(lines):
                yaml_str = "".join(lines[1:end_idx])
                self.metadata = yaml.safe_load(yaml_str)
                self.content = "".join(lines[end_idx+1:])
                
    def get_search_text(self):
        title = self.metadata.get('title', '')
        applies_when = self.metadata.get('applies_when', '')
        tags = " ".join(self.metadata.get('tags', []))
        return f"{title}\n{applies_when}\n{tags}\n{self.content}"

class PlaybookIndex:
    def __init__(self):
        self.playbooks = []
        self.bm25 = None
        self.faiss_index = None
        
    def build(self, playbook_dirs: List[str]):
        for pdir in playbook_dirs:
            category = os.path.basename(pdir)
            if not os.path.exists(pdir):
                continue
            for fname in os.listdir(pdir):
                if fname.endswith('.md'):
                    pb = Playbook(category, os.path.join(pdir, fname))
                    self.playbooks.append(pb)
                    
        if not self.playbooks:
            return
            
        # BM25
        corpus = [pb.get_search_text().lower().split() for pb in self.playbooks]
        self.bm25 = BM25Okapi(corpus)
        
        # FAISS
        embeddings = []
        for pb in self.playbooks:
            emb = get_embedding(pb.get_search_text(), stage="indexing")
            embeddings.append(emb)
            
        emb_matrix = np.array(embeddings, dtype='float32')
        faiss.normalize_L2(emb_matrix)
        
        dim = emb_matrix.shape[1]
        self.faiss_index = faiss.IndexFlatIP(dim)
        self.faiss_index.add(emb_matrix)
        
    def hybrid_search(self, query: str, category: str, top_k: int = 4, stage: str = "embedding") -> List[Playbook]:
        if not self.playbooks:
            return []
            
        cat_indices = [i for i, pb in enumerate(self.playbooks) if pb.category == category]
        if not cat_indices:
            return []
            
        tokenized_query = query.lower().split()
        bm25_scores = self.bm25.get_scores(tokenized_query)
        
        q_emb = get_embedding(query, stage=stage)
        q_emb_matrix = np.array([q_emb], dtype='float32')
        faiss.normalize_L2(q_emb_matrix)
        
        D, I = self.faiss_index.search(q_emb_matrix, len(self.playbooks))
        
        faiss_scores = np.zeros(len(self.playbooks))
        for i, idx in enumerate(I[0]):
            faiss_scores[idx] = float(D[0][i])
            
        # Normalize
        if max(bm25_scores) > min(bm25_scores):
            bm25_norm = (bm25_scores - np.min(bm25_scores)) / (np.max(bm25_scores) - np.min(bm25_scores))
        else:
            bm25_norm = np.zeros_like(bm25_scores)
            
        if max(faiss_scores) > min(faiss_scores):
            faiss_norm = (faiss_scores - np.min(faiss_scores)) / (np.max(faiss_scores) - np.min(faiss_scores))
        else:
            faiss_norm = np.zeros_like(faiss_scores)
            
        hybrid_scores = 0.5 * bm25_norm + 0.5 * faiss_norm
        
        cat_scores = [(idx, hybrid_scores[idx]) for idx in cat_indices]
        cat_scores.sort(key=lambda x: x[1], reverse=True)
        
        top_indices = [x[0] for x in cat_scores[:top_k]]
        return [self.playbooks[i] for i in top_indices]
