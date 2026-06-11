import os
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas

# Luxury Branding Palette
COLOR_PRIMARY = colors.HexColor("#121212")   # Rich charcoal
COLOR_SECONDARY = colors.HexColor("#C5A880") # Brass / Gold
COLOR_BG_LIGHT = colors.HexColor("#FAF8F5")  # Warm cream background for panels
COLOR_TEXT_MUTED = colors.HexColor("#555555")# Muted gray text
COLOR_WHITE = colors.HexColor("#FFFFFF")
COLOR_BORDER = colors.HexColor("#EAE7E2")

class NumberedCanvas(canvas.Canvas):
    """
    Canvas to calculate total page count dynamically and add luxury headers/footers.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pages = []

    def showPage(self):
        self.pages.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self.pages)
        for page in self.pages:
            self.__dict__.update(page)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, total_pages):
        self.saveState()
        
        # Draw background tint on page 1 for luxury cover page
        if self._pageNumber == 1:
            self.setFillColor(COLOR_BG_LIGHT)
            self.rect(0, 0, 612, 792, fill=True, stroke=False)
            
            # Draw elegant vertical brass line on cover
            self.setStrokeColor(COLOR_SECONDARY)
            self.setLineWidth(2)
            self.line(54, 54, 54, 738)
            
        else:
            # Running header for inner pages
            self.setFont("Helvetica", 8)
            self.setFillColor(COLOR_TEXT_MUTED)
            self.drawString(54, 750, "THE DESIGN CONCIERGE  |  PROJECT INTELLIGENCE REPORT")
            self.setStrokeColor(COLOR_BORDER)
            self.setLineWidth(0.5)
            self.line(54, 742, 558, 742)
            
            # Running footer
            page_str = f"Page {self._pageNumber} of {total_pages}"
            self.drawRightString(558, 40, page_str)
            self.drawString(54, 40, "Confidential - Prepared for Interior Designer Review")
            self.line(54, 50, 558, 50)
            
        self.restoreState()


def generate_intelligence_report(lead_data: dict, output_dir: str = "static/reports") -> str:
    """
    Generates an elegant, luxury-branded PDF report for the designer.
    Returns the file path of the generated PDF.
    """
    os.makedirs(output_dir, exist_ok=True)
    file_path = os.path.join(output_dir, f"report_{lead_data['id']}.pdf")
    
    # Page setup - 0.75 in (54 pt) margins
    doc = SimpleDocTemplate(
        file_path,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )
    
    styles = getSampleStyleSheet()
    
    # Custom Luxury Typography Styles
    title_style = ParagraphStyle(
        "CoverTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=28,
        leading=34,
        textColor=COLOR_PRIMARY,
        spaceAfter=10
    )
    
    subtitle_style = ParagraphStyle(
        "CoverSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=12,
        leading=16,
        textColor=COLOR_SECONDARY,
        spaceAfter=30
    )
    
    h1_style = ParagraphStyle(
        "SectionHeading",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=18,
        leading=22,
        textColor=COLOR_PRIMARY,
        spaceBefore=15,
        spaceAfter=10,
        keepWithNext=True
    )
    
    h2_style = ParagraphStyle(
        "SubSectionHeading",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=16,
        textColor=COLOR_SECONDARY,
        spaceBefore=10,
        spaceAfter=6,
        keepWithNext=True
    )
    
    body_style = ParagraphStyle(
        "ReportBody",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10,
        leading=14,
        textColor=COLOR_PRIMARY,
        spaceAfter=8
    )
    
    meta_label_style = ParagraphStyle(
        "MetaLabel",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=10,
        leading=12,
        textColor=COLOR_TEXT_MUTED
    )
    
    meta_val_style = ParagraphStyle(
        "MetaVal",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10,
        leading=12,
        textColor=COLOR_PRIMARY
    )
    
    bullet_style = ParagraphStyle(
        "BulletText",
        parent=body_style,
        leftIndent=15,
        firstLineIndent=-10,
        spaceAfter=4
    )
    
    story = []
    
    # ------------------ COVER PAGE ------------------
    story.append(Spacer(1, 100))
    story.append(Paragraph("THE DESIGN CONCIERGE", subtitle_style))
    story.append(Paragraph("Project Intelligence<br/>Briefing Report", title_style))
    story.append(Paragraph("Automated Pre-Discovery Consultation Assessment", subtitle_style))
    story.append(Spacer(1, 120))
    
    # Project Metadata Block
    client_name = lead_data.get("name") or "Unnamed Lead"
    client_email = lead_data.get("email") or "No Email Provided"
    client_phone = lead_data.get("phone") or "No Phone Provided"
    location = lead_data.get("location") or "Unspecified Location"
    room_type = lead_data.get("room_type") or "Unspecified Space"
    date_str = datetime.now().strftime("%B %d, %Y")
    
    meta_data = [
        [Paragraph("Client Name:", meta_label_style), Paragraph(client_name, meta_val_style)],
        [Paragraph("Email Address:", meta_label_style), Paragraph(client_email, meta_val_style)],
        [Paragraph("Phone Number:", meta_label_style), Paragraph(client_phone, meta_val_style)],
        [Paragraph("Project Location:", meta_label_style), Paragraph(location, meta_val_style)],
        [Paragraph("Target Space:", meta_label_style), Paragraph(room_type, meta_val_style)],
        [Paragraph("Assessment Date:", meta_label_style), Paragraph(date_str, meta_val_style)]
    ]
    
    meta_table = Table(meta_data, colWidths=[120, 300])
    meta_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LINEBELOW', (0,0), (-1,-1), 0.5, COLOR_BORDER),
    ]))
    
    story.append(meta_table)
    story.append(PageBreak())
    
    # ------------------ SECTION 1: EXEC SUMMARY & READINESS ------------------
    story.append(Paragraph("Executive Lead Summary", h1_style))
    story.append(Spacer(1, 5))
    
    readiness_score = lead_data.get("readiness_score", 0)
    dna = lead_data.get("design_dna") or "Not Determined"
    
    # Readiness summary card layout
    summary_data = [
        [
            Paragraph("<b>Design DNA</b><br/><font color='#C5A880' size='14'><b>" + dna + "</b></font>", body_style),
            Paragraph("<b>Project Readiness Score</b><br/><font color='#C5A880' size='22'><b>" + str(readiness_score) + "/100</b></font>", body_style)
        ]
    ]
    summary_table = Table(summary_data, colWidths=[250, 250])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), COLOR_BG_LIGHT),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOX', (0,0), (-1,-1), 1, COLOR_BORDER),
        ('TOPPADDING', (0,0), (-1,-1), 15),
        ('BOTTOMPADDING', (0,0), (-1,-1), 15),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 15))
    
    # ------------------ SECTION 2: VISION AI PROFILE ------------------
    story.append(Paragraph("Spatial Vision AI Analysis", h1_style))
    
    vision = lead_data.get("vision_analysis") or {}
    
    story.append(Paragraph("🏛️ <b>Architectural Bones:</b>", h2_style))
    story.append(Paragraph(vision.get("architectural_bones", "No structure details analyzed."), body_style))
    
    story.append(Paragraph("☀️ <b>Lighting Profile & Exposure:</b>", h2_style))
    story.append(Paragraph(vision.get("lighting_profile", "No lighting details analyzed."), body_style))
    
    story.append(Paragraph("🎨 <b>Existing Room Aesthetic:</b>", h2_style))
    story.append(Paragraph(vision.get("current_style", "No styling details analyzed."), body_style))
    
    story.append(Paragraph("📏 <b>Dimensions & Volume:</b>", h2_style))
    story.append(Paragraph(vision.get("estimated_dimensions", "No dimensions analyzed."), body_style))
    
    story.append(Paragraph("⚠️ <b>Spatial Pain Points & Constraints:</b>", h2_style))
    story.append(Paragraph(vision.get("potential_pain_points", "No challenges identified."), body_style))
    
    story.append(Spacer(1, 15))
    
    # ------------------ SECTION 3: DESIGN ASSESSMENT & ALIGNMENT ------------------
    story.append(Paragraph("Financial & Administrative Briefing", h1_style))
    
    min_b = lead_data.get("budget_min", 0)
    max_b = lead_data.get("budget_max", 0)
    area = lead_data.get("area_sqft", 0)
    scope = {1: "Furnishing & Styling Only", 2: "Soft Renovation (Cosmetic)", 3: "Full Gut Remodel & Build"}.get(lead_data.get("scope_level", 2), "Remodel")
    material = {1: "Premium (High Street / Retail)", 2: "Luxury (Custom Millwork & Finishes)", 3: "Ultra-Luxury (Bespoke & Import Masterpieces)"}.get(lead_data.get("material_tier", 2), "Luxury")
    
    fin_data = [
        [Paragraph("<b>Estimated Square Footage</b>", meta_label_style), Paragraph(f"{area} sq ft", meta_val_style)],
        [Paragraph("<b>Scope of Renovation</b>", meta_label_style), Paragraph(scope, meta_val_style)],
        [Paragraph("<b>Material Tier</b>", meta_label_style), Paragraph(material, meta_val_style)],
        [Paragraph("<b>ML Predicted Cost Range</b>", meta_label_style), Paragraph(f"<b>${min_b:,.2f} - ${max_b:,.2f}</b>", meta_val_style)],
        [Paragraph("<b>Timeline Expectations</b>", meta_label_style), Paragraph(lead_data.get("timeline") or "Unspecified", meta_val_style)],
        [Paragraph("<b>Decision-Maker Involvement</b>", meta_label_style), Paragraph(lead_data.get("decision_maker") or "Unspecified", meta_val_style)]
    ]
    
    fin_table = Table(fin_data, colWidths=[180, 320])
    fin_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LINEBELOW', (0,0), (-1,-1), 0.5, COLOR_BORDER),
    ]))
    story.append(fin_table)
    
    story.append(Spacer(1, 20))
    
    # Designer Consultation Agenda
    story.append(Paragraph("Recommended Lead Handoff Agenda", h2_style))
    story.append(Paragraph("• <b>Discuss Room Bones:</b> Open the meeting by acknowledging the architectural highlights (e.g. fireplace, crown molding) to establish instant creative alignment.", bullet_style))
    story.append(Paragraph("• <b>Validate Budget Predictability:</b> Mention that the initial ML model estimated a project cost between $" + f"{min_b:,.0f} and ${max_b:,.0f}" + " for a " + scope.lower() + " and confirm if they wish to adjust scale.", bullet_style))
    story.append(Paragraph("• <b>Address Design Friction:</b> Address any style mismatch (e.g. lighting limits vs. selected design styles) by pitching alternative luxury textures (such as warm limewash plaster over bare drywall).", bullet_style))
    story.append(Paragraph("• <b>Confirm Readiness Details:</b> Finalize decisions with " + (lead_data.get("decision_maker") or "both partners") + " to lock down the engagement details.", bullet_style))
    
    # Build document
    doc.build(story, canvasmaker=NumberedCanvas)
    return file_path
