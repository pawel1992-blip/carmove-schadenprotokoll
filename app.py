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
        u = st.text_input("Benutzername")
        p = st.text_input("Passwort", type="password")
        if st.button("Login"):
            if u in USERS and USERS[u] == p:
                st.session_state.logged_in = True
                st.session_state.user = u
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
# SCHADENPUNKTE (VOLL)
# =============================
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
        "Panoramadach beschädigt",
        "Seitenscheibe vorne links beschädigt", "Seitenscheibe vorne rechts beschädigt",
        "Seitenscheibe hinten links beschädigt", "Seitenscheibe hinten rechts beschädigt"
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
    sign_kunde = st_canvas(height=180, width=400, background_color="white", key="kunde")
with c2:
    sign_fahrer = st_canvas(height=180, width=400, background_color="white", key="fahrer")

def save_signature(canvas_result, path):
    if canvas_result.image_data is not None:
        Image.fromarray(canvas_result.image_data.astype("uint8")).convert("RGB").save(path)

# =============================
# PDF
# =============================
if st.button("📄 Schadenprotokoll als PDF erstellen"):
    tmp = tempfile.mkdtemp()
    zeit = datetime.now().strftime("%d.%m.%Y %H:%M")

    ks = os.path.join(tmp, "kunde.png")
    fs = os.path.join(tmp, "fahrer.png")
    save_signature(sign_kunde, ks)
    save_signature(sign_fahrer, fs)

    pdf_path = os.path.join(tmp, "Schadenprotokoll.pdf")
    c = pdf_canvas.Canvas(pdf_path, pagesize=A4)
    w, h = A4

    # HEADER
    c.setFillColor(colors.HexColor("#111827"))
    c.rect(0, h - 4 * cm, w, 4 * cm, fill=1)
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 22)
    c.drawString(2 * cm, h - 2.5 * cm, "CarMoveServices")
    c.setFont("Helvetica", 12)
    c.drawString(2 * cm, h - 3.3 * cm, "Digitales Schadenprotokoll")

    # DATEN
    y = h - 5 * cm
    c.setFillColor(colors.black)
    c.setFont("Helvetica", 11)
    c.drawString(2 * cm, y, f"Kunde: {kunde}")
    y -= 0.6 * cm
    c.drawString(2 * cm, y, f"Fahrer: {fahrer}")
    y -= 0.6 * cm
    c.drawString(2 * cm, y, f"Auftrag: {auftrag}")
    y -= 0.6 * cm
    c.drawString(2 * cm, y, f"Datum: {protokoll_datum.strftime('%d.%m.%Y')}")

    # SCHÄDEN (DYNAMISCH)
    y -= 1 * cm
    c.setFont("Helvetica-Bold", 12)
    c.drawString(2 * cm, y, "Festgestellte Schäden")
    y -= 0.7 * cm
    c.setFont("Helvetica", 10)

    for p, v in checkbox_vars.items():
        if v:
            if y < 2 * cm:
                c.showPage()
                y = h - 2 * cm
                c.setFont("Helvetica", 10)
            c.drawString(2.2 * cm, y, f"• {p}")
            y -= 0.45 * cm

    # BILDER
    if bilder:
        c.showPage()
        y = h - 2 * cm
        c.setFont("Helvetica-Bold", 14)
        c.drawString(2 * cm, y, "Schadenbilder")
        y -= 1 * cm

        for up in bilder:
            img = Image.open(up).convert("RGB")
            pth = os.path.join(tmp, up.name)
            img.save(pth)

            if y < 7 * cm:
                c.showPage()
                y = h - 2 * cm

            c.drawImage(pth, 2 * cm, y - 6 * cm, width=w - 4 * cm, height=6 * cm, preserveAspectRatio=True)
            y -= 7 * cm

    # UNTERSCHRIFTEN
    c.showPage()
    c.setFont("Helvetica-Bold", 14)
    c.drawString(2 * cm, h - 3 * cm, "Digitale Bestätigung")

    c.drawImage(ks, 2 * cm, h - 7 * cm, width=6 * cm, height=3 * cm)
    c.setFont("Helvetica", 10)
    c.drawCentredString(5 * cm, h - 7.6 * cm, f"Kunde: {kunde}")
    c.drawCentredString(5 * cm, h - 8.2 * cm, zeit)

    c.drawImage(fs, 10 * cm, h - 7 * cm, width=6 * cm, height=3 * cm)
    c.drawCentredString(13 * cm, h - 7.6 * cm, f"Fahrer: {fahrer}")
    c.drawCentredString(13 * cm, h - 8.2 * cm, zeit)

    c.save()

    with open(pdf_path, "rb") as f:
        st.download_button("⬇️ PDF herunterladen", f, file_name="Schadenprotokoll.pdf")
