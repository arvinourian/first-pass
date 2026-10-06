# ⚡ First Pass: Autonomous Agentic RAG Data Scientist

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Live Demo](https://img.shields.io/badge/Live%20Demo-nourian.dev-FF4B4B?logo=streamlit&logoColor=white)](https://nourian.dev/projects#first-pass)
[![Google Cloud Run](https://img.shields.io/badge/Google%20Cloud-Run-4285F4?logo=googlecloud&logoColor=white)](https://cloud.google.com/run)
[![Gemini API](https://img.shields.io/badge/Powered%20by-Gemini%203.8%20Flash-8E75B2?logo=google&logoColor=white)](https://deepmind.google/technologies/gemini/)

**First Pass** is an autonomous AI data scientist designed to automate the heavy lifting of exploratory data analysis (EDA). Built with a specialized **4-stage Agentic RAG architecture**, the system dynamically ingests raw datasets, retrieves domain-specific analysis strategies, and generates fully executed Jupyter Notebooks without human intervention. 

Stop writing boilerplate code to clean missing values, parse dates, and plot correlation matrices. Upload your data, and let First Pass do the rest.

---

## 🎯 Key Capabilities

* **Agentic Playbook RAG:** Dynamically maps your dataset's statistical profile to a vector database of expert data science "playbooks" (e.g., retrieving advanced time-series analysis templates when temporal columns are detected).
* **Autonomous Execution:** A custom `NotebookBuilder` engine transpiles LLM-generated JSON execution plans directly into raw `.ipynb` files.
* **Multimodal Self-Correction:** An integrated Vision-Language Observer agent supervises notebook execution, iteratively detecting and patching Python runtime exceptions and malformed chart layouts on the fly.
* **Zero-Configuration UI:** A polished Streamlit interface offering multi-format data ingestion (`.csv`, `.parquet`, `.xlsx`) and instant reporting exports (HTML, PDF, DOCX).
* **Production-Ready:** Fully Dockerized and configured for zero-to-scale deployment on Google Cloud Run.

---

## 🧠 System Architecture

First Pass operates on a sequential, multi-agent pipeline designed to mimic the workflow of a human data scientist:

1. **Pass 0 (Domain Context):** Injects industry-specific KPIs and best practices based on the dataset's initial statistical profile.
2. **Pass 1 (Data Cleaning):** Intelligently handles missing values, standardizes types, and mathematically imputes anomalies in-memory.
3. **Pass 2 (Feature Engineering):** Mathematically transforms features (e.g., binning, scaling, temporal extraction) to surface deeper signals.
4. **Pass 3 (Analysis Planning):** Formulates targeted business questions and generates consultant-grade Matplotlib/Seaborn Python code using retrieved templates.
5. **Pass 4 (Observer Loop):** Safely executes the compiled notebook in a secure Jupyter kernel, utilizing an AI observer to catch and resolve tracebacks.

<details open>
<summary><b>View Pipeline Schematic</b></summary>

```mermaid
flowchart TD
    %% Inputs
    User(["User Uploads Dataset and Instructions"])
    
    %% Stage 1: Ingestion
    Ingest["Ingest and Profile Data (Stats, Types, Missing)"]
    Profile[("Raw Data Profile")]
    
    User --> Ingest
    Ingest --> Profile

    %% RAG Knowledge Base
    subgraph Knowledge_Base [Vector Playbook Index]
        DB_Domain[("Domain Playbooks")]
        DB_Clean[("Cleaning Playbooks")]
        DB_Eng[("Engineering Playbooks")]
        DB_Analysis[("Analysis Playbooks")]
    end

    %% Pass 0: Domain
    subgraph Pass_0 [Pass 0: Domain Context]
        P0_Query["Query: Profile + Intent"]
        P0_RAG{"Semantic Search"}
        P0_Context["Inject Industry KPIs and Context"]
        
        Profile --> P0_Query
        P0_Query --> P0_RAG
        DB_Domain -.-> P0_RAG
        P0_RAG --> P0_Context
    end

    %% Pass 1: Cleaning
    subgraph Pass_1 [Pass 1: Data Cleaning]
        P1_Query["Query: Missing/Dupes Stats"]
        P1_RAG{"Semantic Search"}
        P1_Plan["LLM generates Cleaning JSON"]
        P1_Exec["Execute Cleaning Code"]
        CleanProfile[("Cleaned Profile")]

        P0_Context --> P1_Query
        P1_Query --> P1_RAG
        DB_Clean -.-> P1_RAG
        P1_RAG --> P1_Plan
        P1_Plan --> P1_Exec
        P1_Exec --> CleanProfile
    end

    %% Pass 2: Engineering
    subgraph Pass_2 [Pass 2: Feature Engineering]
        P2_Query["Query: Cleaned Profile"]
        P2_RAG{"Semantic Search"}
        P2_Plan["LLM generates Engineering JSON"]
        
        CleanProfile --> P2_Query
        P2_Query --> P2_RAG
        DB_Eng -.-> P2_RAG
        P2_RAG --> P2_Plan
    end

    %% Pass 3: Analysis
    subgraph Pass_3 [Pass 3: Analysis Planning]
        P3_Query["Query: Cleaned Profile"]
        P3_RAG{"Semantic Search"}
        P3_Plan["LLM generates custom_code and Questions"]
        
        CleanProfile --> P3_Query
        P3_Query --> P3_RAG
        DB_Analysis -.-> P3_RAG
        P3_RAG --> P3_Plan
    end

    %% Pass 4: Observer & Execution
    subgraph Pass_4 [Pass 4: Assembly and Observer Loop]
        NB_Build["NotebookBuilder transpiles JSON to .ipynb"]
        Kernel["Execute Jupyter Kernel"]
        Observer{"Multimodal Observer Agent"}
        Fix["LLM patches syntax/layout errors"]
        
        P1_Plan --> NB_Build
        P2_Plan --> NB_Build
        P3_Plan --> NB_Build
        NB_Build --> Kernel
        Kernel --> Observer
        Observer -- "Detects Exception or Visual Flaw" --> Fix
        Fix --> Kernel
    end

    %% Output
    Export["Export HTML, PDF, Scripts, Datasets"]
    
    Observer -- "Clean Execution" --> Export
```
</details>

---

## 🚀 Getting Started

### Local Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/arvinourian/first-pass.git
   cd first-pass
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure the Environment:**
   Create a `.env` file in the root directory and add your Gemini API key:
   ```env
   GEMINI_API_KEY="your_gemini_api_key_here"
   ```

4. **Launch the Web Interface:**
   ```bash
   streamlit run app.py
   ```

### Docker Deployment (Google Cloud Run)

First Pass is production-ready for Google Cloud Run or any Linux-based container orchestration system. The included `Dockerfile` automatically installs the necessary Chromium and Pandoc system dependencies for headless PDF and DOCX reporting.

```bash
docker build -t first-pass .
docker run -p 8080:8080 --env GEMINI_API_KEY="your_api_key" first-pass
```

---

## 📁 Repository Structure

```text
First Pass/
├── app.py                           # Streamlit web application entrypoint
├── batch_run.py                     # Headless bulk execution script for pipelines
├── requirements.txt                 # Python dependencies
├── Dockerfile                       # Production containerization script
├── first_pass/                      # Core backend package
│   ├── ingest.py                    # Data loaders (CSV, Excel, Parquet)
│   ├── profile.py                   # Statistical dataset profiling 
│   ├── notebook_builder.py          # Jupyter transpiler and kernel execution
│   ├── export.py                    # Cross-platform HTML, PDF, DOCX utilities
│   ├── telemetry.py                 # Telemetry and logging module
│   ├── llm/                         # LLM agent logic (Planner, Observer, Prompts)
│   ├── retrieval/                   # FAISS vector database index for playbooks
│   └── templates/                   # Repository of Pandas/Seaborn code templates
├── playbooks/                       # Markdown vector index (Domain, Cleaning, Analysis)
├── Sample Inputs/                   # Example raw datasets and context guides
└── Sample Outputs/                  # Example generated HTML reports
```

## 📝 License
This project is open-source and available under the [MIT License](LICENSE).
