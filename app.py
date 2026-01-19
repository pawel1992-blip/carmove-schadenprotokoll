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
            if USERS.get(username) == password:
                st.session_state.logged_in = True
                st.session_state.user = username
                st.experimental_rerun()
            else:
                st.error("Falsche Zugangsdaten")
        st.stop()

login()

# Sidebar Logout
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

# Kundendaten
col1, col2 = st.columns(2)
with col1:
    kunde = st.text_input("Kundenname")
    fahrer = st.text_input("Fahrername")
with col2:
    auftrag = st.text_input("Kennzeichen / Auftrag")
    protokoll_datum = st.date_input("Datum", value=date.today())

# Schäden
st.subheader("🛠️ Schäden")
checkbox_vars = {}
for bereich, punkte in schadenpunkte.items():
    with st.expander(bereich):
        st.markdown(f"<b style='color:#0F4C81;'>{bereich}</b>", unsafe_allow_html=True)
        for punkt in punkte:
            checkbox_vars[punkt] = st.checkbox(punkt)

# Schadenbilder
st.subheader("📸 Schadenbilder")
bilder = st.file_uploader("Fotos aufnehmen oder hochladen", type=["jpg","jpeg","png"], accept_multiple_files=True)

# Unterschriften
st.subheader("✍️ Unterschriften")
c1, c2 = st.columns(2)
with c1:
    st.markdown("**Kunde**")
    sign_kunde = st_canvas(height=180, width=400, background_color="white", key="kunde")
with c2:
    st.markdown("**Fahrer**")
    sign_fahrer = st_canvas(height=180, width=400, background_color="white", key="fahrer")

def save_signature(canvas_result, path):
    """Speichert die Unterschrift falls vorhanden."""
    if canvas_result and canvas_result.image_data is not None:
        Image.fromarray(canvas_result.image_data.astype("uint8")).convert("RGB").save(path)

# =============================
# PDF GENERIEREN
# =============================
def create_pdf(pdf_path, kunde, fahrer, auftrag, protokoll_datum, checkbox_vars, bilder, sign_paths):
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
    for label, value in [("Datum", protokoll_datum.strftime('%d.%m.%Y')), 
                         ("Kunde", kunde), 
                         ("Fahrer", fahrer), 
                         ("Auftrag", auftrag)]:
        c.drawString(2*cm, y, f"{label}: {value}")
        y -= 0.6*cm
    y -= 0.4*cm

    # Schäden
    for bereich, punkte in schadenpunkte.items():
        selected = [p for p in punkte if checkbox_vars.get(p)]
        if not selected:
            continue
        box_height = 0.8 + 0.5*len(selected)
        if y - box_height*cm < 2*cm:
            c.showPage()
            y = h - 2*cm

        # Schatten & Box
        c.setFillColor(HexColor("#d9d9d9"))
        c.roundRect(2.1*cm, y - box_height*cm - 0.1*cm, w - 4.2*cm, box_height*cm, 6, fill=True, stroke=False)
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
        for punkt in selected:
            if y < 2*cm:
                c.showPage()
                y = h - 2*cm
            c.drawString(2.4*cm, y, f"- {punkt}")
            y -= 0.5*cm
        y -= 0.3*cm

    # Bilder
    if bilder:
        c.showPage()
        y = h - 2*cm
        c.setFont("Helvetica-Bold",12)
        c.setFillColor(HexColor("#0F4C81"))
        c.drawString(2*cm,y,"Schadenbilder")
        y -= 1*cm
        for img_file in bilder:
            img = Image.open(img_file).convert("RGB")
            tmp_path = os.path.join(tempfile.gettempdir(), img_file.name)
            img.save(tmp_path)
            if y < 7*cm:
                c.showPage()
                y = h - 2*cm
            c.drawImage(tmp_path,2*cm,y-6*cm,width=w-4*cm,height=6*cm,preserveAspectRatio=True)
            y -= 7*cm

    # Unterschriften
    c.showPage()
    y = h - 3*cm
    c.setFont("Helvetica-Bold",12)
    c.drawString(2*cm,y,"Unterschriften:")
    zeit = datetime.now().strftime("%d.%m.%Y %H:%M")

    if sign_paths.get("kunde"):
        c.drawImage(sign_paths["kunde"], 2*cm, y-4*cm, width=6*cm, height=3*cm)
        c.setFont("Helvetica",10)
        c.drawCentredString(5*cm, y-4.6*cm, f"Kunde: {kunde}")
        c.drawCentredString(5*cm, y-5.2*cm, zeit)

    if sign_paths.get("fahrer"):
        c.drawImage(sign_paths["fahrer"], 10*cm, y-4*cm, width=6*cm, height=3*cm)
        c.drawCentredString(13*cm, y-4.6*cm, f"Fahrer: {fahrer}")
        c.drawCentredString(13*cm, y-5.2*cm, zeit)

    c.save()

# PDF erstellen
if st.button("📄 Schadenprotokoll als PDF erstellen"):
    if not kunde or not fahrer:
        st.error("Bitte Kunden- UND Fahrernamen eingeben")
        st.stop()

    tmp_dir = tempfile.mkdtemp()
    sign_paths = {
        "kunde": os.path.join(tmp_dir, "kunde.png"),
        "fahrer": os.path.join(tmp_dir, "fahrer.png")
    }
    save_signature(sign_kunde, sign_paths["kunde"])
    save_signature(sign_fahrer, sign_paths["fahrer"])

    pdf_path = os.path.join(tmp_dir, "Schadenprotokoll.pdf")
    create_pdf(pdf_path, kunde, fahrer, auftrag, protokoll_datum, checkbox_vars, bilder, sign_paths)

    with open(pdf_path,"rb") as f:
        st.download_button("⬇️ PDF herunterladen", f, file_name="Schadenprotokoll.pdf")
