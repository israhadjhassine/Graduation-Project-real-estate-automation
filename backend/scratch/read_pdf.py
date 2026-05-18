import sys
import os

pdf_path = r"c:\Users\jesse\Desktop\study\iset_me\terminal\stage_pfe\real-estate-automation\real-estate-automation\docs\PFE_Documentation_EliteEstate.pdf"
output_path = r"c:\Users\jesse\Desktop\study\iset_me\terminal\stage_pfe\real-estate-automation\real-estate-automation\backend\scratch\pdf_text.txt"

print(f"Checking PDF at: {pdf_path}")
if not os.path.exists(pdf_path):
    print("PDF not found!")
    sys.exit(1)

try:
    import pypdf
    print("pypdf is installed, using it.")
    reader = pypdf.PdfReader(pdf_path)
    text = ""
    for idx, page in enumerate(reader.pages):
        text += f"\n--- PAGE {idx+1} ---\n"
        text += page.extract_text()
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"Extracted to {output_path}")
except ImportError:
    try:
        import PyPDF2
        print("PyPDF2 is installed, using it.")
        reader = PyPDF2.PdfReader(pdf_path)
        text = ""
        for idx, page in enumerate(reader.pages):
            text += f"\n--- PAGE {idx+1} ---\n"
            text += page.extract_text()
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"Extracted to {output_path}")
    except ImportError:
        try:
            import pdfminer
            from pdfminer.high_level import extract_text
            print("pdfminer is installed, using it.")
            text = extract_text(pdf_path)
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(text)
            print(f"Extracted to {output_path}")
        except ImportError:
            print("No PDF reader libraries installed!")
