import streamlit as st
import os
import json
from datetime import datetime, date

import gspread
import streamlit as st

from google.oauth2.service_account import Credentials

# =========================================================
# CONFIGURACIÓN
# =========================================================

st.set_page_config(
    page_title="Préstamo de Tipodones",
    page_icon="🦷",
    layout="centered"
)


# =========================================================
# ESTILOS
# =========================================================

st.markdown(
    """
    <style>
        .main {
            max-width: 800px;
            margin: auto;
        }

        h1 {
            text-align: center;
        }

        .subtitulo {
            text-align: center;
            color: #666;
            margin-bottom: 30px;
        }
    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# CONEXIÓN CON GOOGLE SHEETS
# =========================================================

@st.cache_resource
def conectar_google_sheets():

    credentials_info = json.loads(
        os.environ["GOOGLE_CREDENTIALS"]
    )

    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]

    credentials = Credentials.from_service_account_info(
        credentials_info,
        scopes=scopes
    )

    client = gspread.authorize(credentials)

    spreadsheet = client.open(
        "Registro de Préstamo de Tipodones"
    )

    sheet = spreadsheet.worksheet("Prestamos")

    return sheet


try:
    sheet = conectar_google_sheets()

except Exception as e:

    st.error(
        "No se pudo conectar con Google Sheets."
    )

    st.code(str(e))

    st.stop()


# =========================================================
# ENCABEZADO
# =========================================================

st.title("🦷 Préstamo de Tipodones")

st.markdown(
    '<p class="subtitulo">'
    'Centro de simulación - Facultad de Estomatología'
    '</p>',
    unsafe_allow_html=True
)


# =========================================================
# FORMULARIO
# =========================================================

with st.form("formulario_prestamo"):

    st.subheader("Datos del alumno")

    nombre = st.text_input(
        "Nombre completo",
        placeholder="Ej. Juan Pérez García"
    )

    dni = st.text_input(
        "DNI",
        placeholder="Ej. 12345678",
        max_chars=8
    )

    sede = st.selectbox(
        "Sede",
        [
            "SMP",
            "La Molina"
        ]
    )

    fecha_prestamo = st.date_input(
        "Fecha del préstamo",
        value=date.today(),
        format="DD/MM/YYYY"
    )

    tipodon = st.selectbox(
        "Tipodón",
        options=list(range(1, 71)),
        format_func=lambda x: f"Tipodón {x}"
    )

    enviar = st.form_submit_button(
        "Registrar préstamo",
        use_container_width=True
    )


# =========================================================
# PROCESAMIENTO
# =========================================================

if enviar:

    # ---------------------------------------------
    # VALIDAR NOMBRE
    # ---------------------------------------------

    if not nombre.strip():

        st.warning(
            "Por favor, ingresa tu nombre completo."
        )

        st.stop()


    # ---------------------------------------------
    # VALIDAR DNI
    # ---------------------------------------------

    dni = dni.strip()

    if not dni.isdigit():

        st.warning(
            "El DNI debe contener solamente números."
        )

        st.stop()


    if len(dni) != 8:

        st.warning(
            "El DNI debe tener exactamente 8 dígitos."
        )

        st.stop()


    # ---------------------------------------------
    # OBTENER REGISTROS EXISTENTES
    # ---------------------------------------------

    registros = sheet.get_all_records()


    # ---------------------------------------------
    # VERIFICAR TIPODÓN DUPLICADO
    # ---------------------------------------------

    tipodon_ocupado = False

    for registro in registros:

        tipodon_registrado = str(
            registro.get("Tipodón", "")
        ).strip()

        fecha_registrada = str(
            registro.get("Fecha préstamo", "")
        ).strip()

        if (
            tipodon_registrado == str(tipodon)
            and fecha_registrada
            == fecha_prestamo.strftime("%d/%m/%Y")
        ):

            tipodon_ocupado = True

            break


    if tipodon_ocupado:

        st.error(
            f"❌ El Tipodón {tipodon} "
            f"ya está registrado para el "
            f"{fecha_prestamo.strftime('%d/%m/%Y')}."
        )

        st.stop()


    # ---------------------------------------------
    # GUARDAR EN GOOGLE SHEETS
    # ---------------------------------------------

    fecha_registro = datetime.now().strftime(
        "%d/%m/%Y %H:%M:%S"
    )

    nueva_fila = [
        fecha_registro,
        nombre.strip(),
        dni,
        sede,
        fecha_prestamo.strftime("%d/%m/%Y"),
        tipodon
    ]

    try:

        sheet.append_row(
            nueva_fila,
            value_input_option="USER_ENTERED"
        )

        st.success(
            "✅ ¡Préstamo registrado correctamente!"
        )

        st.info(
            f"Tipodón {tipodon} · "
            f"{sede} · "
            f"{fecha_prestamo.strftime('%d/%m/%Y')}"
        )

    except Exception as e:

        st.error(
            "Ocurrió un error al guardar "
            "el préstamo."
        )

        st.code(str(e))