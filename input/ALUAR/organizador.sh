#!/bin/bash

# Ruta donde se ejecutará el script (MODIFICA SEGÚN TU NECESIDAD)
BASE_DIR="/app/ocr/input/ALUAR"

# Verifica si `inotifywait` está instalado
if ! command -v inotifywait &> /dev/null; then
    echo "Error: inotify-tools no está instalado. Instálalo con: sudo yum install inotify-tools"
    exit 1
fi

# Organizar archivos existentes antes de iniciar la monitorización
echo "📂 Organizando archivos existentes en $BASE_DIR..."

find "$BASE_DIR" -mindepth 2 -type f | while read FILE_PATH; do
    FILE_NAME=$(basename "$FILE_PATH")
    PARENT_DIR=$(dirname "$FILE_PATH")

    # Extraer los tres primeros niveles del nombre del archivo (ej: 1.1.1)
    FOLDER_NAME=$(echo "$FILE_NAME" | grep -oE "^[0-9]+\.[0-9]+\.[0-9]+")

    if [[ -n "$FOLDER_NAME" ]]; then
        DEST_DIR="$PARENT_DIR/$FOLDER_NAME"  # Mantenerlo dentro de su carpeta actual
        mkdir -p "$DEST_DIR"
        mv "$FILE_PATH" "$DEST_DIR/"
        echo "✅ Archivo existente movido: $FILE_NAME → $DEST_DIR/"
    fi
done

# Verificar si hay archivos sueltos en el segundo nivel y organizarlos
echo "🔍 Revisando si hay archivos sueltos en el segundo nivel..."
find "$BASE_DIR" -mindepth 2 -maxdepth 3 -type f | while read FILE_PATH; do
    FILE_NAME=$(basename "$FILE_PATH")
    PARENT_DIR=$(dirname "$FILE_PATH")

    # Extraer los tres primeros niveles del nombre del archivo (ej: 1.1.1)
    FOLDER_NAME=$(echo "$FILE_NAME" | grep -oE "^[0-9]+\.[0-9]+\.[0-9]+")

    if [[ -n "$FOLDER_NAME" ]]; then
        DEST_DIR="$PARENT_DIR/$FOLDER_NAME"
        mkdir -p "$DEST_DIR"
        mv "$FILE_PATH" "$DEST_DIR/"
        echo "✅ Archivo suelto movido: $FILE_NAME → $DEST_DIR/"
    fi
done

echo "🚀 Monitoreando archivos dentro de subcarpetas de segundo nivel en: $BASE_DIR"

# Loop infinito para monitorear la carpeta y subcarpetas de segundo nivel
while true; do
    FILE_PATH=$(inotifywait -r -e create --format "%w%f" "$BASE_DIR")

    if [[ -n "$FILE_PATH" ]]; then
        FILE_NAME=$(basename "$FILE_PATH")
        PARENT_DIR=$(dirname "$FILE_PATH")

        # Solo procesar archivos dentro de **dos niveles de profundidad**
        DEPTH=$(echo "$PARENT_DIR" | awk -F'/' '{print NF}')
        BASE_DEPTH=$(echo "$BASE_DIR" | awk -F'/' '{print NF}')
        REL_DEPTH=$((DEPTH - BASE_DEPTH))

        if [[ "$REL_DEPTH" -ge 2 ]]; then
            # Extraer los tres primeros niveles del nombre del archivo (ej: 1.1.1)
            FOLDER_NAME=$(echo "$FILE_NAME" | grep -oE "^[0-9]+\.[0-9]+\.[0-9]+")

            if [[ -n "$FOLDER_NAME" ]]; then
                DEST_DIR="$PARENT_DIR/$FOLDER_NAME"  # Mantener dentro de su carpeta original
                mkdir -p "$DEST_DIR"

                # Mover el archivo a la carpeta correspondiente
                mv "$FILE_PATH" "$DEST_DIR/"
                echo "📂 Movido: $FILE_NAME → $DEST_DIR/"
            fi
        else
            echo "❌ Archivo ignorado (fuera de profundidad permitida): $FILE_PATH"
        fi
    fi
done
