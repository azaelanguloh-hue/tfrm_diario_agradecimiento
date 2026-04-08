# -*- coding: utf-8 -*-
import os
from datetime import date, datetime

import streamlit as st

# PDF
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
from reportlab.lib import colors


# -----------------------------
# Config / Branding (TFRM)
# -----------------------------
APP_TITLE = "Diario de Agradecimiento (TFRM)"

# Colores TFRM (aprox)
TFRM_DARK = colors.HexColor("#1F2430")   # gris oscuro
TFRM_LILAC = colors.HexColor("#C9B3E6")  # lila suave
TFRM_LIGHT = colors.HexColor("#F7F4EF")  # crema

LOGO_PATH = os.path.join("assets", "tfrm_logo.png")  # debe existir


st.set_page_config(page_title=APP_TITLE, page_icon="📝", layout="wide")

# Header con logo
col1, col2 = st.columns([1, 6])
with col1:
    if os.path.exists(LOGO_PATH):
        st.image(LOGO_PATH, width=110)
with col2:
    st.markdown(f"# 📝 {APP_TITLE}")
    st.caption("Sencillo. Sin login. Tu historial vive en esta sesión del navegador. Puedes exportarlo a PDF cuando quieras.")

st.divider()


# -----------------------------
# Helpers
# -----------------------------
SENTIMIENTOS = [
    "",  # opción vacía
    "feliz",
    "tranquila",
    "agradecida",
    "motivada",
    "esperanzada",
    "cansada",
    "abrumada",
    "triste",
    "enojada",
    "con miedo",
    "con culpa",
    "con vergüenza",
    "sin energía",
    "emocionada",
    "angustiada",
    "frustrada",
    "harta",
    "enamorada",
]
def fmt_fecha_lat(d: date) -> str:
    # dd/mm/aaaa
    return d.strftime("%d/%m/%Y")

def build_pdf(entries: list) -> bytes:
    """
    Genera un PDF bonito con branding TFRM + logo.
    """
    import io
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    w, h = letter

    margin = 0.75 * inch
    y = h - margin

    # Fondo claro
    c.setFillColor(TFRM_LIGHT)
    c.rect(0, 0, w, h, fill=1, stroke=0)

    # Header dark bar
    c.setFillColor(TFRM_DARK)
    c.rect(0, h - 1.25*inch, w, 1.25*inch, fill=1, stroke=0)

    # Logo
    if os.path.exists(LOGO_PATH):
        try:
            img = ImageReader(LOGO_PATH)
            c.drawImage(img, margin, h - 1.05*inch, width=1.6*inch, height=0.7*inch, mask='auto')
        except Exception:
            pass

    # Título
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(margin + 1.8*inch, h - 0.75*inch, "Diario de Agradecimiento (TFRM)")

    # Sub
    c.setFont("Helvetica", 10)
    c.setFillColor(colors.white)
    c.drawString(margin + 1.8*inch, h - 1.02*inch, f"Exportado: {datetime.now().strftime('%d/%m/%Y %H:%M')}")

    y = h - 1.6*inch

    # Entries
    if not entries:
        c.setFillColor(TFRM_DARK)
        c.setFont("Helvetica", 12)
        c.drawString(margin, y, "No hay entradas todavía.")
        c.showPage()
        c.save()
        buffer.seek(0)
        return buffer.read()

    # Bloques
    c.setFillColor(TFRM_DARK)
    for i, e in enumerate(entries, start=1):
        # tarjeta
        if y < 2.2*inch:
            c.showPage()
            c.setFillColor(TFRM_LIGHT)
            c.rect(0, 0, w, h, fill=1, stroke=0)
            y = h - margin

        # caja
        box_h = 1.9*inch
        c.setFillColor(colors.white)
        c.roundRect(margin, y - box_h, w - 2*margin, box_h, 14, fill=1, stroke=0)

        # borde lila
        c.setStrokeColor(TFRM_LILAC)
        c.setLineWidth(2)
        c.roundRect(margin, y - box_h, w - 2*margin, box_h, 14, fill=0, stroke=1)

        # texto
        c.setFillColor(TFRM_DARK)
        c.setFont("Helvetica-Bold", 12)
        c.drawString(margin + 14, y - 22, f"{i}. {e.get('fecha_lat','')}  |  {e.get('sentimiento','') or '—'}")

        c.setFont("Helvetica", 10)
        lines = []
        lines.append(f"Hoy agradezco: {e.get('a1','')}")
        lines.append(f"También agradezco: {e.get('a2','')}")
        lines.append(f"Y agradezco: {e.get('a3','')}")
        nota = e.get('nota','').strip()
        if nota:
            lines.append(f"Nota: {nota}")

        ty = y - 44
        for ln in lines:
            if len(ln) > 120:
                # corte simple
                ln = ln[:117] + "..."
            c.drawString(margin + 14, ty, ln)
            ty -= 14

        y -= (box_h + 18)

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer.read()


# -----------------------------
# State
# -----------------------------
if "entries" not in st.session_state:
    st.session_state.entries = []


# -----------------------------
# UI
# -----------------------------
st.markdown("## Entrada de hoy")

c1, c2 = st.columns([1, 1])

with c1:
    fecha = st.date_input("Fecha", value=date.today())
    fecha_lat = fmt_fecha_lat(fecha)

with c2:
    sentimiento = st.selectbox("¿Cómo te sientes hoy? (opcional)", options=SENTIMIENTOS, index=0)

a1 = st.text_input("Hoy agradezco...", "")
a2 = st.text_input("También agradezco...", "")
a3 = st.text_input("Y agradezco...", "")
nota = st.text_area("Nota (opcional): ¿qué aprendiste hoy o qué quieres recordar?", "", height=100)

btn1, btn2, btn3 = st.columns([1, 1, 3])

with btn1:
    guardar = st.button("Guardar entrada", use_container_width=True)

with btn2:
    limpiar = st.button("Limpiar campos", use_container_width=True)

if limpiar:
    st.experimental_rerun()

if guardar:
    entry = {
        "fecha": fecha.isoformat(),
        "fecha_lat": fecha_lat,
        "sentimiento": sentimiento,
        "a1": a1.strip(),
        "a2": a2.strip(),
        "a3": a3.strip(),
        "nota": nota.strip(),
    }
    st.session_state.entries.insert(0, entry)
    st.success("Entrada guardada ✅")

st.divider()

st.markdown("## Historial (esta sesión)")
if st.session_state.entries:
    for e in st.session_state.entries[:10]:
        st.markdown(f"**{e['fecha_lat']}**  •  _{e.get('sentimiento') or '—'}_")
        st.write(f"- Hoy agradezco: {e.get('a1','')}")
        st.write(f"- También agradezco: {e.get('a2','')}")
        st.write(f"- Y agradezco: {e.get('a3','')}")
        if e.get("nota"):
            st.write(f"- Nota: {e.get('nota')}")
        st.divider()
else:
    st.info("Aún no hay entradas. Escribe una arriba y presiona **Guardar entrada**.")

st.markdown("### Exportar a PDF")
pdf_bytes = build_pdf(st.session_state.entries)

st.download_button(
    label="Descargar PDF (TFRM)",
    data=pdf_bytes,
    file_name=f"diario_agradecimiento_TFRM_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
    mime="application/pdf",
    use_container_width=True,
)

st.caption("Tip: guarda este link en tu PDF. No requiere login.")
