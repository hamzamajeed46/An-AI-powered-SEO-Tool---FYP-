from fpdf import FPDF
from pymongo import MongoClient
import re
from flask import send_file
from io import BytesIO

# MongoDB connection
client = MongoClient("mongodb://localhost:27017/")
db = client["seotool"]

def strip_html(html_text):
    clean = re.compile('<.*?>')
    return re.sub(clean, '', html_text)
def render_html_text(pdf, html_text):
    # Convert <strong> and <b> to [B]...[/B]
    text = re.sub(r'<\s*(b|strong)\s*>', '[B]', html_text, flags=re.IGNORECASE)
    text = re.sub(r'<\s*/\s*(b|strong)\s*>', '[/B]', text, flags=re.IGNORECASE)

    # Convert <h1> to [H1], etc.
    for i in range(1, 4):
        text = re.sub(fr'<\s*h{i}\s*>', f'[H{i}]', text, flags=re.IGNORECASE)
        text = re.sub(fr'<\s*/\s*h{i}\s*>', f'[/H{i}]', text, flags=re.IGNORECASE)

    # Remove other HTML tags
    text = re.sub(r'<.*?>', '', text)

    # Split into tokens
    tokens = re.split(r'(\[/?[A-Z0-9]+\])', text)

    bold = False
    heading = None

    for token in tokens:
        if token == '[B]':
            bold = True
            continue
        elif token == '[/B]':
            bold = False
            continue
        elif token.startswith('[H') and token.endswith(']'):
            heading = int(token[2])  # e.g. [H2] → 2
            continue
        elif token.startswith('[/H') and token.endswith(']'):
            heading = None
            continue

        # Set font styles
        if heading:
            font_size = {1: 14, 2: 12, 3: 11}.get(heading, 10)
            pdf.set_font("Arial", "B", font_size)
            pdf.multi_cell(0, 8, token.strip())
            pdf.set_font("Arial", "", 10)
        elif bold:
            pdf.set_font("Arial", "B", 10)
            pdf.multi_cell(0, 8, token.strip())
            pdf.set_font("Arial", "", 10)
        else:
            pdf.multi_cell(0, 8, token.strip())



# PDF class
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

def render_backlinks_section(pdf, data):
    for idx, item in enumerate(data, start=1):
        item.pop("email", None)
        pdf.set_font("Arial", "B", 11)
        pdf.cell(0, 8, f"Backlink #{idx}", ln=True)
        pdf.set_font("Arial", "", 10)

        backlinks_data = item.get("backlinks", {})
        backlinks_data.pop("status", None)

        # Print main backlink fields
        for key, value in backlinks_data.items():
            if key != "backlinksList":
                pdf.set_font("Arial", "B", 10)
                pdf.cell(40, 8, f"{key}:", ln=0)
                pdf.set_font("Arial", "", 10)
                pdf.multi_cell(0, 8, str(value))

        # Print backlinksList
        links = backlinks_data.get("backlinksList", [])
        if links:
            pdf.ln(1)
            pdf.set_font("Arial", "B", 10)
            pdf.cell(0, 8, "Backlinks List:", ln=True)

            for i, link in enumerate(links, start=1):
                pdf.set_font("Arial", "B", 10)
                pdf.cell(20, 8, f"#{i}", ln=True)

                for key in ['url', 'title', 'domain_rating', 'target_url', 'anchor', 'summary']:
                    value = str(link.get(key, "")).encode("ascii", "ignore").decode("ascii")
                    pdf.set_font("Arial", "B", 10)
                    pdf.cell(35, 8, f"{key}:", ln=0)
                    pdf.set_font("Arial", "", 10)
                    pdf.multi_cell(0, 8, value)

                pdf.ln(1)

        # Add Recommendations
        if "recommendations" in item and item["recommendations"]:
            pdf.set_font("Arial", "B", 10)
            pdf.cell(0, 8, "Recommendations:", ln=True)
            pdf.set_font("Arial", "", 10)
            render_html_text(pdf, str(item["recommendations"]))
            pdf.ln(1)

        # Add Insights
        if "insights" in item and item["insights"]:
            pdf.set_font("Arial", "B", 10)
            pdf.cell(0, 8, "Insights:", ln=True)
            pdf.set_font("Arial", "", 10)
            render_html_text(pdf, str(item["insights"]))


            pdf.ln(1)

        pdf.ln(5)

