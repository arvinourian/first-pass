import subprocess
import os

def export_to_html(notebook_path: str, output_dir: str):
    base_name = os.path.splitext(os.path.basename(notebook_path))[0]
    html_path = os.path.join(output_dir, f"{base_name}.html")
    subprocess.run(
        ["jupyter", "nbconvert", "--to", "html", notebook_path, "--output-dir", output_dir],
        check=True, capture_output=True, text=True
    )
    return html_path

def export_to_py(notebook_path: str, output_dir: str):
    base_name = os.path.splitext(os.path.basename(notebook_path))[0]
    py_path = os.path.join(output_dir, f"{base_name}.py")
    subprocess.run(
        ["jupyter", "nbconvert", "--to", "script", notebook_path, "--output-dir", output_dir],
        check=True, capture_output=True, text=True
    )
    return py_path

def export_to_md(notebook_path: str, output_dir: str):
    base_name = os.path.splitext(os.path.basename(notebook_path))[0]
    md_path = os.path.join(output_dir, f"{base_name}.md")
    subprocess.run(
        ["jupyter", "nbconvert", "--to", "markdown", notebook_path, "--output-dir", output_dir],
        check=True, capture_output=True, text=True
    )
    return md_path

def export_to_docx(notebook_path: str, output_dir: str):
    base_name = os.path.splitext(os.path.basename(notebook_path))[0]
    md_path = os.path.join(output_dir, f"{base_name}.md")
    if not os.path.exists(md_path):
        md_path = export_to_md(notebook_path, output_dir)
    docx_path = os.path.join(output_dir, f"{base_name}.docx")
    import pypandoc
    pypandoc.convert_file(md_path, 'docx', outputfile=docx_path)
    return docx_path

def export_to_pdf(notebook_path: str, output_dir: str):
    base_name = os.path.splitext(os.path.basename(notebook_path))[0]
    html_path = os.path.join(output_dir, f"{base_name}.html")
    if not os.path.exists(html_path):
        html_path = export_to_html(notebook_path, output_dir)
    pdf_path = os.path.join(output_dir, f"{base_name}.pdf")
    abs_html = os.path.abspath(html_path)
    abs_pdf = os.path.abspath(pdf_path)
    
    if os.name == 'nt':
        browser_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
        if not os.path.exists(browser_path):
            browser_path = "msedge"
    else:
        browser_path = "chromium"
        
    subprocess.run(
        [browser_path, "--headless", "--no-sandbox", "--disable-gpu", f"--print-to-pdf={abs_pdf}", abs_html],
        check=True, capture_output=True, text=True
    )
    return pdf_path
