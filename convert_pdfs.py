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

pdf_files = [f for f in os.listdir(input_folder) if f.lower().endswith('.pdf')]

def process_pdf(pdf_file):
    input_path = os.path.join(input_folder, pdf_file)
    output_file = f"ocr_{pdf_file}"  
    output_path = os.path.join(output_folder, output_file)
    
    command = [
        "docker", "run", "--rm",
        "-v", f"{input_folder}:/data/input", 
        "-v", f"{output_folder}:/data/output",  
        "jbarlow83/ocrmypdf",
        f"/data/input/{pdf_file}",
        f"/data/output/{output_file}",
        "--force-ocr",
        "--image-dpi", "200", 
        "--jobs",
        "4"
    ]
 
    print(f"Procesando: {pdf_file}")
    try:
       
        subprocess.run(command, check=True)
        print(f"Archivo procesado: {output_file}")
    except subprocess.CalledProcessError as e:
        print(f"Error al procesar {pdf_file}: {e}")


max_threads = 4
with ThreadPoolExecutor(max_threads) as executor:
    executor.map(process_pdf, pdf_files)

print("Procesamiento completado.")
