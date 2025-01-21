import os
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import FileResponse, StreamingResponse
import zipfile
import io
import uvicorn
from ocr_processor import process_pdf, input_folder, output_folder, process_existing_files

# FastAPI
app = FastAPI(
    title="PDF Processing API",
    description="API para manejar la subida, conversion y gestión de archivos PDF utilizando OCRmyPDF.",
    version="1.0.0"
)

# Endpoint para subir un archivo sin procesarlo
@app.post("/upload/", summary="Subir un archivo PDF", description="Sube un archivo PDF a la carpeta de entrada sin procesarlo.")
async def upload_file(file: UploadFile = File(...)):
    input_path = os.path.join(input_folder, file.filename)
    with open(input_path, "wb") as f:
        f.write(await file.read())
    return {"message": f"Archivo {file.filename} guardado en la carpeta de entrada."}

# Endpoint para subir un archivo ZIP y descomprimirlo en la carpeta input
@app.post("/upload-zip/", summary="Subir un archivo ZIP", description="Sube un archivo ZIP con PDFs, descomprímelo en la carpeta de entrada.")
async def upload_zip(file: UploadFile = File(...)):
    zip_path = os.path.join(input_folder, file.filename)

    # Guardar el archivo ZIP temporalmente
    with open(zip_path, "wb") as temp_zip:
        temp_zip.write(await file.read())

    # Extraer los archivos del ZIP
    try:
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(input_folder)
        saved_files = zip_ref.namelist()
    except zipfile.BadZipFile:
        os.remove(zip_path)
        return {"error": "El archivo no es un ZIP válido."}

    # Eliminar el archivo ZIP después de extraerlo
    os.remove(zip_path)
    return {"message": "Archivos extraídos exitosamente.", "saved_files": saved_files}

# Endpoint para convertir los PDFs en la carpeta input
@app.post("/convert/", summary="Convertir PDFs", description="Procesa todos los archivos PDF en la carpeta de entrada utilizando OCRmyPDF y los guarda en la carpeta de salida.")
def convert_files():
    process_existing_files()
    return {"message": "Archivos en la carpeta de entrada procesados exitosamente."}

# Endpoint para descargar un archivo de la carpeta output
@app.get("/download/{filename}", summary="Descargar archivo", description="Descarga un archivo PDF procesado desde la carpeta de salida.")
def download_file(filename: str):
    file_path = os.path.join(output_folder, filename)
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="application/pdf", filename=filename)
    else:
        return {"error": "Archivo no encontrado."}

# Endpoint para descargar todos los archivos de la carpeta output como un archivo ZIP
@app.get("/download-all/", summary="Descargar todos los archivos", description="Descarga todos los archivos procesados en la carpeta de salida como un archivo ZIP.")
def download_all_files():
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zip_file:
        for filename in os.listdir(output_folder):
            file_path = os.path.join(output_folder, filename)
            if os.path.isfile(file_path):
                zip_file.write(file_path, arcname=filename)
    zip_buffer.seek(0)
    return StreamingResponse(zip_buffer, media_type="application/zip", headers={"Content-Disposition": "attachment; filename=output_files.zip"})

# Endpoint para eliminar todos los archivos de la carpeta input
@app.delete("/delete-input/", summary="Eliminar archivos de entrada", description="Elimina todos los archivos en la carpeta de entrada.")
def delete_input_files():
    files_deleted = []
    for file in os.listdir(input_folder):
        file_path = os.path.join(input_folder, file)
        if os.path.isfile(file_path):
            os.remove(file_path)
            files_deleted.append(file)
    return {"message": "Archivos eliminados de la carpeta de entrada.", "deleted_files": files_deleted}

# Endpoint para eliminar todos los archivos de la carpeta output
@app.delete("/delete-output/", summary="Eliminar archivos de salida", description="Elimina todos los archivos en la carpeta de salida.")
def delete_output_files():
    files_deleted = []
    for file in os.listdir(output_folder):
        file_path = os.path.join(output_folder, file)
        if os.path.isfile(file_path):
            os.remove(file_path)
            files_deleted.append(file)
    return {"message": "Archivos eliminados de la carpeta de salida.", "deleted_files": files_deleted}

# Endpoint para eliminar todos los archivos de ambas carpetas
@app.delete("/delete-all/", summary="Eliminar todos los archivos", description="Elimina todos los archivos en las carpetas de entrada y salida.")
def delete_all_files():
    input_deleted = []
    output_deleted = []

    for file in os.listdir(input_folder):
        file_path = os.path.join(input_folder, file)
        if os.path.isfile(file_path):
            os.remove(file_path)
            input_deleted.append(file)

    for file in os.listdir(output_folder):
        file_path = os.path.join(output_folder, file)
        if os.path.isfile(file_path):
            os.remove(file_path)
            output_deleted.append(file)

    return {
        "message": "Archivos eliminados de ambas carpetas.",
        "deleted_input_files": input_deleted,
        "deleted_output_files": output_deleted
    }

# Endpoint para listar documentos en la carpeta output
@app.get("/documents-output/", summary="Listar archivos de salida", description="Lista todos los archivos en la carpeta de salida.")
def list_output_files():
    files = os.listdir(output_folder)
    return {"output_files": files}

# Endpoint para listar documentos en la carpeta input
@app.get("/documents-input/", summary="Listar archivos de entrada", description="Lista todos los archivos en la carpeta de entrada.")
def list_input_files():
    files = os.listdir(input_folder)
    return {"input_files": files}

# Inicia el servidor FastAPI
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8032)
