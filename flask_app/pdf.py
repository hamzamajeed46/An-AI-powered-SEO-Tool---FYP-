from fpdf import FPDF, HTMLMixin
import re

class PDF(FPDF):
    def __init__(self):
        super().__init__('P', 'mm', 'A4')
        self.set_auto_page_break(auto=True, margin=15)
        self.set_font("Arial", size=10)

    def header(self):
        self.set_font("Arial", "B", 16)
        self.cell(0, 10, "SEO Report", ln=True, align="C")
        self.ln(10)

    def section_title(self, title):
        self.set_font("Arial", "B", 12)
        self.set_text_color(0, 0, 128)
        self.cell(0, 10, title, ln=True)
        self.set_text_color(0, 0, 0)
        self.ln(2)

    def write_html(self, html_text):
        html_text = html_text.replace('\n', '')  # Remove newlines for simplicity
        tokens = re.split(r'(<.*?>)', html_text)
        bold = italic = underline = False

        for token in tokens:
            if token == '':
                continue
            if token.startswith('<'):
                tag = token.lower()
                if tag == '<b>' or tag == '<strong>':
                    bold = True
                    self.set_font(style=("B" if bold else "") + ("I" if italic else "") + ("U" if underline else ""))
                elif tag == '</b>' or tag == '</strong>':
                    bold = False
                    self.set_font(style=("B" if bold else "") + ("I" if italic else "") + ("U" if underline else ""))
                elif tag == '<i>' or tag == '<em>':
                    italic = True
                    self.set_font(style=("B" if bold else "") + ("I" if italic else "") + ("U" if underline else ""))
                elif tag == '</i>' or tag == '</em>':
                    italic = False
                    self.set_font(style=("B" if bold else "") + ("I" if italic else "") + ("U" if underline else ""))
                elif tag == '<u>':
                    underline = True
                    self.set_font(style=("B" if bold else "") + ("I" if italic else "") + ("U" if underline else ""))
                elif tag == '</u>':
                    underline = False
                    self.set_font(style=("B" if bold else "") + ("I" if italic else "") + ("U" if underline else ""))
                elif tag == '<br>' or tag == '<br/>':
                    self.ln(5)
                elif tag == '<p>':
                    self.ln(4)
                elif tag == '</p>':
                    self.ln(4)
                # Add more tags as needed
            else:
                self.multi_cell(0, 8, token)
