import streamlit as st
from streamlit_drawable_canvas import st_canvas
from PIL import Image
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas as pdf_canvas
from reportlab.lib.units import cm
import os
import tempfile
from datetime import date

# =============================
# LOGIN
# =============================
USERS = {
    "admin": "2804CarM",
    "fahrer": "carmove"
}

def login():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        st.set_page_config(page_title="CarMoveServices Login", layout="centered")
        st.title("🔐 Login – CarMoveServices")

        username = st.text_input("Benutzername")
        password = st.text_input("Passwort", type="password")

        if st.button("Login"):
            if username in USERS and USERS[username] == password:
                st.session_state.logged_in = True
                st.session_state.user = username
                st.success("Login erfolgreich")
                st.rerun()
            else:
                st.error("Falscher Benutzername oder Passwort")

        st.stop()

login()

# =============================
# APP
# =============================
st.set_page_config(page_title="CarMoveServices Schadenprotokoll", layout="wide")

with st.sidebar:
    st.write(f"👤 Eingeloggt als: **{st.session_state.user}**")
    if st.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.rerun()

# -----------------------------
# Schadenpunkte
# -----------------------------
schadenpunkte = {
    "Außen – Front": [
        "Frontstoßstange beschädigt", "Frontstoßstange gerissen", "Frontstoßstange lackbeschädigt",
        "Motorhaube beschädigt", "Motorhaube verbeult", "Motorhaube lackbeschädigt",
        "Steinschlag Windschutzscheibe", "Riss Windschutzscheibe",
        "Scheinwerfer beschädigt", "Scheinwerfer blind",
        "Nebelscheinwerfer beschädigt", "Kühlergrill beschädigt"
    ],
    "Außen – Seite links": [
        "Kratzer Tür vorne links", "Delle Tür vorne links", "Lackschaden Tür vorne links",
        "Kratzer Tür hinten links", "Delle Tür hinten links", "Lackschaden Tür hinten links",
        "Kotflügel vorne links beschädigt", "Seitenschweller links beschädigt",
        "Außenspiegel links beschädigt", "Felgenschaden vorne links",
        "Felgenschaden hinten links", "Reifen beschädigt links"
    ],
    "Außen – Seite rechts": [
        "Kratzer Tür vorne rechts", "Delle Tür vorne rechts", "Lackschaden Tür vorne rechts",
        "Kratzer Tür hinten rechts", "Delle Tür hinten rechts", "Lackschaden Tür hinten rechts",
        "Kotflügel vorne rechts beschädigt", "Seitenschweller rechts beschädigt",
        "Außenspiegel rechts beschädigt", "Felgenschaden vorne rechts",
        "Felgenschaden hinten rechts", "Reifen beschädigt rechts"
    ],
    "Außen – Heck": [
        "Heckstoßstange beschädigt", "Heckstoßstange gerissen", "Heckstoßstange lackbeschädigt",
        "Kofferraumdeckel beschädigt", "Kofferraumdeckel verbeult",
        "Rückleuchte links beschädigt", "Rückleuchte rechts beschädigt",
        "Kennzeichenhalter beschädigt", "Auspuff beschädigt"
    ],
    "Dach & Glas": [
        "Dach beschädigt", "Dach verkratzt", "Dachantenne beschädigt",
        "Panoramadach beschädigt", "Seitenscheibe vorne links beschädigt",
        "Seitenscheibe vorne rechts beschädigt", "Seitenscheibe hinten links beschädigt",
        "Seitenscheibe hinten rechts beschädigt"
    ],
    "Innenraum": [
        "Fahrersitz beschädigt", "Beifahrersitz beschädigt", "Rücksitzbank beschädigt",
        "Armaturenbrett beschädigt", "Lenkrad beschädigt", "Schaltknauf beschädigt",
        "Innenverkleidung beschädigt", "Teppichboden beschädigt",
        "Dachhimmel beschädigt", "Geruchsbelästigung", "Warnleuchte aktiv"
    ],
    "Technik / Sonstiges": [
        "Motor startet nicht", "Getriebeproblem", "Bremsen auffällig",
        "Lenkung auffällig", "Reifendruckwarnung aktiv",
        "Batterie schwach", "Fehlermeldung Bordcomputer"
    ]
}

# -----------------------------
# Kopf
# -----------------------------
st.title("🚗 CarMoveServices – Schadenprotokoll")

# -----------------------------
# Kundendaten
# -----------------------------
st.subheader("👤 Kundendaten")

col1, col2 = st.columns(2)
with col1:
    kunde = st.text_input("Kundenname")
    fahrer = st.text_input("Fahrername")

