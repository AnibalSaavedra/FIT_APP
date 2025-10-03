
import os
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import streamlit as st
from dotenv import load_dotenv

# === Carga de credenciales ===
load_dotenv()  # permite usar .env en local
SMTP_USER = st.secrets.get("SMTP_USER", os.getenv("SMTP_USER"))
SMTP_PASS = st.secrets.get("SMTP_PASS", os.getenv("SMTP_PASS"))
REPORTE_TO = st.secrets.get("REPORTE_TO", os.getenv("REPORTE_TO"))

st.set_page_config(page_title="Encuesta Preventiva CCR", page_icon="🧪", layout="centered")

if "consent_ok" not in st.session_state:
    st.session_state.consent_ok = False
if "enviado" not in st.session_state:
    st.session_state.enviado = False

def enviar_correo(reporte_to, datos):
    if not SMTP_USER or not SMTP_PASS or not reporte_to:
        raise RuntimeError("Faltan credenciales SMTP_USER/SMTP_PASS o REPORTE_TO. Configura .env o st.secrets")
    cuerpo = []
    cuerpo.append("🧪 Encuesta Preventiva de Cáncer Colorrectal (CCR)")
    cuerpo.append(f"Fecha/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    cuerpo.append("")
    cuerpo.append("Consentimiento: ACEPTADO")
    cuerpo.append("")
    for k, v in datos.items():
        cuerpo.append(f"{k}: {v}")
    text = "\n".join(cuerpo)

    msg = MIMEMultipart()
    msg["From"] = SMTP_USER
    msg["To"] = reporte_to
    msg["Subject"] = "Nuevo envío – Encuesta Preventiva CCR"
    msg.attach(MIMEText(text, "plain", _charset="utf-8"))

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(SMTP_USER, SMTP_PASS)
        server.send_message(msg)

# === Página 1: Consentimiento ===
if not st.session_state.consent_ok:
    st.title("Consentimiento informado")
    st.markdown("""
- Esta encuesta **no solicita** ni almacena datos personales sensibles.
- Puedes responder de forma **anónima**.
- Usaremos tus respuestas solo con fines de **mejora y prevención** en salud.
- Al continuar, aceptas nuestros **términos, condiciones y consentimiento** para uso de la información con fines sanitarios.
    """)
    acepto = st.checkbox("He leído y **acepto** los términos, condiciones y consentimiento.")
    st.button("Aceptar y continuar", type="primary", disabled=not acepto, on_click=lambda: st.session_state.update({'consent_ok': True}))
    st.stop()

# === Página 2: Encuesta ===
st.title("Encuesta preventiva de cáncer colorrectal")
st.caption("Responde las siguientes preguntas (selección única).")

opc = ["Sí", "No", "No recuerda"]

col1, col2 = st.columns(2)
with col1:
    edad = st.selectbox("¿Tienes entre 45 y 75 años?", opc, index=1)
    fdr = st.selectbox("¿Tienes familiares de primer grado con CCR?", opc, index=2)
    polipos = st.selectbox("¿Antecedente de pólipos o EII?", opc, index=2)
with col2:
    fit = st.selectbox("¿Test FIT+/sangre oculta en deposiciones?", opc, index=2)
    sintomas = st.selectbox("¿Síntomas de alarma (sangrado, cambio hábito, anemia)?", opc, index=2)
    colonoscopia = st.selectbox("¿Te has realizado colonoscopia en los últimos 10 años?", opc, index=2)

st.divider()
st.subheader("Contacto (opcional)")
correo = st.text_input("Correo para retroalimentación (opcional)")
ident = st.text_input("Identificación/nombre (opcional)")

if st.button("Enviar respuesta", type="primary", disabled=st.session_state.enviado):
    datos = {
        "Edad 45–75": edad,
        "Familiar 1er grado CCR": fdr,
        "Pólipos/EII": polipos,
        "FIT+/Sangre oculta": fit,
        "Síntomas alarma": sintomas,
        "Colonoscopia <10 años": colonoscopia,
        "Identificación": ident or "",
        "Correo usuario": correo or "",
    }
    try:
        enviar_correo(REPORTE_TO, datos)
        st.session_state.enviado = True
        st.success("✅ ¡Gracias! Tu respuesta fue enviada y se notificó por correo.")
    except Exception as e:
        st.warning(f"Respuesta guardada pero hubo un problema enviando el correo: {e}")
        st.session_state.enviado = False

st.info("Si dejas el correo podremos enviarte recomendaciones preventivas.")
