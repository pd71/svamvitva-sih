import os
import io
import csv
import datetime
from typing import Dict, Any, List
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def generate_analysis_pdf_report(
    analysis_dict: Dict[str, Any],
    buildings: List[Dict[str, Any]],
    roads: List[Dict[str, Any]],
    waterbodies: List[Dict[str, Any]],
    output_pdf_path: str
) -> str:
    """
    Generates a executive-grade PDF summary report using ReportLab.
    """
    doc = SimpleDocTemplate(
        output_pdf_path,
        pagesize=A4,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()

    # Custom styles
    header_style = ParagraphStyle(
        'HeaderStyle',
        parent=styles['Heading1'],
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#0F172A'),
        fontName='Helvetica-Bold'
    )

    sub_header = ParagraphStyle(
        'SubHeader',
        parent=styles['Normal'],
        fontSize=10,
        leading=13,
        textColor=colors.HexColor('#0284C7'),
        fontName='Helvetica-Bold'
    )

    section_title = ParagraphStyle(
        'SectionTitle',
        parent=styles['Heading2'],
        fontSize=14,
        leading=18,
        textColor=colors.HexColor('#1E293B'),
        fontName='Helvetica-Bold',
        spaceBefore=12,
        spaceAfter=6
    )

    body_style = ParagraphStyle(
        'BodyTextCustom',
        parent=styles['BodyText'],
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#334155')
    )

    story = []

    # Title Banner
    story.append(Paragraph("SVAMITVA AI FEATURE EXTRACTION REPORT", sub_header))
    story.append(Spacer(1, 4))
    story.append(Paragraph(f"Village Analysis: {analysis_dict.get('village_name', 'Sample Village')}", header_style))
    story.append(Paragraph(f"Generated on {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')} | Problem Statement: DJS_26_SW_08", body_style))
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#0284C7'), spaceBefore=0, spaceAfter=15))

    # Summary KPI Table
    kpi_data = [
        [
            Paragraph("<b>Total Buildings</b>", body_style),
            Paragraph(f"<b>{analysis_dict.get('total_buildings', 0)}</b>", body_style),
            Paragraph("<b>Total Road Length</b>", body_style),
            Paragraph(f"<b>{analysis_dict.get('total_roads_len', 0.0):.1f} m</b>", body_style),
        ],
        [
            Paragraph("<b>Waterbody Area</b>", body_style),
            Paragraph(f"<b>{analysis_dict.get('total_water_area', 0.0):.1f} m²</b>", body_style),
            Paragraph("<b>Avg Confidence</b>", body_style),
            Paragraph(f"<b>{analysis_dict.get('avg_confidence', 0.0)*100:.1f}%</b>", body_style),
        ]
    ]

    t_kpi = Table(kpi_data, colWidths=[120, 120, 120, 120])
    t_kpi.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#E2E8F0')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('PADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t_kpi)
    story.append(Spacer(1, 15))

    # Overlay Image Thumbnail if available
    overlay_path = analysis_dict.get('overlay_path')
    if overlay_path and os.path.exists(overlay_path):
        story.append(Paragraph("AI Feature Extraction & GIS Overlay Map", section_title))
        try:
            img = Image(overlay_path, width=500, height=280)
            story.append(img)
            story.append(Spacer(1, 15))
        except Exception:
            pass

    # Roof Classification Breakdown
    story.append(Paragraph("Roof Type Distribution & Statistics", section_title))
    rcc_cnt = sum(1 for b in buildings if b.get('roof_type') == 'RCC')
    tiled_cnt = sum(1 for b in buildings if b.get('roof_type') == 'Tiled')
    tin_cnt = sum(1 for b in buildings if b.get('roof_type') == 'Tin')
    other_cnt = sum(1 for b in buildings if b.get('roof_type') == 'Other')
    total_bldgs = max(1, len(buildings))

    roof_table_data = [
        ["Roof Material Category", "Detected Count", "Percentage Share", "AI Model Used"],
        ["RCC (Reinforced Concrete)", str(rcc_cnt), f"{(rcc_cnt/total_bldgs)*100:.1f}%", "EfficientNet-B4 / HSV Engine"],
        ["Tiled (Terracotta Clay)", str(tiled_cnt), f"{(tiled_cnt/total_bldgs)*100:.1f}%", "EfficientNet-B4 / HSV Engine"],
        ["Tin / Metal Sheet", str(tin_cnt), f"{(tin_cnt/total_bldgs)*100:.1f}%", "EfficientNet-B4 / HSV Engine"],
        ["Other / Traditional", str(other_cnt), f"{(other_cnt/total_bldgs)*100:.1f}%", "EfficientNet-B4 / HSV Engine"],
    ]

    t_roof = Table(roof_table_data, colWidths=[160, 100, 100, 140])
    t_roof.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0F172A')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#CBD5E1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_roof)
    story.append(Spacer(1, 15))

    # Top Detected Buildings Feature Table
    story.append(Paragraph("Building Details Inventory (Sample Top Detections)", section_title))
    bldg_rows = [["ID", "Area (m²)", "Centroid (X, Y)", "Roof Type", "Conf.", "Status"]]
    
    for b in buildings[:12]:
        cx, cy = b.get('centroid_x', 0), b.get('centroid_y', 0)
        bldg_rows.append([
            f"#{b.get('building_index', 0)}",
            f"{b.get('area_sqm', 0.0):.1f}",
            f"({cx:.0f}, {cy:.0f})",
            b.get('roof_type', 'RCC'),
            f"{b.get('confidence', 0.0)*100:.0f}%",
            b.get('status', 'detected').upper()
        ])

    t_bldgs = Table(bldg_rows, colWidths=[40, 70, 110, 100, 60, 120])
    t_bldgs.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0284C7')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#CBD5E1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('PADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_bldgs)

    doc.build(story)
    return output_pdf_path


def generate_analysis_csv_export(
    buildings: List[Dict[str, Any]],
    roads: List[Dict[str, Any]],
    waterbodies: List[Dict[str, Any]]
) -> str:
    """
    Generates a CSV string containing all extracted feature rows.
    """
    output = io.StringIO()
    writer = csv.writer(output)
    
    writer.writerow(["Feature_Type", "Feature_ID", "Area_sqm", "Length_m", "Centroid_X", "Centroid_Y", "Roof_Type", "Confidence", "Status"])
    
    for b in buildings:
        writer.writerow([
            "Building",
            f"B_{b.get('building_index', 0)}",
            b.get('area_sqm', 0.0),
            "",
            b.get('centroid_x', 0),
            b.get('centroid_y', 0),
            b.get('roof_type', 'RCC'),
            b.get('confidence', 0.0),
            b.get('status', 'detected')
        ])

    for r in roads:
        writer.writerow([
            "Road",
            f"R_{r.get('road_index', 0)}",
            "",
            r.get('length_m', 0.0),
            "",
            "",
            "",
            r.get('confidence', 0.0),
            "detected"
        ])

    for w in waterbodies:
        writer.writerow([
            "Waterbody",
            f"W_{w.get('waterbody_index', 0)}",
            w.get('area_sqm', 0.0),
            "",
            "",
            "",
            "",
            w.get('confidence', 0.0),
            "detected"
        ])

    return output.getvalue()
