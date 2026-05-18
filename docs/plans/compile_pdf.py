import os
import re
from fpdf import FPDF
from datetime import datetime

class EliteEstatePDF(FPDF):
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=20)
        
    def header(self):
        if self.page_no() == 1:
            return  # Skip cover page
        self.set_font("helvetica", "I", 8)
        self.set_text_color(100, 116, 139) # Slate 500
        self.cell(0, 10, "Elite Estate - PFE Technical Documentation", align="L")
        self.set_draw_color(226, 232, 240) # Slate 200
        self.line(10, 18, 200, 18)
        self.set_xy(10, 20)
        
    def footer(self):
        if self.page_no() == 1:
            return  # Skip cover page
        self.set_y(-15)
        self.set_font("helvetica", "I", 8)
        self.set_text_color(148, 163, 184) # Slate 400
        self.cell(0, 10, "Elite Estate Automation System", align="L")
        self.set_x(180)
        self.cell(0, 10, f"Page {self.page_no()}", align="R")

def clean_markdown_inline(text):
    """Clean and translate Unicode/Markdown formatting for standard Helvetica PDF compatibility."""
    if not text:
        return ""
        
    # Mapping of common unicode characters to clean ASCII representations
    unicode_replacements = {
        '\u2014': ' - ',  # em-dash
        '\u2013': '-',    # en-dash
        '\u201c': '"',    # left smart quote
        '\u201d': '"',    # right smart quote
        '\u2018': "'",    # left single quote
        '\u2019': "'",    # right single quote
        '\u2022': '*',    # bullet point
        '\u2026': '...',  # ellipsis
        '\u00a0': ' ',    # non-breaking space
        '\u00e9': 'e',    # e acute
        '\u00e8': 'e',    # e grave
        '\u00e0': 'a',    # a grave
        '\u00f9': 'u',    # u grave
        '\u00e7': 'c',    # c cedilla
        '\u20ac': 'EUR',  # Euro symbol
    }
    
    for uni_char, ascii_char in unicode_replacements.items():
        text = text.replace(uni_char, ascii_char)
        
    # Strip any remaining non-ASCII characters to prevent Helvetica mapping errors
    text = text.encode('ascii', errors='ignore').decode('ascii')
    
    # Process alerts and blocks
    text = text.replace("> [!NOTE]", "**NOTE:**")
    text = text.replace("> [!WARNING]", "**WARNING:**")
    text = text.replace("> [!IMPORTANT]", "**IMPORTANT:**")
    text = text.replace("> [!TIP]", "**TIP:**")
    text = text.replace("> [!CAUTION]", "**CAUTION:**")
    
    # Clean Markdown links [link_text](url) -> link_text (url)
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'**\1** (\2)', text)
    
    # Strip raw HTML elements or markers
    text = re.sub(r'<[^>]+>', '', text)
    return text.strip()