with col2:
    auftrag = st.text_input("Kennzeichen / Auftrag")
    protokoll_datum = st.date_input("Datum", value=date.today())

# -----------------------------
# Schäden
# -----------------------------
st.subheader("🛠️ Schäden")
checkbox_vars = {}

for bereich, punkte in schadenpunkte.items():
    with st.expander(bereich):
        for p in punkte:
            checkbox_vars[p] = st.checkbox(p)

# -----------------------------
# Bilder
# -----------------------------
st.subheader("📸 Schadenbilder")
bilder = st.file_uploader(
    "Fotos aufnehmen oder hochladen",
    type=["jpg", "jpeg", "png"],
    accept_multiple_files=True
)

# -----------------------------
# Unterschriften
# -----------------------------
st.subheader("✍️ Unterschriften")

c1, c2 = st.columns(2)
with c1:
    st.markdown("**Unterschrift Kunde**")
    sign_kunde = st_canvas(height=180, width=400, drawing_mode="freedraw",
                           stroke_width=2, stroke_color="black",
                           background_color="white", key="kunde")

with c2:
    st.markdown("**Unterschrift Fahrer**")
    sign_fahrer = st_canvas(height=180, width=400, drawing_mode="freedraw",
                            stroke_width=2, stroke_color="black",
                            background_color="white", key="fahrer")

# -----------------------------
# PDF
# -----------------------------
def save_canvas(canvas_result, path):
    if canvas_result.image_data is not None:
        img = Image.fromarray(canvas_result.image_data.astype("uint8"))
        img.save(path)

if st.button("📄 Schadenprotokoll als PDF erstellen"):
    if not kunde or not fahrer:
        st.error("Bitte Kunden- UND Fahrernamen eingeben")
        st.stop()

    tmp = tempfile.mkdtemp()
    kunde_sign = os.path.join(tmp, "kunde.png")
    fahrer_sign = os.path.join(tmp, "fahrer.png")

    save_canvas(sign_kunde, kunde_sign)
    save_canvas(sign_fahrer, fahrer_sign)

    pdf_path = os.path.join(tmp, "Schadenprotokoll.pdf")
    c = pdf_canvas.Canvas(pdf_path, pagesize=A4)
    w, h = A4
    y = h - 2 * cm

    c.setFont("Helvetica-Bold", 16)
    c.drawString(2 * cm, y, "Schadenprotokoll – CarMoveServices")
    y -= 1.5 * cm

    c.setFont("Helvetica", 11)
    c.drawString(2 * cm, y, f"Datum: {protokoll_datum.strftime('%d.%m.%Y')}")
    y -= 0.7 * cm
    c.drawString(2 * cm, y, f"Kunde: {kunde}")
    y -= 0.7 * cm
    c.drawString(2 * cm, y, f"Fahrer: {fahrer}")
    y -= 0.7 * cm
    c.drawString(2 * cm, y, f"Auftrag: {auftrag}")
    y -= 1 * cm

    c.setFont("Helvetica-Bold", 12)
    c.drawString(2 * cm, y, "Festgestellte Schäden:")
    y -= 0.7 * cm
    c.setFont("Helvetica", 10)

    for p, v in checkbox_vars.items():
        if v:
            if y < 2 * cm:
                c.showPage()
                y = h - 2 * cm
            c.drawString(2.2 * cm, y, f"- {p}")
            y -= 0.5 * cm

    if bilder:
        c.showPage()
        y = h - 2 * cm
        c.setFont("Helvetica-Bold", 12)
        c.drawString(2 * cm, y, "Schadenbilder")
        y -= 1 * cm

        for img in bilder:
            img_path = os.path.join(tmp, img.name)
            with open(img_path, "wb") as f:
                f.write(img.read())
            c.drawImage(img_path, 2 * cm, y - 6 * cm,
                        width=w - 4 * cm, height=6 * cm, preserveAspectRatio=True)
            y -= 7 * cm

c.showPage()
c.setFont("Helvetica-Bold", 12)
c.drawString(2 * cm, h - 3 * cm, "Unterschriften")

# Kunde
c.drawImage(kunde_sign, 2 * cm, h - 7 * cm, width=6 * cm, height=3 * cm)
c.setFont("Helvetica", 10)
c.drawCentredString(5 * cm, h - 7.5 * cm, "Kunde")

# Fahrer
c.drawImage(fahrer_sign, 10 * cm, h - 7 * cm, width=6 * cm, height=3 * cm)
c.drawCentredString(13 * cm, h - 7.5 * cm, "Fahrer")
 

 

    with open(pdf_path, "rb") as f:
        st.download_button("⬇️ PDF herunterladen", f, file_name="Schadenprotokoll.pdf")



