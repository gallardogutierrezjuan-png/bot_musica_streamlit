import asyncio
import os
import tempfile
import streamlit as st
from dotenv import load_dotenv
from parser_utils import parse_vkm_results
from telethon import TelegramClient
from telethon.sessions import StringSession

load_dotenv()


# Función para leer las claves tanto localmente como desde los Secrets de Streamlit Cloud
def get_secret(key):
    if hasattr(st, "secrets") and key in st.secrets:
        return st.secrets[key]
    if key in os.environ and os.environ[key]:
        return os.environ[key]
    return None


API_ID = get_secret("TELEGRAM_API_ID")
API_HASH = get_secret("TELEGRAM_API_HASH")
SESSION_STRING = get_secret("TELEGRAM_STRING_SESSION")
BOT_USERNAME = "vkmusbot"

_client = None


def get_telegram_client():
    global _client
    if _client is None:
        if not API_ID or not API_HASH:
            raise ValueError(
                "No se encontraron las credenciales TELEGRAM_API_ID o"
                " TELEGRAM_API_HASH en los Secrets de Streamlit."
            )

        # Convertir API_ID a entero de forma segura
        api_id_int = int(str(API_ID).strip())
        api_hash_str = str(API_HASH).strip()

        if SESSION_STRING:
            _client = TelegramClient(
                StringSession(str(SESSION_STRING).strip()),
                api_id_int,
                api_hash_str,
            )
        else:
            _client = TelegramClient("sesion_prueba", api_id_int, api_hash_str)

    return _client


async def buscar_canciones_async(query):
    client = get_telegram_client()
    await client.start()

    bot_entity = await client.get_input_entity(BOT_USERNAME)
    await client.send_message(bot_entity, query)

    await asyncio.sleep(4)

    messages = await client.get_messages(bot_entity, limit=3)
    bot_response = None
    for msg in messages:
        if not msg.out and msg.buttons:
            bot_response = msg
            break

    if not bot_response:
        return [], None

    songs = parse_vkm_results(bot_response.text)
    return songs, bot_response.id


def realizar_busqueda(query):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    return loop.run_until_complete(buscar_canciones_async(query))


async def descargar_cancion_async(msg_id, index_opcion):
    client = get_telegram_client()
    await client.start()

    bot_entity = await client.get_input_entity(BOT_USERNAME)
    message = await client.get_messages(bot_entity, ids=msg_id)

    if not message or not message.buttons:
        return None, "No se encontró el mensaje original de resultados."

    fila = 0 if index_opcion < 4 else 1
    col = index_opcion % 4

    await message.click(fila, col)
    await asyncio.sleep(7)

    audio_messages = await client.get_messages(bot_entity, limit=2)

    for amsg in audio_messages:
        if not amsg.out and amsg.media:
            temp_dir = tempfile.gettempdir()
            filename = (
                amsg.file.name
                if hasattr(amsg, "file") and amsg.file.name
                else "cancion.mp3"
            )
            file_path = os.path.join(temp_dir, filename)

            await client.download_media(amsg, file_path)
            return file_path, filename

    return None, "El bot no entregó el archivo de audio."


def descargar_cancion(msg_id, index_opcion):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    return loop.run_until_complete(
        descargar_cancion_async(msg_id, index_opcion)
    )
