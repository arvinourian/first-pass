# First Pass

**First Pass** is an automated AI data scientist designed to perform the initial heavy lifting of data exploration. Upload a dataset, and First Pass will ingest, profile, clean, engineer features, and analyze the data, ultimately generating a fully executed Jupyter Notebook and comprehensive multi-format reports.

## Features

- **Multi-Format Ingestion**: Supports `.csv`, `.xlsx`, `.xls`, and `.parquet` files.
- **4-Stage AI Pipeline**:
  - **Domain Context (Pass 0)**: Injects industry-specific KPIs and best practices based on the dataset's profile.
  - **Data Cleaning (Pass 1)**: Intelligently handles missing values, standardizes date formats, and removes duplicates.
  - **Feature Engineering (Pass 2)**: Mathematically transforms data (e.g., binning, scaling, extracting time features) before analysis.
  - **Analysis Planning (Pass 3)**: Formulates targeted business questions and generates consultant-grade Matplotlib/Seaborn Python code using specialized RAG playbooks.
- **Observer Loop (Pass 4)**: A multimodal vision agent that supervises the notebook execution, catching syntax errors (like `IndentationError`) and iteratively refining chart layouts.
- **Rich Exports**: Download the executed Jupyter Notebook (`.ipynb`), Python script (`.py`), HTML Report, PDF, DOCX, or the finalized cleaned datasets.

## Directory Structure

```text
First Pass/
|-- app.py                           # The main Streamlit web application interface
|-- batch_run.py                     # Script for headless bulk evaluation on sample datasets
|-- first_pass/                      # Core Python package backend
|   |-- ingest.py                    # Data loading logic
|   |-- profile.py                   # Data profiling (types, missing values, stats)
|   |-- notebook_builder.py          # Jupyter notebook generation and execution engine
|   |-- export.py                    # HTML, PDF, DOCX, and script export utilities
|   |-- telemetry.py                 # Telemetry and logging module
|   |-- llm/                         # LLM agent logic (Planner, Synthesis, Observer)
|   |-- retrieval/                   # Playbook index and semantic RAG search
|   `-- templates/                   # Repository of analysis and cleaning code templates
|-- playbooks/                       # Markdown files containing expert domain knowledge and RAG schemas
|-- Sample Inputs/                   # Example raw datasets and context files
|-- Sample Outputs/                  # Example generated HTML reports
|-- tests/                           # Unit tests
`-- temp/                            # Temporary directory for intermediate notebook execution
```

## Setup & Installation

1. Ensure you have Python 3.10+ installed.
2. Install dependencies (e.g. `streamlit`, `pandas`, `matplotlib`, `seaborn`, `nbformat`, `nbconvert`).
3. Add your Gemini API key to a `.env` file in the root directory:
   ```env
   GEMINI_API_KEY="your_api_key_here"
   ```

## Usage

### Web Interface
To launch the interactive web application, run:
```bash
streamlit run app.py
```

### Batch Processing
To run the automated pipeline across the datasets in `Sample Inputs` and output reports to `Sample Outputs`, execute:
```bash
python batch_run.py
```

## Architecture

First Pass uses a dynamic **Retrieval-Augmented Generation (RAG)** architecture. When a dataset is uploaded, it generates a statistical profile. This profile is used to query the `playbooks/` folder, pulling the most relevant domain knowledge, cleaning strategies, and analysis templates. The LLM Planner then constructs a JSON plan, which the `NotebookBuilder` transpiles into an `.ipynb` file. The execution environment catches warnings and errors, which are sent to the Observer agent for self-correction before final export.


### Pipeline Schematic

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


