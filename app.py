import streamlit as st
from streamlit_drawable_canvas import st_canvas
from PIL import Image
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas as pdf_canvas
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor
import os
import tempfile
from datetime import date, datetime

# =============================
# LOGIN
# =============================
USERS = {"admin": "2804CarM", "fahrer": "carmove"}

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
                st.experimental_rerun()
            else:
                st.error("Falsche Zugangsdaten")
        st.stop()

login()

with st.sidebar:
    st.markdown(f"**👤 Eingeloggt als:** {st.session_state.user}")
    if st.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.experimental_rerun()

# =============================
# SCHADENPUNKTE
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
st.markdown("<h1 style='color:#0F4C81;'>🚗 CarMoveServices – Schadenprotokoll</h1>", unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    kunde = st.text_input("Kundenname")
    fahrer = st.text_input("Fahrername")
with col2:
    auftrag = st.text_input("Kennzeichen / Auftrag")
    protokoll_datum = st.date_input("Datum", value=date.today())

st.subheader("🛠️ Schäden")
checkbox_vars = {}
for bereich, punkte in schadenpunkte.items():
    with st.expander(bereich):
        for punkt in punkte:
            checkbox_vars[punkt] = st.checkbox(punkt)

st.subheader("📸 Schadenbilder")
bilder = st.file_uploader("Fotos aufnehmen oder hochladen", type=["jpg","jpeg","png"], accept_multiple_files=True)

st.subheader("✍️ Unterschriften")
c1, c2 = st.columns(2)
with c1:
    st.markdown("**Kunde**")
    sign_kunde = st_canvas(height=180, width=400, background_color="white", key="kunde")
with c2:
    st.markdown("**Fahrer**")
    sign_fahrer = st_canvas(height=180, width=400, background_color="white", key="fahrer")

def save_signature(canvas_result, path):
    if canvas_result.image_data is not None:
        Image.fromarray(canvas_result.image_data.astype("uint8")).convert("RGB").save(path)

# =============================
# PDF GENERIEREN
# =============================
if st.button("📄 Schadenprotokoll als PDF erstellen"):
    if not kunde or not fahrer:
        st.error("Bitte Kunden- UND Fahrernamen eingeben")
        st.stop()

    tmp = tempfile.mkdtemp()
    zeit = datetime.now().strftime("%d.%m.%Y %H:%M")

    ks = os.path.join(tmp, "kunde.png")
    fs = os.path.join(tmp, "fahrer.png")
    save_signature(sign_kunde, ks)
    save_signature(sign_fahrer, fs)

    pdf_path = os.path.join(tmp, "Schadenprotokoll.pdf")
    c = pdf_canvas.Canvas(pdf_path, pagesize=A4)
    w, h = A4
    y = h - 2*cm

    # HEADER
    c.setFont("Helvetica-Bold",18)
    c.setFillColor(HexColor("#0F4C81"))
    c.drawString(2*cm,y,"Schadenprotokoll – CarMoveServices")
    y -= 2*cm

    c.setFont("Helvetica",11)
    c.setFillColorRGB(0,0,0)
    c.drawString(2*cm,y,f"Datum: {protokoll_datum.strftime('%d.%m.%Y')}")
    y -= 0.6*cm
    c.drawString(2*cm,y,f"Kunde: {kunde}")
    y -= 0.6*cm
    c.drawString(2*cm,y,f"Fahrer: {fahrer}")
    y -= 0.6*cm
    c.drawString(2*cm,y,f"Auftrag: {auftrag}")
    y -= 1*cm

    # SCHÄDEN MIT GRAUEM HINTERGRUND
    for bereich, punkte in schadenpunkte.items():
        checked = [p for p in punkte if checkbox_vars[p]]
        if not checked:
            continue

        box_height = 0.8 + 0.5*len(checked)
        if y - box_height*cm < 2*cm:
            c.showPage()
            y = h - 2*cm

        # Grauer Hintergrund
        c.setFillColor(HexColor("#f0f0f0"))
        c.roundRect(2*cm, y - box_height*cm, w - 4*cm, box_height*cm, 6, fill=True, stroke=False)

        # Überschrift
        c.setFont("Helvetica-Bold",12)
        c.setFillColor(HexColor("#0F4C81"))
        c.drawString(2.2*cm, y, bereich)
        y -= 0.8*cm

        # Punkte
        c.setFont("Helvetica",10)
        c.setFillColorRGB(0,0,0)
        for punkt in checked:
            if y < 2*cm:
                c.showPage()
                y = h - 2*cm
            c.drawString(2.4*cm, y, f"- {punkt}")
            y -= 0.5*cm
        y -= 0.3*cm

    # BILDER
    if bilder:
        c.showPage()
        y = h - 2*cm
        c.setFont("Helvetica-Bold",12)
        c.setFillColor(HexColor("#0F4C81"))
        c.drawString(2*cm,y,"Schadenbilder")
        y -= 1*cm
        for img_file in bilder:
            img = Image.open(img_file).convert("RGB")
            img_path = os.path.join(tmp,img_file.name)
            img.save(img_path)
            if y < 7*cm:
                c.showPage()
                y = h - 2*cm
            c.drawImage(img_path,2*cm,y-6*cm,width=w-4*cm,height=6*cm,preserveAspectRatio=True)
            y -= 7*cm

    # UNTERSCHRIFTEN
    c.showPage()
    c.setFont("Helvetica-Bold",12)
    c.setFillColorRGB(0,0,0)
    c.drawString(2*cm,h-3*cm,"Unterschriften:")

    c.drawImage(ks,2*cm,h-7*cm,width=6*cm,height=3*cm)
    c.setFont("Helvetica",10)
    c.drawCentredString(5*cm,h-7.6*cm,f"Kunde: {kunde}")
    c.drawCentredString(5*cm,h-8.2*cm,zeit)

    c.drawImage(fs,10*cm,h-7*cm,width=6*cm,height=3*cm)
    c.drawCentredString(13*cm,h-7.6*cm,f"Fahrer: {fahrer}")
    c.drawCentredString(13*cm,h-8.2*cm,zeit)

    c.save()

    with open(pdf_path,"rb") as f:
        st.download_button("⬇️ PDF herunterladen",f,file_name="Schadenprotokoll.pdf")
