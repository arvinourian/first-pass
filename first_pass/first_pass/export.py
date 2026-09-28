import subprocess
import os

def export_notebook(notebook_path: str, output_dir: str):
    """Exports a jupyter notebook to multiple formats."""
    
    base_name = os.path.splitext(os.path.basename(notebook_path))[0]
    
    # 1. Export to Python script
    py_path = os.path.join(output_dir, f"{base_name}.py")
    try:
        # Uses nbconvert to script
        subprocess.run(
            ["jupyter", "nbconvert", "--to", "script", notebook_path, "--output-dir", output_dir],
            check=True,
            capture_output=True,
            text=True
        )
    except subprocess.CalledProcessError as e:
        print(f"Error exporting to python: {e.stderr}")
        
    # 2. Export to HTML (reading format)
    html_path = os.path.join(output_dir, f"{base_name}.html")
    try:
        subprocess.run(
            ["jupyter", "nbconvert", "--to", "html", notebook_path, "--output-dir", output_dir],
            check=True,
            capture_output=True,
            text=True
        )
    except subprocess.CalledProcessError as e:
        print(f"Error exporting to HTML: {e.stderr}")
        
    # 3. Export to Markdown
    md_path = os.path.join(output_dir, f"{base_name}.md")
    try:
        subprocess.run(
            ["jupyter", "nbconvert", "--to", "markdown", notebook_path, "--output-dir", output_dir],
            check=True,
            capture_output=True,
            text=True
        )
    except subprocess.CalledProcessError as e:
        print(f"Error exporting to Markdown: {e.stderr}")
        
    # 4. Export to DOCX
    docx_path = os.path.join(output_dir, f"{base_name}.docx")
    try:
        import pypandoc
        pypandoc.convert_file(md_path, 'docx', outputfile=docx_path)
    except Exception as e:
        print(f"Error exporting to DOCX: {e}")
        
    # 5. Export to PDF (via Edge)
    pdf_path = os.path.join(output_dir, f"{base_name}.pdf")
    try:
        # Get absolute paths for edge
        abs_html = os.path.abspath(html_path)
        abs_pdf = os.path.abspath(pdf_path)
        edge_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
        if not os.path.exists(edge_path):
            edge_path = "msedge" # fallback
        subprocess.run(
            [edge_path, "--headless", f"--print-to-pdf={abs_pdf}", abs_html],
            check=True,
            capture_output=True,
            text=True
        )
    except Exception as e:
        print(f"Error exporting to PDF via Edge: {e}")
        
    return py_path, html_path, md_path, docx_path, pdf_path
