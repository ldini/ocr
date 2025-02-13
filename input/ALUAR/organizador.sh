#!/bin/bash

# Ruta donde se ejecutará el script (MODIFICA SEGÚN TU NECESIDAD)
BASE_DIR="/app/ocr/input/ALUAR"

# Verifica si `inotifywait` está instalado
if ! command -v inotifywait &> /dev/null; then
    echo "Error: inotify-tools no está instalado. Instálalo con: sudo apt install inotify-tools"
    exit 1
fi

echo "Monitoreando archivos dentro de subcarpetas de segundo nivel en: $BASE_DIR"

# Loop infinito para monitorear la carpeta y subcarpetas de segundo nivel
while true; do
    # Detectar nuevos archivos en subcarpetas de segundo nivel
    FILE_PATH=$(inotifywait -r -e create --format "%w%f" "$BASE_DIR" | grep -E "/[0-9A-Za-z_-]+/[0-9A-Za-z_-]+/[0-9]+\.[0-9]+\.[0-9]+.*$")

    if [[ -n "$FILE_PATH" ]]; then
        # Extraer solo el nombre del archivo
        FILE_NAME=$(basename "$FILE_PATH")

        # Extraer la carpeta contenedora (de segundo nivel)
        PARENT_DIR=$(dirname "$FILE_PATH")
        
        # Extraer los tres primeros niveles del nombre del archivo (ej: 5.1.1)
        FOLDER_NAME=$(echo "$FILE_NAME" | grep -oE "^[0-9]+\.[0-9]+\.[0-9]+")

        if [[ -n "$FOLDER_NAME" ]]; then
            # Crear la carpeta dentro del directorio donde estaba el archivo
            DEST_DIR="$PARENT_DIR/$FOLDER_NAME"
            mkdir -p "$DEST_DIR"

            # Mover el archivo a la carpeta correspondiente
            mv "$FILE_PATH" "$DEST_DIR/"
            echo "📂 Movido: $FILE_NAME → $DEST_DIR/"
        fi
    fi
done