def compile_markdown_to_pdf(md_path, pdf_path):
    print(f"Reading markdown from {md_path}...")
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    pdf = EliteEstatePDF()
    
    # ------------------ COVER PAGE ------------------
    pdf.add_page()
    
    # Elegant Top Color Bar
    pdf.set_fill_color(37, 99, 235) # Blue 600
    pdf.rect(0, 0, 210, 15, "F")
    
    pdf.ln(30)
    
    # Title
    pdf.set_font("helvetica", "B", 32)
    pdf.set_text_color(30, 41, 59) # Slate 800
    pdf.cell(0, 15, "ELITE ESTATE", align="C")
    pdf.ln(18)
    
    pdf.set_font("helvetica", "B", 18)
    pdf.set_text_color(71, 85, 105) # Slate 600
    pdf.cell(0, 10, "AI-Driven Real Estate Automation Platform", align="C")
    pdf.ln(12)
    
    # Accent Line
    pdf.set_draw_color(37, 99, 235)
    pdf.set_line_width(1.5)
    pdf.line(60, pdf.get_y(), 150, pdf.get_y())
    pdf.set_line_width(0.2) # reset
    
    pdf.ln(25)
    
    # Details Table
    pdf.set_font("helvetica", "", 12)
    pdf.set_text_color(30, 41, 59)
    
    details = [
        ("Document Type:", "PFE Technical & Architectural Documentation"),
        ("Project Type:", "End-of-Study Project (Projet de Fin d'Etudes - PFE)"),
        ("Institution:", "Higher Institute of Technological Studies (ISET)"),
        ("Academic Year:", "2025-2026"),
        ("Date Prepared:", "May 2026"),
        ("Development Team:", "Member A (Platform) & Member B (AI & n8n)")
    ]
    
    pdf.set_x(25)
    with pdf.table(col_widths=(45, 115), borders_layout="NONE", line_height=8) as table:
        for label, val in details:
            row = table.row()
            pdf.set_font("helvetica", "B", 11)
            pdf.set_text_color(71, 85, 105)
            row.cell(label)
            pdf.set_font("helvetica", "", 11)
            pdf.set_text_color(30, 41, 59)
            row.cell(val)
            
    pdf.ln(30)
    
    # Professional Box / Statement
    pdf.set_fill_color(248, 250, 252) # Slate 50
    pdf.set_draw_color(226, 232, 240) # Slate 200
    pdf.rect(20, pdf.get_y(), 170, 25, "FD")
    
    pdf.set_xy(25, pdf.get_y() + 5)
    pdf.set_font("helvetica", "I", 9.5)
    pdf.set_text_color(71, 85, 105)
    pdf.multi_cell(160, 5, "This document presents the complete technical architecture, data schema, role-based workflows, and AI integration mechanisms built for the Elite Estate automation platform.", align="C")
    
    # ------------------ END COVER PAGE ------------------
    
    # Split content by lines
    lines = content.split('\n')
    
    pdf.add_page()
    pdf.set_font("helvetica", "", 10)
    pdf.set_text_color(30, 41, 59)
    
    i = 0
    in_code_block = False
    code_content = []
    
    while i < len(lines):
        line = lines[i]
        
        # Skip top title and metadata from source MD to avoid duplication on Page 2
        if i < 11 and (line.startswith("# ") or line.startswith("## ") or line.startswith("**Project Type**") or line.startswith("**Institution**")):
            i += 1
            continue
            
        # Code block detection
        if line.strip().startswith("```"):
            if not in_code_block:
                in_code_block = True
                code_content = []
            else:
                in_code_block = False
                
                # Render code block
                pdf.set_font("courier", "", 8.5)
                pdf.set_fill_color(241, 245, 249) # Slate 100
                pdf.set_text_color(30, 41, 59)
                
                code_str = "\n".join(code_content)
                code_str = clean_markdown_inline(code_str)
                pdf.multi_cell(0, 4, code_str, border=1, fill=True)
                pdf.set_x(pdf.l_margin)
                pdf.ln(4)
                
                # Reset fonts
                pdf.set_font("helvetica", "", 10)
            i += 1
            continue
            
        if in_code_block:
            code_content.append(line)
            i += 1
            continue
            
        # Headings
        if line.startswith("# "):
            pdf.ln(6)
            pdf.set_font("helvetica", "B", 18)
            pdf.set_text_color(30, 41, 59)
            pdf.cell(0, 10, clean_markdown_inline(line[2:]))
            pdf.ln(10)
            
            # Accent underline
            pdf.set_draw_color(37, 99, 235)
            pdf.set_line_width(1.0)
            pdf.line(pdf.get_x(), pdf.get_y(), pdf.get_x() + 190, pdf.get_y())
            pdf.set_line_width(0.2)
            pdf.ln(4)
            i += 1
            continue
            
        if line.startswith("## "):
            pdf.ln(5)
            pdf.set_font("helvetica", "B", 14)
            pdf.set_text_color(30, 41, 59)
            pdf.cell(0, 8, clean_markdown_inline(line[3:]))
            pdf.ln(10)
            i += 1
            continue
            
        if line.startswith("### "):
            pdf.ln(4)
            pdf.set_font("helvetica", "B", 11.5)
            pdf.set_text_color(71, 85, 105)
            pdf.cell(0, 7, clean_markdown_inline(line[4:]))
            pdf.ln(9)
            i += 1
            continue
            
        if line.startswith("#### "):
            pdf.ln(3)
            pdf.set_font("helvetica", "B", 10.5)
            pdf.set_text_color(100, 116, 139)
            pdf.cell(0, 6, clean_markdown_inline(line[5:]))
            pdf.ln(8)
            i += 1
            continue
            
        # Horizontal rule
        if line.strip() == "---":
            pdf.ln(4)
            pdf.set_draw_color(226, 232, 240)
            pdf.line(10, pdf.get_y(), 200, pdf.get_y())
            pdf.ln(4)
            i += 1
            continue
            
        # Tables detection
        if line.strip().startswith("|") and i + 1 < len(lines) and lines[i+1].strip().startswith("|---"):
            table_lines = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                table_lines.append(lines[i])
                i += 1
                
            headers = [clean_markdown_inline(h.strip()) for h in table_lines[0].split('|')[1:-1]]
            rows = []
            for tl in table_lines[2:]:
                rows.append([clean_markdown_inline(c.strip()) for c in tl.split('|')[1:-1]])
                
            num_cols = len(headers)
            col_widths = [190 / num_cols] * num_cols
            if num_cols == 2:
                col_widths = [45, 145]
            elif num_cols == 3:
                col_widths = [40, 75, 75]
            elif num_cols == 4:
                col_widths = [30, 45, 85, 30]
                
            pdf.set_font("helvetica", "", 9)
            with pdf.table(col_widths=col_widths, borders_layout="HORIZONTAL_LINES", line_height=7) as table:
                header_row = table.row()
                pdf.set_font("helvetica", "B", 9)
                pdf.set_text_color(255, 255, 255)
                pdf.set_fill_color(30, 41, 59)
                for h in headers:
                    header_row.cell(h)
                    
                pdf.set_font("helvetica", "", 8.5)
                pdf.set_text_color(30, 41, 59)
                for idx, r in enumerate(rows):
                    row = table.row()
                    if idx % 2 == 1:
                        pdf.set_fill_color(248, 250, 252)
                    else:
                        pdf.set_fill_color(255, 255, 255)
                    for val in r:
                        row.cell(val)
            pdf.ln(4)
            pdf.set_font("helvetica", "", 10)
            continue
            
        # Lists
        if line.strip().startswith("- ") or line.strip().startswith("* "):
            bullet_char = "*"
            list_text = line.strip()[2:]
            list_text = clean_markdown_inline(list_text)
            pdf.set_x(15)
            pdf.set_font("helvetica", "B", 10)
            pdf.cell(5, 5, f"{bullet_char}", align="C")
            pdf.set_font("helvetica", "", 10)
            pdf.set_text_color(30, 41, 59)
            pdf.multi_cell(0, 5, list_text)
            pdf.set_x(pdf.l_margin)
            i += 1
            continue
            
        if re.match(r'^\s*(\d+)\.\s+', line):
            match = re.match(r'^\s*(\d+)\.\s+', line)
            num = match.group(1)
            list_text = line[match.end():]
            list_text = clean_markdown_inline(list_text)
            pdf.set_x(15)
            pdf.set_font("helvetica", "B", 10)
            pdf.cell(6, 5, f"{num}.", align="L")
            pdf.set_font("helvetica", "", 10)
            pdf.set_text_color(30, 41, 59)
            pdf.multi_cell(0, 5, list_text)
            pdf.set_x(pdf.l_margin)
            i += 1
            continue
            
        # Alerts / Callouts
        if line.strip().startswith(">"):
            alert_lines = []
            while i < len(lines) and lines[i].strip().startswith(">"):
                alert_lines.append(lines[i].strip()[1:].strip())
                i += 1
                
            alert_text = " ".join(alert_lines)
            alert_text = clean_markdown_inline(alert_text)
            
            pdf.set_fill_color(248, 250, 252)
            pdf.set_draw_color(37, 99, 235)
            pdf.set_text_color(71, 85, 105)
            
            pdf.set_font("helvetica", "I", 9.5)
            x_start = pdf.get_x()
            y_start = pdf.get_y()
            
            # Simple gray background box with left blue line
            pdf.rect(x_start + 2, y_start, 186, 16, "DF")
            pdf.set_xy(x_start + 6, y_start + 3)
            pdf.multi_cell(180, 5, alert_text)
            pdf.set_x(pdf.l_margin)
            pdf.ln(5)
            
            pdf.set_font("helvetica", "", 10)
            pdf.set_text_color(30, 41, 59)
            continue
            
        # Blank lines
        if not line.strip():
            pdf.ln(2.5)
            i += 1
            continue
            
        # Regular paragraph
        paragraph_text = clean_markdown_inline(line.strip())
        pdf.set_font("helvetica", "", 10)
        pdf.set_text_color(30, 41, 59)
        try:
            pdf.multi_cell(0, 5.5, paragraph_text)
            pdf.set_x(pdf.l_margin)
        except Exception as e:
            print(f"FAILED on line {i+1}: {repr(line)}")
            print(f"Cleaned: {repr(paragraph_text)}")
            print(f"Coords: x={pdf.get_x()}, y={pdf.get_y()}, page={pdf.page_no()}")
            raise e
        i += 1

    # Save
    print(f"Saving compiled PDF to {pdf_path}...")
    pdf.output(pdf_path)
    print("Compilation successful!")

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    md_file = os.path.join(base_dir, "PFE_Documentation_EliteEstate.md")
    output_pdf = os.path.join(os.path.dirname(base_dir), "PFE_Documentation_EliteEstate.pdf")
    
    compile_markdown_to_pdf(md_file, output_pdf)
