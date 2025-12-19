import streamlit as st
from PIL import Image, ImageDraw
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
import tempfile
import os

# =============================
# Seitenkonfiguration
# =============================
st.set_page_config(
    page_title="CarMoveServices – Schadenprotokoll",
    layout="wide"
)

st.title("🚗 CarMoveServices – Schadenprotokoll")

# =============================
# Schadenpunkte (BEIBEHALTEN)
# =============================
SCHADENPUNKTE = {
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

# =============================
# Kundendaten
# =============================
st.subheader("👤 Kundendaten")

kunde = st.text_input("Kundenname")
auftrag = st.text_input("Auftrag / Kennzeichen")

# =============================
# Schäden
# =============================
st.subheader("🛠️ Schäden")

ausgewaehlte_schaeden = []

for bereich, punkte in SCHADENPUNKTE.items():
    with st.expander(bereich, expanded=False):
        for punkt in punkte:
            if st.checkbox(punkt, key=punkt):
                ausgewaehlte_schaeden.append(punkt)

# =============================
# Bilder
# =============================
st.subheader("📸 Schadenbilder")

bilder = st.file_uploader(
    "Bilder hochladen",
    type=["jpg", "jpeg", "png"],
    accept_multiple_files=True
)

# =============================
# Unterschrift
# =============================
st.subheader("✍️ Unterschrift Kunde")

signature = st.canvas(
    fill_color="rgba(255,255,255,1)",
    stroke_width=2,
    stroke_color="black",
    background_color="white",
    height=200,
    drawing_mode="freedraw",
    key="signature"
)

# =============================
# PDF erstellen
# =============================
def erstelle_pdf():
    temp_dir = tempfile.mkdtemp()
    pdf_path = os.path.join(temp_dir, "Schadenprotokoll.pdf")

    c = canvas.Canvas(pdf_path, pagesize=A4)
    w, h = A4
    y = h - 2 * cm

    c.setFont("Helvetica-Bold", 16)
    c.drawString(2 * cm, y, "Schadenprotokoll – CarMoveServices")
    y -= 1.5 * cm

    c.setFont("Helvetica", 11)
    c.drawString(2 * cm, y, f"Kunde: {kunde}")
    y -= 0.7 * cm
    c.drawString(2 * cm, y, f"Auftrag: {auftrag}")
    y -= 1 * cm

    c.setFont("Helvetica-Bold", 12)
    c.drawString(2 * cm, y, "Festgestellte Schäden:")
    y -= 0.7 * cm

    c.setFont("Helvetica", 10)
    for s in ausgewaehlte_schaeden:
        if y < 2 * cm:
            c.showPage()
            y = h - 2 * cm
        c.drawString(2.2 * cm, y, f"- {s}")
        y -= 0.45 * cm

    # Bilder
    if bilder:
        c.showPage()
        y = h - 2 * cm
        c.setFont("Helvetica-Bold", 12)
        c.drawString(2 * cm, y, "Schadenbilder")
        y -= 1 * cm

        for bild in bilder:
            img_path = os.path.join(temp_dir, bild.name)
            with open(img_path, "wb") as f:
                f.write(bild.getbuffer())

            if y < 8 * cm:
                c.showPage()
                y = h - 2 * cm

            c.drawImage(img_path, 2 * cm, y - 6 * cm, width=w - 4 * cm, height=6 * cm, preserveAspectRatio=True)
            y -= 7 * cm

    c.save()
    return pdf_path

# =============================
# Button
# =============================
if st.button("📄 Schadenprotokoll als PDF erstellen"):
    if not kunde:
        st.error("Bitte Kundenname eingeben")
    else:
        pdf = erstelle_pdf()
        with open(pdf, "rb") as f:
            st.download_button(
                label="📥 PDF herunterladen",
                data=f,
                file_name=f"Schadenprotokoll_{kunde}.pdf",
                mime="application/pdf"
            )
