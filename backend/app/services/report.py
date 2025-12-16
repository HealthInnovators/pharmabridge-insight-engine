from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from typing import Dict, Any, List
import datetime


def build_report(data: Dict[str, Any], path: str):
    print(f"Starting report generation for path: {path}")
    print(f"Available data keys: {list(data.keys())}")
    
    try:
        c = canvas.Canvas(path, pagesize=A4)
        width, height = A4

        def draw_heading(text: str, y: float, level: int = 1):
            font_size = 16 if level == 1 else 14 if level == 2 else 12
            c.setFont("Helvetica-Bold", font_size)
            c.drawString(2 * cm, y, text)
            return y - (1.2 * cm if level == 1 else 0.8 * cm)

        def draw_lines(lines: List[str], y: float, indent: int = 0):
            c.setFont("Helvetica", 10)
            for line in lines:
                if not line:
                    y -= 0.4 * cm  # Add some space for empty lines
                    continue
                    
                # Handle line breaks in the text
                max_line_length = 90 - (indent * 3)  # Adjust for indentation
                line_parts = [line[i:i+max_line_length] for i in range(0, len(line), max_line_length)]
                
                for part in line_parts:
                    if y < 3 * cm:  # Leave space for footer
                        c.showPage()
                        y = height - 2 * cm
                        c.setFont("Helvetica", 10)
                    
                    # Apply indentation
                    indent_str = " " * indent * 3
                    c.drawString(2 * cm + (indent * 0.5 * cm), y, f"{indent_str}{part}")
                    y -= 0.5 * cm
                    
            return y

        # Start with a title page
        y = height - 5 * cm
        c.setFont("Helvetica-Bold", 20)
        c.drawCentredString(width/2, y, "PharmaBridge Insights Report")
        y -= 1.5 * cm
        
        c.setFont("Helvetica", 12)
        y = draw_lines(["", f"Generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ""], y)
        
        # Add a new page for the content
        c.showPage()
        y = height - 2 * cm
        
        # Add query section
        query = data.get('query', 'No query provided')
        y = draw_heading("Query", y, 2)
        y = draw_lines([query, ""], y, 0)

        sources = data.get("sources", {})
        if isinstance(sources, dict) and sources:
            y = draw_heading("Data Sources", y, 2)
            lines = []
            for label, key in [
                ("Publications", "publications"),
                ("Clinical Trials", "trials"),
                ("Patents", "patents"),
                ("Market (IQVIA)", "iqvia"),
                ("EXIM", "exim"),
                ("Internal Knowledge", "internal_docs"),
                ("Web Intelligence", "web_intel"),
            ]:
                meta = sources.get(key)
                if isinstance(meta, dict) and meta.get("source"):
                    lines.append(f"{label}: {meta.get('source')}")
            generated_at = sources.get("generated_at")
            if isinstance(generated_at, str) and generated_at:
                lines.append(f"Generated at: {generated_at}")
            if lines:
                y = draw_lines(lines + [""], y, 1)
        
        # Helper function to safely get list data
        def safe_get_list(data, key):
            items = data.get(key, [])
            return items if isinstance(items, list) else []
            
        # Add each section if data exists
        sections = [
            ("publications", "Publications", lambda p: f"{p.get('title', 'No title')} — {p.get('journal', 'No journal')} ({p.get('year', 'N/A')})"),
            ("trials", "Clinical Trials", lambda t: f"{t.get('nct_id', 'NCTXXXX')} — {t.get('title', 'No title')} [{t.get('phase', 'Phase N/A')}] ({t.get('status', 'Status N/A')})"),
            ("patents", "Patents", lambda p: f"{p.get('patent_number', 'N/A')} — {p.get('title', 'No title')} (exp: {p.get('expiry', 'N/A')})"),
        ]
        
        for key, title, formatter in sections:
            items = safe_get_list(data, key)
            if items:
                y = draw_heading(title, y, 2)
                y = draw_lines([formatter(item) for item in items], y, 1)
                y = draw_lines([""], y)  # Add some space after section
        
        # Add IQVIA data if available
        iqvia = data.get("iqvia", {})
        if iqvia:
            y = draw_heading("Market Insights (IQVIA)", y, 2)
            lines = []
            if 'therapy_area' in iqvia:
                lines.append(f"Therapy Area: {iqvia['therapy_area']}")
            if 'cagr' in iqvia:
                lines.append(f"CAGR: {iqvia['cagr']}%")
            if 'market_size' in iqvia:
                lines.append(f"Market Size: ${iqvia['market_size']}M")
                
            competitors = iqvia.get('competitors', [])
            if competitors:
                lines.append("")
                lines.append("Key Competitors:")
                for comp in competitors[:5]:  # Limit to top 5
                    lines.append(f"- {comp.get('name', 'N/A')}: {comp.get('market_share', 0) * 100:.1f}%")
            
            y = draw_lines(lines, y, 1)
            y = draw_lines([""], y)  # Add some space after section
        
        # Add EXIM data if available
        exim = data.get("exim", {})
        if exim:
            y = draw_heading("EXIM Trends", y, 2)
            lines = []
            if 'import_dependency' in exim:
                lines.append(f"Import Dependency: {exim['import_dependency'] * 100:.1f}%")
                
            exporters = exim.get('top_exporters', [])
            if exporters:
                lines.append("")
                lines.append("Top Exporting Countries:")
                for exp in exporters[:5]:  # Limit to top 5
                    lines.append(f"- {exp.get('country', 'N/A')}: {exp.get('share', 'N/A')}")
            
            y = draw_lines(lines, y, 1)
            y = draw_lines([""], y)  # Add some space after section
        
        # Add Internal Documents if available
        internal_docs = safe_get_list(data, "internal_docs")
        if internal_docs:
            y = draw_heading("Internal Knowledge", y, 2)
            y = draw_lines([f"- {doc.get('title', 'No title')}: {doc.get('summary', 'No summary')[:100]}" 
                          for doc in internal_docs], y, 1)
            y = draw_lines([""], y)  # Add some space after section
        
        # Add Web Intelligence if available
        web_intel = safe_get_list(data, "web_intel")
        if web_intel:
            y = draw_heading("Web Intelligence", y, 2)
            y = draw_lines([f"- {item.get('source', 'Source')}: {item.get('summary', 'No summary')[:100]}" 
                          for item in web_intel[:5]], y, 1)  # Limit to 5 items
            y = draw_lines([""], y)  # Add some space after section
        
        # Add Insights and Flags if available
        insights = safe_get_list(data, "insights")
        if insights:
            y = draw_heading("Key Insights", y, 2)
            y = draw_lines([f"• {insight}" for insight in insights], y, 1)
        
        # Add footer
        c.setFont("Helvetica", 8)
        c.drawCentredString(width/2, 1 * cm, "Confidential - PharmaBridge Insights")
        
        c.showPage()
        c.save()
        print(f"Successfully generated report at: {path}")
        
    except Exception as e:
        print(f"Error generating report: {str(e)}")
        import traceback
        traceback.print_exc()
        raise
