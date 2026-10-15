import streamlit as st
import json
import io
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# ---------------------------------------------------------
# Page Configuration & Styling
# ---------------------------------------------------------
st.set_page_config(page_title="Beobachtungs-App", page_icon="📋", layout="wide")

# Custom CSS for tablet-friendly buttons
st.markdown("""
<style>
    .big-counter {
        font-size: 24px !important;
        font-weight: bold;
        text-align: center;
    }
    .signature-footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: rgba(240, 242, 246, 0.9);
        color: #555555;
        text-align: center;
        padding: 8px 0;
        font-size: 13px;
        font-weight: 500;
        border-top: 1px solid #e0e0e0;
        z-index: 999;
    }
</style>
""", unsafe_allow_html=True)

SIGNATURE_TEXT = "Juan Carlos Nogueira Pérez - Training und Coaching"

# ---------------------------------------------------------
# Session State Initialization
# ---------------------------------------------------------
if 'fields' not in st.session_state:
    st.session_state.fields = [
        {"id": 1, "label": "Teilnehmer-Beteiligung", "type": "Zähler", "value": 0, "options": ""},
        {"id": 2, "label": "Aufmerksamkeit", "type": "Auswahl", "value": "Hoch", "options": "Hoch, Mittel, Niedrig"},
        {"id": 3, "label": "Allgemeine Anmerkungen", "type": "Freitext", "value": "", "options": ""}
    ]

# ---------------------------------------------------------
# PDF Generation Function
# ---------------------------------------------------------
def generate_pdf(title, fields, signature):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=40, leftMargin=40,
        topMargin=40, bottomMargin=50
    )
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#1E3A8A'),
        spaceAfter=10
    )
    subtitle_style = ParagraphStyle(
        'DocSub',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.gray,
        spaceAfter=20
    )
    cell_label_style = ParagraphStyle(
        'CellLabel',
        parent=styles['Normal'],
        fontSize=11,
        fontName='Helvetica-Bold',
        textColor=colors.HexColor('#1F2937')
    )
    cell_value_style = ParagraphStyle(
        'CellValue',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.HexColor('#111827')
    )

    story = []
    
    # Header
    story.append(Paragraph(title, title_style))
    datum_str = datetime.now().strftime("%d.%m.%Y um %H:%M Uhr")
    story.append(Paragraph(f"Erstellt am: {datum_str}", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#CBD5E1'), spaceAfter=20))
    
    # Table Content
    data = [[Paragraph("Beobachtungs-Kategorie", cell_label_style), Paragraph("Ergebnis / Erfassung", cell_label_style)]]
    
    for f in fields:
        val_str = str(f['value']) if f['value'] != "" else "-"
        data.append([
            Paragraph(f['label'], cell_label_style),
            Paragraph(val_str, cell_value_style)
        ])

    table = Table(data, colWidths=[200, 310])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#F1F5F9')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor('#0F172A')),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
    ]))
    
    story.append(table)
    story.append(Spacer(1, 40))
    
    # Footer Signature
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#CBD5E1'), spaceAfter=10))
    sig_style = ParagraphStyle(
        'Sig',
        parent=styles['Normal'],
        fontSize=10,
        alignment=1, # Center
        textColor=colors.HexColor('#475569')
    )
    story.append(Paragraph(signature, sig_style))
    
    doc.build(story)
    buffer.seek(0)
    return buffer

# ---------------------------------------------------------
# Application Header
# ---------------------------------------------------------
st.title("📋 Beobachtungs- & Zähl-App")

