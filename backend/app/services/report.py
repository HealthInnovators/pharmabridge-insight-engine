from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from typing import Dict, Any, List


def build_report(data: Dict[str, Any], path: str):
    c = canvas.Canvas(path, pagesize=A4)
    width, height = A4

    def draw_heading(text: str, y: float):
        c.setFont("Helvetica-Bold", 14)
        c.drawString(2 * cm, y, text)
        return y - 0.8 * cm

    def draw_lines(lines: List[str], y: float):
        c.setFont("Helvetica", 10)
        for line in lines:
            c.drawString(2 * cm, y, line[:100])
            y -= 0.6 * cm
            if y < 2 * cm:
                c.showPage()
                y = height - 2 * cm
                c.setFont("Helvetica", 10)
        return y

    y = height - 2 * cm
    y = draw_heading("PharmaBridge Agentic Report", y)
    y = draw_lines([f"Query: {data.get('query','')}"], y)

    pubs = data.get("publications", [])
    if pubs:
        y = draw_heading("Publications", y)
        y = draw_lines([f"- {p['title']} — {p['journal']} ({p['year']})" for p in pubs], y)

    trials = data.get("trials", [])
    if trials:
        y = draw_heading("Clinical Trials", y)
        y = draw_lines([f"- {t['nct_id']} — {t['title']} [{t['phase']}] ({t['status']})" for t in trials], y)

    patents = data.get("patents", [])
    if patents:
        y = draw_heading("Patents", y)
        y = draw_lines([f"- {p['patent_number']} — {p['title']} (exp: {p['expiry']})" for p in patents], y)

    c.showPage()
    c.save()