def render_traffic_section(pdf, traffic_doc):
    if not traffic_doc:
        pdf.set_font("Arial", "", 10)
        pdf.cell(0, 10, "No traffic data found.", ln=True)
        return

    pdf.section_title("Traffic Overview")

    # Traffic summary
    traffic_info = traffic_doc.get("traffic", {})
    pdf.set_font("Arial", "B", 10)
    pdf.cell(50, 8, "Monthly Avg Traffic:", ln=0)
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 8, str(traffic_info.get("trafficMonthlyAvg", "N/A")), ln=1)

    pdf.set_font("Arial", "B", 10)
    pdf.cell(50, 8, "Monthly Avg Cost:", ln=0)
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 8, str(traffic_info.get("costMonthlyAvg", "N/A")), ln=1)

   

    # Traffic History
    history = traffic_info.get("traffic_history", [])
    if history:
        pdf.ln(2)
        pdf.set_font("Arial", "B", 11)
        pdf.cell(0, 8, "Traffic History:", ln=True)
        pdf.set_font("Arial", "", 10)
        for entry in history:
            date = entry.get("date", "N/A")
            organic = entry.get("organic", "N/A")
            pdf.cell(0, 8, f"{date}: {organic} organic visits", ln=True)

    # Top Pages
    top_pages = traffic_info.get("top_pages", [])
    if top_pages:
        pdf.ln(2)
        pdf.set_font("Arial", "B", 11)
        pdf.cell(0, 8, "Top Pages:", ln=True)
        pdf.set_font("Arial", "", 10)
        for page in top_pages:
            pdf.cell(0, 8, f"{page.get('url', '')} - {page.get('traffic', '')} visits ({round(page.get('share', 0), 2)}%)", ln=True)

    # Top Keywords
    top_keywords = traffic_info.get("top_keywords", [])
    if top_keywords:
        pdf.ln(2)
        pdf.set_font("Arial", "B", 11)
        pdf.cell(0, 8, "Top Keywords:", ln=True)
        pdf.set_font("Arial", "", 10)
        for kw in top_keywords:
            pdf.cell(0, 8, f"{kw.get('keyword', '')} (Pos: {kw.get('position', '')}) - {kw.get('traffic', '')} traffic", ln=True)

    # Top Countries
    top_countries = traffic_info.get("top_countries", [])
    if top_countries:
        pdf.ln(2)
        pdf.set_font("Arial", "B", 11)
        pdf.cell(0, 8, "Top Countries:", ln=True)
        pdf.set_font("Arial", "", 10)
        for c in top_countries:
            pdf.cell(0, 8, f"{c.get('country', '').upper()} - {round(c.get('share', 0), 2)}%", ln=True)

    # Recommendations
    rec = traffic_doc.get("recommendations")
    if rec:
        pdf.ln(2)
        pdf.set_font("Arial", "B", 10)
        pdf.cell(0, 8, "Recommendations:", ln=True)
        pdf.set_font("Arial", "", 10)
        render_html_text(pdf, rec)



def create_seo_report(website: str):
    pdf = PDF()
    pdf.add_page()

    backlinks = list(db.backlinks.find({"url": website}).sort("score", -1).limit(1))
    for b in backlinks:
        b.pop("_id", None)

    if backlinks:
        pdf.section_title(f"Backlinks for {website}")
        render_backlinks_section(pdf, backlinks)
    else:
        pdf.set_font("Arial", "", 10)
        pdf.cell(0, 10, f"No backlinks found for {website}", ln=True)

    
    # --- Traffic ---
    traffic_docs = list(db.traffic.find({"url": website}).sort("score", -1).limit(1))
    traffic_doc = traffic_docs[0] if traffic_docs else None

    if traffic_doc:    
        render_traffic_section(pdf, traffic_doc)
    else:
        pdf.set_font("Arial", "", 10)
        pdf.cell(0, 10, f"No Traffic data found for {website}", ln=True)
    # Generate PDF output as a string
    pdf_bytes = pdf.output(dest='S').encode('latin1')
    pdf.ln(10)

    # Write to BytesIO
    output = BytesIO(pdf_bytes)
    output.seek(0)

    return send_file(
        output,
        as_attachment=True,
        download_name="seo_backlinks_report.pdf",
        mimetype="application/pdf"
    )