# Sidebar for Template Management & Field Settings
with st.sidebar:
    st.header("⚙️ Konfiguration & Vorlagen")
    
    # Template Export
    st.subheader("Vorlage speichern")
    config_json = json.dumps(st.session_state.fields, indent=2, ensure_ascii=False)
    st.download_button(
        label="💾 Aktuelle Konfiguration als Datei speichern",
        data=config_json,
        file_name="beobachtung_vorlage.json",
        mime="application/json"
    )
    
    # Template Import
    st.subheader("Vorlage laden")
    uploaded_file = st.file_uploader("JSON-Vorlage hochladen", type=["json"])
    if uploaded_file is not None:
        try:
            loaded_fields = json.load(uploaded_file)
            st.session_state.fields = loaded_fields
            st.success("Vorlage erfolgreich geladen!")
        except Exception as e:
            st.error("Fehler beim Laden der Datei.")

    st.divider()
    
    # Dynamic Field Setup
    st.subheader("Felder bearbeiten")
    with st.expander("Zeilen hinzufügen / anpassen"):
        for i, field in enumerate(st.session_state.fields):
            st.markdown(f"**Feld {i+1}**")
            field['label'] = st.text_input(f"Bezeichnung #{i+1}", field['label'], key=f"lbl_{i}")
            field['type'] = st.selectbox(f"Typ #{i+1}", ["Zähler", "Auswahl", "Freitext"], index=["Zähler", "Auswahl", "Freitext"].index(field['type']), key=f"typ_{i}")
            if field['type'] == "Auswahl":
                field['options'] = st.text_input(f"Optionen (kommagetrennt) #{i+1}", field['options'], key=f"opt_{i}")
            st.divider()
            
        if st.button("➕ Neues Feld hinzufügen"):
            st.session_state.fields.append({
                "id": len(st.session_state.fields) + 1,
                "label": "Neues Feld",
                "type": "Zähler",
                "value": 0,
                "options": ""
            })
            st.rerun()

# ---------------------------------------------------------
# Main Observation Interface
# ---------------------------------------------------------
doc_title = st.text_input("Titel / Anlass der Beobachtung", "Beobachtungsprotokoll")

st.subheader("Erfassung")

for i, field in enumerate(st.session_state.fields):
    col1, col2 = st.columns([2, 3])
    
    with col1:
        st.markdown(f"### {field['label']}")
        
    with col2:
        if field['type'] == "Zähler":
            btn_col1, btn_col2, btn_col3 = st.columns([1, 2, 1])
            with btn_col1:
                if st.button("➖", key=f"dec_{i}", use_container_width=True):
                    field['value'] = max(0, int(field.get('value', 0)) - 1)
                    st.rerun()
            with btn_col2:
                st.markdown(f"<div class='big-counter'>{field.get('value', 0)}</div>", unsafe_allow_html=True)
            with btn_col3:
                if st.button("➕", key=f"inc_{i}", use_container_width=True):
                    field['value'] = int(field.get('value', 0)) + 1
                    st.rerun()
                    
        elif field['type'] == "Auswahl":
            opts = [o.strip() for o in field['options'].split(",") if o.strip()]
            if not opts:
                opts = ["Option 1", "Option 2"]
            field['value'] = st.selectbox(
                "Auswählen:",
                opts,
                index=opts.index(field['value']) if field['value'] in opts else 0,
                key=f"sel_{i}",
                label_visibility="collapsed"
            )
            
        elif field['type'] == "Freitext":
            field['value'] = st.text_area(
                "Notiz:",
                value=field.get('value', ''),
                key=f"txt_{i}",
                label_visibility="collapsed"
            )

st.divider()

# ---------------------------------------------------------
# PDF Export
# ---------------------------------------------------------
col_pdf, col_reset = st.columns([2, 1])

with col_pdf:
    pdf_buffer = generate_pdf(doc_title, st.session_state.fields, SIGNATURE_TEXT)
    st.download_button(
        label="📄 PDF-Protokoll erstellen & herunterladen",
        data=pdf_buffer,
        file_name=f"Beobachtung_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
        mime="application/pdf",
        use_container_width=True,
        type="primary"
    )

with col_reset:
    if st.button("🔄 Zähler & Eingaben zurücksetzen", use_container_width=True):
        for f in st.session_state.fields:
            if f['type'] == "Zähler":
                f['value'] = 0
            elif f['type'] == "Freitext":
                f['value'] = ""
        st.rerun()

# ---------------------------------------------------------
# Subtle Footer Signature
# ---------------------------------------------------------
st.markdown(f"<div class='signature-footer'>{SIGNATURE_TEXT}</div>", unsafe_allow_html=True)
