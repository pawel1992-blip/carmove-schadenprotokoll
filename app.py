import streamlit as st
from streamlit_drawable_canvas import st_canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from PIL import Image
import numpy as np
import datetime
import os

st.set_page_config(page_title="CarMoveServices Schadenprotokoll", layout="wide")

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
    "Innenraum": [
        "Fahrersitz beschädigt",
        "Beifahrersitz beschädigt",
        "Rücksitzbank beschädigt",
        "Armaturenbrett beschädigt",
        "Lenkrad beschädigt",
        "Innenverkleidung beschädigt",
        "Geruchsbelästigung"
    ]
}

# -----------------------------
# Kopfbereich
# -----------------------------
st.title("🚗 CarMoveServices – Schadenprotokoll")

col1, col2, col3 = st.columns(3)
kunde = col1.text_input("Kundenname")
fahrer = col2.text_input("Fahrername")
auftrag = col3.text_input("Auftrag / Kennzeichen")

datum = st.date_input("Datum", value=datetime.date.today())

# -----------------------------
# Schäden
# -----------------------------
st.header("📋 Schadendokumentation")

schaden_auswahl = []

for bereich, punkte in schadenpunkte.items():
    with st.expander(bereich):
        for punkt in punkte:
            if st.checkbox(punkt):
                schaden_auswahl.append(punkt)

# -----------------------------
# Bilder / Kamera (iPhone!)
# -----------------------------
st.header("📸 Schadenbilder")
bilder = st.file_uploader(
    "Fotos aufnehmen oder hochladen (iPhone Kamera möglich)",
    type=["jpg", "jpeg", "png"],
    accept_multiple_files=True
)

# -----------------------------
# Unterschriften
# -----------------------------
def sign_canvas(title, key):
    st.subheader(title)
    return st_canvas(
        stroke_width=3,
        stroke_color="#000000",
        background_color="#FFFFFF",
        height=150,
        width=500,
        drawing_mode="freedraw",
        key=key
    )

sign_kunde = sign_canvas("✍️ Unterschrift Kunde", "sign_kunde")
sign_fahrer = sign_canvas("✍️ Unterschrift Fahrer", "sign_fahrer")

# -----------------------------
# Helfer: Canvas speichern
# -----------------------------
def save_canvas(canvas_data, path):
    if canvas_data is None:
        return
    img = Image.fromarray(canvas_data.astype("uint8"))
    img.save(path)

# -----------------------------
# PDF ERSTELLEN
# -----------------------------
if st.button("📄 Schadenprotokoll als PDF erstellen"):
    if not kunde or not fahrer:
        st.error("Bitte Kunden- und Fahrernamen eingeben.")
        st.stop()

    os.makedirs("output", exist_ok=True)

    kunde_sign = "output/sign_kunde.png"
    fahrer_sign = "output/sign_fahrer.png"

    save_canvas(sign_kunde.image_data, kunde_sign)
    save_canvas(sign_fahrer.image_data, fahrer_sign)

    pdf_path = f"output/Schadenprotokoll_{kunde.replace(' ','_')}.pdf"
    c = canvas.Canvas(pdf_path, pagesize=A4)
    w, h = A4
    y = h - 2 * cm

    # Titel
    c.setFont("Helvetica-Bold", 18)
    c.drawString(2 * cm, y, "Schadenprotokoll – CarMoveServices")
    y -= 1.5 * cm

    # Daten
    c.setFont("Helvetica", 11)
    c.drawString(2 * cm, y, f"Kunde: {kunde}")
    y -= 0.6 * cm
    c.drawString(2 * cm, y, f"Fahrer: {fahrer}")
    y -= 0.6 * cm
    c.drawString(2 * cm, y, f"Auftrag: {auftrag}")
    y -= 0.6 * cm
    c.drawString(2 * cm, y, f"Datum: {datum.strftime('%d.%m.%Y')}")
    y -= 1 * cm

    # Schäden
    c.setFont("Helvetica-Bold", 12)
    c.drawString(2 * cm, y, "Festgestellte Schäden:")
    y -= 0.7 * cm
    c.setFont("Helvetica", 10)

    for s in schaden_auswahl:
        if y < 2 * cm:
            c.showPage()
            y = h - 2 * cm
        c.drawString(2.2 * cm, y, f"- {s}")
        y -= 0.45 * cm

    # Bilder
    for img in bilder or []:
        c.showPage()
        c.drawImage(Image.open(img), 2 * cm, h - 10 * cm, width=16 * cm, height=8 * cm, preserveAspectRatio=True)

    # Unterschriften
    c.showPage()
    c.drawString(2 * cm, h - 3 * cm, "Unterschrift Kunde")
    c.drawImage(kunde_sign, 2 * cm, h - 7 * cm, width=6 * cm, height=3 * cm)

    c.drawString(10 * cm, h - 3 * cm, "Unterschrift Fahrer")
    c.drawImage(fahrer_sign, 10 * cm, h - 7 * cm, width=6 * cm, height=3 * cm)

    c.save()

    st.success("✅ PDF erfolgreich erstellt!")
    with open(pdf_path, "rb") as f:
        st.download_button("⬇️ PDF herunterladen", f, file_name=os.path.basename(pdf_path))
