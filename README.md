# ðŸš€ First Pass

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
â”œâ”€â”€ app.py                           # The main Streamlit web application interface
â”œâ”€â”€ batch_run.py                     # Script for headless bulk evaluation on sample datasets
â”œâ”€â”€ first_pass/                      # Core Python package backend
â”‚   â”œâ”€â”€ ingest.py                    # Data loading logic
â”‚   â”œâ”€â”€ profile.py                   # Data profiling (types, missing values, stats)
â”‚   â”œâ”€â”€ notebook_builder.py          # Jupyter notebook generation and execution engine
â”‚   â”œâ”€â”€ export.py                    # HTML, PDF, DOCX, and script export utilities
â”‚   â”œâ”€â”€ telemetry.py                 # Telemetry and logging module
â”‚   â”œâ”€â”€ llm/                         # LLM agent logic (Planner, Synthesis, Observer)
â”‚   â”œâ”€â”€ retrieval/                   # Playbook index and semantic RAG search
â”‚   â””â”€â”€ templates/                   # Repository of analysis and cleaning code templates
â”œâ”€â”€ playbooks/                       # Markdown files containing expert domain knowledge and RAG schemas
â”œâ”€â”€ Sample Inputs/                   # Example raw datasets and context files
â”œâ”€â”€ Sample Outputs/                  # Example generated HTML reports
â”œâ”€â”€ tests/                           # Unit tests
â””â”€â”€ temp/                            # Temporary directory for intermediate notebook execution
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
