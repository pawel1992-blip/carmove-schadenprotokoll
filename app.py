import streamlit as st
from streamlit_drawable_canvas import st_canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas as pdf_canvas
from reportlab.lib.units import cm
from PIL import Image
import numpy as np
import os
from datetime import datetime

st.set_page_config(page_title="CarMoveServices – Schadenprotokoll", layout="wide")

# -----------------------------
# Schadenpunkte
# -----------------------------
schadenpunkte = {
    "Außen – Front": [
        "Frontstoßstange beschädigt",
        "Frontstoßstange gerissen",
        "Frontstoßstange lackbeschädigt",
        "Motorhaube beschädigt",
        "Motorhaube verbeult",
        "Motorhaube lackbeschädigt",
        "Steinschlag Windschutzscheibe",
        "Riss Windschutzscheibe",
        "Scheinwerfer beschädigt",
        "Scheinwerfer blind",
        "Nebelscheinwerfer beschädigt",
        "Kühlergrill beschädigt"
    ],
    "Außen – Seite links": [
        "Kratzer Tür vorne links",
        "Delle Tür vorne links",
        "Lackschaden Tür vorne links",
        "Kratzer Tür hinten links",
        "Delle Tür hinten links",
        "Lackschaden Tür hinten links",
        "Kotflügel vorne links beschädigt",
        "Seitenschweller links beschädigt",
        "Außenspiegel links beschädigt",
        "Felgenschaden vorne links",
        "Felgenschaden hinten links",
        "Reifen beschädigt links"
    ],
    "Außen – Seite rechts": [
        "Kratzer Tür vorne rechts",
        "Delle Tür vorne rechts",
        "Lackschaden Tür vorne rechts",
        "Kratzer Tür hinten rechts",
        "Delle Tür hinten rechts",
        "Lackschaden Tür hinten rechts",
        "Kotflügel vorne rechts beschädigt",
        "Seitenschweller rechts beschädigt",
        "Außenspiegel rechts beschädigt",
        "Felgenschaden vorne rechts",
        "Felgenschaden hinten rechts",
        "Reifen beschädigt rechts"
    ],
    "Außen – Heck": [
        "Heckstoßstange beschädigt",
        "Heckstoßstange gerissen",
        "Heckstoßstange lackbeschädigt",
        "Kofferraumdeckel beschädigt",
        "Kofferraumdeckel verbeult",
        "Rückleuchte links beschädigt",
        "Rückleuchte rechts beschädigt",
        "Kennzeichenhalter beschädigt",
        "Auspuff beschädigt"
    ],
    "Dach & Glas": [
        "Dach beschädigt",
        "Dach verkratzt",
        "Dachantenne beschädigt",
        "Panoramadach beschädigt",
        "Seitenscheibe vorne links beschädigt",
        "Seitenscheibe vorne rechts beschädigt",
        "Seitenscheibe hinten links beschädigt",
        "Seitenscheibe hinten rechts beschädigt"
    ],
    "Innenraum": [
        "Fahrersitz beschädigt",
        "Beifahrersitz beschädigt",
        "Rücksitzbank beschädigt",
        "Armaturenbrett beschädigt",
        "Lenkrad beschädigt",
        "Schaltknauf beschädigt",
        "Innenverkleidung beschädigt",
        "Teppichboden beschädigt",
        "Dachhimmel beschädigt",
        "Geruchsbelästigung (Rauchen, Tiere)",
        "Warnleuchte im Cockpit aktiv"
    ],
    "Technik / Sonstiges": [
        "Motor startet nicht",
        "Getriebeproblem",
        "Bremsen auffällig",
        "Lenkung auffällig",
        "Reifendruckwarnung aktiv",
        "Batterie schwach",
        "Bordcomputer Fehlermeldung",
        "Serviceanzeige aktiv"
    ]
}

# -----------------------------
# UI – Kopf
# -----------------------------
st.title("🚗 CarMoveServices – Schadenprotokoll")

# -----------------------------
# Kundendaten
# -----------------------------
st.subheader("👤 Kundendaten")

col1, col2 = st.columns(2)
with col1:
    kunde = st.text_input("Kundenname *")
with col2:
    auftrag = st.text_input("Kennzeichen / Auftrag")

