#!/usr/bin/env python3

import os
import subprocess
from concurrent.futures import ThreadPoolExecutor

script_dir = os.path.dirname(os.path.abspath(__file__))
input_folder = os.path.join(script_dir, "input")
output_folder = os.path.join(script_dir, "output")

if not os.path.exists(output_folder):
    os.makedirs(output_folder)

if not os.path.exists(input_folder):
    os.makedirs(input_folder)

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
    pdf_files = [f for f in os.listdir(input_folder) if f.lower().endswith(".pdf")]
    with ThreadPoolExecutor(max_workers=4) as executor:
        for pdf_file in pdf_files:
            input_path = os.path.join(input_folder, pdf_file)
            output_file = f"ocr_{pdf_file}"
            output_path = os.path.join(output_folder, output_file)
            executor.submit(process_pdf, input_path, output_path)

if __name__ == "__main__":
    print("Iniciando procesamiento de archivos existentes en la carpeta 'input'...")
    process_existing_files()
    print("Procesamiento completado.")
