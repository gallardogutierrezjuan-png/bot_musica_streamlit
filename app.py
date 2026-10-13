import os
import streamlit as st
from telegram_service import descargar_cancion, realizar_busqueda

# Configuración de página
st.set_page_config(
    page_title="Music Downloader", page_icon="🎵", layout="centered"
)


# Cargar CSS personalizado
def cargar_css():
    if os.path.exists("style.css"):
        with open("style.css", "r") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


cargar_css()

st.title("🎵 Plataforma de Búsqueda de Música")
st.caption("Interfaz web conectada en tiempo real con Telegram Engine")

# Inicializar sesión de estado
if "resultados" not in st.session_state:
    st.session_state.resultados = []
if "msg_id" not in st.session_state:
    st.session_state.msg_id = None

# Buscador principal
with st.form(key="search_form"):
    col1, col2 = st.columns([4, 1])
    with col1:
        query = st.text_input(
            "Buscar por Artista, Canción o Álbum",
            placeholder="Ejemplo: Radiohead",
            label_visibility="collapsed",
        )
    with col2:
        submit_button = st.form_submit_button(label="Buscar 🔍")

if submit_button and query.strip():
    with st.spinner("Buscando en el catálogo..."):
        try:
            songs, msg_id = realizar_busqueda(query.strip())
            st.session_state.resultados = songs
            st.session_state.msg_id = msg_id

            if not songs:
                st.warning(
                    "No se encontraron coincidencias o el servicio demoró en"
                    " responder."
                )
        except Exception as e:
            st.error(f"Error durante la búsqueda: {e}")

# Desplegar Lista de Resultados
if st.session_state.resultados:
    st.subheader(
        f"Resultados de la búsqueda ({len(st.session_state.resultados)})"
    )

    for idx, song in enumerate(st.session_state.resultados):
        st.markdown(
            f"""
            <div class="song-card">
                <div class="song-title">{song['id']}. {song['title']}</div>
                <div class="song-artist">👤 {song['artist']}</div>
                <div class="song-meta">⏱️ Duración: {song['duration']} | 📦 Tamaño: {song['size']} {f"| 🎧 Bitrate: {song['stats']}" if song['stats'] else ""}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        col_btn, _ = st.columns([2, 3])
        with col_btn:
            if st.button(
                f"Obtener/Descargar #{song['id']}", key=f"btn_{song['id']}"
            ):
                with st.spinner(
                    f"Descargando '{song['title']}' desde Telegram..."
                ):
                    file_path, filename_or_error = descargar_cancion(
                        st.session_state.msg_id, idx
                    )

                    if file_path and os.path.exists(file_path):
                        st.success("¡Archivo listo para descargar!")
                        with open(file_path, "rb") as file:
                            st.download_button(
                                label=f"⬇️ Descargar {song['title']}.mp3",
                                data=file,
                                file_name=filename_or_error,
                                mime="audio/mpeg",
                            )
                        # Limpieza del archivo temporal tras preparar el botón
                    else:
                        st.error(
                            f"No se pudo obtener el archivo: {filename_or_error}"
                        )

        st.divider()