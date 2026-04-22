import io
import datetime
from fpdf import FPDF

class RadarCorePDF(FPDF):
    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.cell(0, 10, f"RadarCore Scan - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')} - Page {self.page_no()}", 0, 0, "C")

def generate_minimal_pdf(opportunity_item: dict) -> bytes:
    """
    Generates a single-page PDF containing the details of the opportunity.
    """
    pdf = RadarCorePDF()
    pdf.add_page("P", "A4")
    
    sym = opportunity_item.get("symbol", "UNKNOWN")
    m = opportunity_item.get("metrics", {})
    title = opportunity_item.get("title", sym)
    
    # Title
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, f"RadarCore - {title}", ln=True, align="C")
    pdf.ln(5)
    
    # Main indicators
    pdf.set_font("Arial", "", 12)
    bucket = m.get('bucket', 'PATTERN')
    conf = opportunity_item.get("confidence", getattr(opportunity_item, "confidence", 0))
    if type(conf)==dict: conf=0
    pdf.cell(0, 8, f"Symbol: {sym}", ln=True)
    pdf.cell(0, 8, f"Pattern: {bucket} ({conf:.1f}% confidence)", ln=True)
    
    phase = m.get('phase', 'NO_PATTERN')
    if phase not in ["NO_PATTERN", "N/A", "UNKNOWN"]:
        prog = m.get('progress_pct', 0)
        pdf.cell(0, 8, f"Phase: {phase} ({prog:.1f}% progress)", ln=True)
        
    price = m.get('current_price', 0)
    if price > 0:
        pdf.cell(0, 8, f"Current Price: ${price:.2f}", ln=True)
        
    drop = m.get('drop_from_high_pct', m.get('drop_pct', 0))
    rebound = m.get('rebound_pct', 0)
    pdf.cell(0, 8, f"Drop: {drop:.1f}% | Rebound: {rebound:.1f}%", ln=True)
    
    u3y = m.get('upside_to_ath3y', 0)
    u5y = m.get('upside_to_ath5y', 0)
    pdf.cell(0, 8, f"Upside (3Y): {u3y:.1f}% | Upside (5Y): {u5y:.1f}%", ln=True)
    
    # Earnings Warning
    risk = m.get("earnings_risk_level", "NONE")
    d_next = m.get("days_to_next_earnings", "N/A")
    if risk in ["HIGH", "MEDIUM"]:
        pdf.ln(5)
        pdf.set_text_color(220, 50, 50)
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 8, f"WARNING: Earnings in {d_next} days (Risk: {risk})", ln=True)
        pdf.set_text_color(0, 0, 0)
        
    enote = m.get("earnings_note")
    if enote:
        pdf.set_text_color(100, 100, 100)
        pdf.cell(0, 8, f"Note: {enote}", ln=True)
        pdf.set_text_color(0, 0, 0)
        
    # Return as bytes
    return bytes(pdf.output())

def generate_global_pdf(opportunities_list: list) -> bytes:
    """
    Generates a PDF spanning multiple pages (one per opportunity).
    """
    pdf = RadarCorePDF()
    
    if not opportunities_list:
        pdf.add_page("P", "A4")
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, "RadarCore - Global Scan", ln=True, align="C")
        pdf.ln(10)
        pdf.set_font("Arial", "", 12)
        pdf.cell(0, 10, "No opportunities to show.", ln=True, align="C")
        return bytes(pdf.output())
        
    for idx, item in enumerate(opportunities_list):
        if idx > 0:
            pass # add_page is called below anyway but we'll add one page per opportunity
        pdf.add_page("P", "A4")
        
        sym = item.get("symbol", "UNKNOWN")
        m = item.get("metrics", {})
        title = item.get("title", sym)
        
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, f"RadarCore - {title}", ln=True, align="C")
        pdf.ln(5)
        
        pdf.set_font("Arial", "", 12)
        bucket = m.get('bucket', 'PATTERN')
        conf = item.get("confidence", 0)
        pdf.cell(0, 8, f"Symbol: {sym}", ln=True)
        pdf.cell(0, 8, f"Pattern: {bucket} ({conf:.1f}% confidence)", ln=True)
        
        phase = m.get('phase', 'NO_PATTERN')
        if phase not in ["NO_PATTERN", "N/A", "UNKNOWN"]:
            prog = m.get('progress_pct', 0)
            pdf.cell(0, 8, f"Phase: {phase} ({prog:.1f}% progress)", ln=True)
            
        drop = m.get('drop_from_high_pct', m.get('drop_pct', 0))
        rebound = m.get('rebound_pct', 0)
        pdf.cell(0, 8, f"Drop: {drop:.1f}% | Rebound: {rebound:.1f}%", ln=True)
        
        risk = m.get("earnings_risk_level", "NONE")
        if risk in ["HIGH", "MEDIUM"]:
            d_next = m.get("days_to_next_earnings", "N/A")
            pdf.ln(5)
            pdf.set_text_color(220, 50, 50)
            pdf.set_font("Arial", "B", 12)
            pdf.cell(0, 8, f"WARNING: Earnings in {d_next} days", ln=True)
            pdf.set_text_color(0, 0, 0)
            
    return bytes(pdf.output())
