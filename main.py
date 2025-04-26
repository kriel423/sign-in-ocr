from fastapi import FastAPI, UploadFile, File, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import shutil, os
import uuid
from utils.ocr_parser import process_images_and_generate_excel

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

UPLOAD_DIR = "uploads"
OUTPUT_PATH = "output/weekly_hours.xlsx"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs("output", exist_ok=True)

@app.get("/", response_class=HTMLResponse)
def upload_form(request: Request):
    return templates.TemplateResponse("upload.html", {"request": request})

@app.post("/upload")
def upload_images(files: list[UploadFile] = File(...)):
    file_paths = []
    for file in files:
        file_id = str(uuid.uuid4())
        save_path = os.path.join(UPLOAD_DIR, f"{file_id}_{file.filename}")
        with open(save_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        file_paths.append(save_path)

    process_images_and_generate_excel(file_paths, OUTPUT_PATH)
    return FileResponse(path=OUTPUT_PATH, filename="weekly_hours.xlsx", media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
