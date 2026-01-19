import streamlit as st
from streamlit_drawable_canvas import st_canvas
from PIL import Image
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas as pdf_canvas
from reportlab.lib.units import cm
from reportlab.lib import colors
import os
import tempfile
from datetime import date, datetime

# =============================
# PAGE CONFIG
# =============================
st.set_page_config(page_title="CarMoveServices Schadenprotokoll", layout="wide")

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
        st.title("🔐 Login – CarMoveServices")
        username = st.text_input("Benutzername")
        password = st.text_input("Passwort", type="password")

        if st.button("Login"):
            if username in USERS and USERS[username] == password:
                st.session_state.logged_in = True
                st.session_state.user = username
                st.rerun()
            else:
                st.error("Falsche Zugangsdaten")
        st.stop()

login()

with st.sidebar:
    st.write(f"👤 Eingeloggt als **{st.session_state.user}**")
    if st.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.rerun()

# =============================
# SCHADENPUNKTE
# =============================
schadenpunkte = {
    "Außen – Front": [
        "Frontstoßstange beschädigt", "Motorhaube beschädigt",
        "Steinschlag Windschutzscheibe", "Scheinwerfer beschädigt"
    ],
    "Außen – Seite links": [
        "Kratzer Tür vorne links", "Felgenschaden vorne links"
    ],
    "Außen – Seite rechts": [
        "Kratzer Tür vorne rechts", "Felgenschaden vorne rechts"
    ],
    "Innenraum": [
        "Fahrersitz beschädigt", "Warnleuchte aktiv"
    ],
    "Technik": [
        "Motor startet nicht", "Reifendruckwarnung aktiv"
    ]
}

# =============================
# FORMULAR
# =============================
st.title("🚗 CarMoveServices – Schadenprotokoll")

col1, col2 = st.columns(2)
with col1:
    kunde = st.text_input("Kundenname")
    fahrer = st.text_input("Fahrername")
with col2:
    auftrag = st.text_input("Kennzeichen / Auftrag")
    protokoll_datum = st.date_input("Datum", value=date.today())

st.subheader("🛠️ Schäden")
checkbox_vars = {}
for b, p in schadenpunkte.items():
    with st.expander(b):
        for s in p:
            checkbox_vars[s] = st.checkbox(s)

st.subheader("📸 Schadenbilder")
bilder = st.file_uploader(
    "Fotos aufnehmen oder hochladen",
    type=["jpg", "jpeg", "png"],
    accept_multiple_files=True
)

st.subheader("✍️ Unterschriften")
c1, c2 = st.columns(2)
with c1:
    st.markdown("**Unterschrift Kunde**")
    sign_kunde = st_canvas(height=180, width=400, key="kunde")
with c2:
    st.markdown("**Unterschrift Fahrer**")
    sign_fahrer = st_canvas(height=180, width=400, key="fahrer")

# =============================
# PDF ERSTELLEN
# =============================
def save_canvas(canvas_result, path):
    if canvas_result.image_data is not None:
        Image.fromarray(canvas_result.image_data.astype("uint8")).save(path)

if st.button("📄 Schadenprotokoll als PDF erstellen"):
    if not kunde or not fahrer:
        st.error("Bitte Kunden- UND Fahrernamen eingeben")
        st.stop()

    zeitstempel = datetime.now().strftime("%d.%m.%Y %H:%M")
    tmp = tempfile.mkdtemp()

    kunde_sign = os.path.join(tmp, "kunde.png")
    fahrer_sign = os.path.join(tmp, "fahrer.png")
    save_canvas(sign_kunde, kunde_sign)
    save_canvas(sign_fahrer, fahrer_sign)

    pdf_path = os.path.join(tmp, "Schadenprotokoll.pdf")
    c = pdf_canvas.Canvas(pdf_path, pagesize=A4)
    w, h = A4

    # ---------- HEADER ----------
    c.setFillColor(colors.HexColor("#0B5394"))
    c.rect(0, h - 3 * cm, w, 3 * cm, fill=1)

    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 20)
    c.drawString(2 * cm, h - 2 * cm, "CarMoveServices")
    c.setFont("Helvetica", 12)
    c.drawString(2 * cm, h - 2.7 * cm, "Schadenprotokoll")

    # ---------- DATEN ----------
    y = h - 4 * cm
    c.setFillColor(colors.black)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(2 * cm, y, "Kundendaten")
    c.setStrokeColor(colors.grey)
    c.line(2 * cm, y - 0.2 * cm, w - 2 * cm, y - 0.2 * cm)

    c.setFont("Helvetica", 11)
    y -= 0.8 * cm
    c.drawString(2 * cm, y, f"Kunde: {kunde}")
    y -= 0.6 * cm
    c.drawString(2 * cm, y, f"Fahrer: {fahrer}")
    y -= 0.6 * cm
    c.drawString(2 * cm, y, f"Auftrag: {auftrag}")
    y -= 0.6 * cm
    c.drawString(2 * cm, y, f"Datum: {protokoll_datum.strftime('%d.%m.%Y')}")

    # ---------- SCHÄDEN ----------
    y -= 1 * cm
    c.setFont("Helvetica-Bold", 12)
    c.drawString(2 * cm, y, "Festgestellte Schäden")
    c.line(2 * cm, y - 0.2 * cm, w - 2 * cm, y - 0.2 * cm)

    c.setFont("Helvetica", 10)
    y -= 0.8 * cm
    for p, v in checkbox_vars.items():
        if v:
            c.drawString(2.2 * cm, y, f"• {p}")
            y -= 0.45 * cm

    # ---------- UNTERSCHRIFTEN ----------
    c.showPage()
    c.setFont("Helvetica-Bold", 14)
    c.drawString(2 * cm, h - 3 * cm, "Unterschriften")

    # Kunde
    c.drawImage(kunde_sign, 2 * cm, h - 7 * cm, width=6 * cm, height=3 * cm)
    c.setFont("Helvetica", 10)
    c.drawCentredString(5 * cm, h - 7.6 * cm, f"Kunde: {kunde}")
    c.drawCentredString(5 * cm, h - 8.2 * cm, zeitstempel)

    # Fahrer
    c.drawImage(fahrer_sign, 10 * cm, h - 7 * cm, width=6 * cm, height=3 * cm)
    c.drawCentredString(13 * cm, h - 7.6 * cm, f"Fahrer: {fahrer}")
    c.drawCentredString(13 * cm, h - 8.2 * cm, zeitstempel)

    c.save()

    with open(pdf_path, "rb") as f:
        st.download_button(
            "⬇️ PDF herunterladen",
            f,
            file_name="Schadenprotokoll.pdf"
        )
