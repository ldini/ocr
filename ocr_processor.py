#!/usr/bin/env python3

import os
import subprocess
from concurrent.futures import ThreadPoolExecutor
from PIL import Image
from datetime import datetime

script_dir = os.path.dirname(os.path.abspath(__file__))
input_folder = os.path.join(script_dir, "input")
output_folder = os.path.join(script_dir, "output")

if not os.path.exists(output_folder):
    os.makedirs(output_folder)

if not os.path.exists(input_folder):
    os.makedirs(input_folder)

def convert_image_to_pdf(image_path, pdf_path):
    try:
        with Image.open(image_path) as img:
            img = img.convert("RGB")  # Asegurarse de que sea un PDF compatible
            img.save(pdf_path)
        return True
    except Exception as e:
        print(f"Error al convertir {os.path.basename(image_path)} a PDF: {e}")
        return False

def process_pdf(input_path, output_path):
    command = [
        "docker", "run", "--rm",
        "-v", f"{os.path.abspath(input_folder)}:/data/input",
        "-v", f"{os.path.abspath(output_folder)}:/data/output",
        "jbarlow83/ocrmypdf",
        f"/data/input/{os.path.basename(input_path)}",
        f"/data/output/{os.path.basename(output_path)}",
        "--force-ocr",
        "--image-dpi", "200",
        "--jobs", "4",
    ]

    print(f"Procesando: {os.path.basename(input_path)}")
    try:
        subprocess.run(command, check=True)
        print(f"Archivo procesado: {os.path.basename(output_path)}")
    except subprocess.CalledProcessError as e:
        print(f"Error al procesar {os.path.basename(input_path)}: {e}")
        return False
    return True

def process_existing_files():
    files = [f for f in os.listdir(input_folder) if f.lower().endswith((".pdf", ".jpg", ".jpeg", ".png"))]
    with ThreadPoolExecutor(max_workers=4) as executor:
        for file in files:
            input_path = os.path.join(input_folder, file)
            if file.lower().endswith(".pdf"):
                output_file = f"{file}"
                output_path = os.path.join(output_folder, output_file)
                executor.submit(process_pdf, input_path, output_path)
            else:
                # Convertir imagen a PDF y procesar
                temp_pdf_path = os.path.join(input_folder, f"{os.path.splitext(file)[0]}.pdf")
                if convert_image_to_pdf(input_path, temp_pdf_path):
                    output_file = f"{os.path.splitext(file)[0]}.pdf"
                    output_path = os.path.join(output_folder, output_file)
                    executor.submit(process_pdf, temp_pdf_path, output_path)

if __name__ == "__main__":
    start_time = datetime.now()
    print(f"Inicio del procesamiento: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")

    print("Iniciando procesamiento de archivos existentes en la carpeta 'input'...")
    process_existing_files()

    end_time = datetime.now()
    print(f"Procesamiento completado.")
    print(f"Hora de finalización: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")

    elapsed_time = end_time - start_time
    print(f"Duración total: {elapsed_time}")