# -----------------------------
# Schäden
# -----------------------------
st.subheader("🛠️ Schaden-Checkliste")

ausgewaehlte_schaeden = []

for bereich, punkte in schadenpunkte.items():
    with st.expander(bereich, expanded=False):
        for punkt in punkte:
            if st.checkbox(punkt, key=punkt):
                ausgewaehlte_schaeden.append(punkt)

# -----------------------------
# Bilder Upload
# -----------------------------
st.subheader("📷 Schadenbilder")
bilder = st.file_uploader(
    "Bilder auswählen",
    type=["jpg", "jpeg", "png"],
    accept_multiple_files=True
)

# -----------------------------
# Unterschrift
# -----------------------------
st.subheader("✍️ Unterschrift Kunde")

canvas_result = st_canvas(
    fill_color="rgba(255,255,255,0)",
    stroke_width=3,
    stroke_color="#000000",
    background_color="#FFFFFF",
    width=500,
    height=200,
    drawing_mode="freedraw",
    key="signature"
)

signature_image = None
if canvas_result.image_data is not None:
    img_array = canvas_result.image_data.astype(np.uint8)
    signature_image = Image.fromarray(img_array)

# -----------------------------
# PDF erstellen
# -----------------------------
def pdf_erstellen():
    if not kunde:
        st.error("❌ Kundenname fehlt")
        return

    if not signature_image:
        st.error("❌ Unterschrift fehlt")
        return

    pdf_name = f"Schadenprotokoll_{kunde.replace(' ', '_')}.pdf"
    c = pdf_canvas.Canvas(pdf_name, pagesize=A4)
    width, height = A4
    y = height - 2 * cm

    # Titel
    c.setFont("Helvetica-Bold", 16)
    c.drawString(2 * cm, y, "Schadenprotokoll – CarMoveServices")
    y -= 1.5 * cm

    # Kundendaten
    c.setFont("Helvetica", 11)
    c.drawString(2 * cm, y, f"Kunde: {kunde}")
    y -= 0.7 * cm
    c.drawString(2 * cm, y, f"Auftrag / Kennzeichen: {auftrag}")
    y -= 0.7 * cm
    c.drawString(2 * cm, y, f"Datum: {datetime.now().strftime('%d.%m.%Y %H:%M')}")
    y -= 1 * cm

    # Schäden
    c.setFont("Helvetica-Bold", 12)
    c.drawString(2 * cm, y, "Festgestellte Schäden:")
    y -= 0.7 * cm

    c.setFont("Helvetica", 10)
    for schaden in ausgewaehlte_schaeden:
        if y < 2 * cm:
            c.showPage()
            y = height - 2 * cm
        c.drawString(2.2 * cm, y, f"- {schaden}")
        y -= 0.5 * cm

    # Bilder
    if bilder:
        c.showPage()
        y = height - 2 * cm
        c.setFont("Helvetica-Bold", 12)
        c.drawString(2 * cm, y, "Schadenbilder")
        y -= 1 * cm

        for bild in bilder:
            img = Image.open(bild)
            img_path = f"_tmp_{bild.name}"
            img.save(img_path)

            if y < 8 * cm:
                c.showPage()
                y = height - 2 * cm

            c.drawImage(
                img_path,
                2 * cm,
                y - 6 * cm,
                width=width - 4 * cm,
                height=6 * cm,
                preserveAspectRatio=True
            )
            y -= 7 * cm
            os.remove(img_path)

    # Unterschrift
    c.showPage()
    y = height - 3 * cm
    c.setFont("Helvetica-Bold", 12)
    c.drawString(2 * cm, y, "Unterschrift Kunde")

    sig_path = "_signature.png"
    signature_image.save(sig_path)

    c.drawImage(sig_path, 2 * cm, y - 4 * cm, width=6 * cm, height=3 * cm)
    os.remove(sig_path)

    c.save()

    with open(pdf_name, "rb") as f:
        st.download_button("📄 PDF herunterladen", f, file_name=pdf_name)

# -----------------------------
# Button
# -----------------------------
st.divider()
if st.button("📄 Schadenprotokoll als PDF erstellen"):
    pdf_erstellen()
