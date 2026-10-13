import re


def parse_vkm_results(text):
    """Parsea el texto recibido de @vkm_bot para extraer las canciones y sus metadatos."""
    songs = []
    # Patrón Regex para capturar: ID, Artista - Canción, Duración, Tamaño y Reproducciones/Bitrate
    pattern = r"\*\*(\d+)\.\*\*\s+(.*?)\s+--\s+(.*?)\s+__(\d+:\d+)\s+([\d\.]+M)\s+([\d\.]+k?)__"

    matches = re.findall(pattern, text)

    for match in matches:
        num_str, artist, title, duration, size, stats = match
        songs.append(
            {
                "id": int(num_str),
                "artist": artist.strip(),
                "title": title.strip(),
                "duration": duration.strip(),
                "size": size.strip(),
                "stats": stats.strip(),
            }
        )

    # Si la expresión regular anterior no captura formatos ligeramente distintos, intentamos un fallback por líneas
    if not songs:
        lines = text.split("\n")
        for line in lines:
            line = line.strip()
            match_simple = re.match(r"\*\*(\d+)\.\*\*\s+(.*)", line)
            if match_simple:
                num = int(match_simple.group(1))
                content = match_simple.group(2)
                # Separar artista y título si hay guión
                parts = content.split(" - ", 1)
                artist = parts[0] if len(parts) > 1 else "Desconocido"
                title = parts[1] if len(parts) > 1 else parts[0]
                songs.append(
                    {
                        "id": num,
                        "artist": artist.replace("__", "").strip(),
                        "title": title.replace("__", "").strip(),
                        "duration": "N/A",
                        "size": "N/A",
                        "stats": "",
                    }
                )

    return songs