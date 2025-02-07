from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import cv2
import numpy as np

from img import process_images
from db import CompetitionDatabase

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (for development)
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

UPLOAD_DIR = Path("../unprocessed_images")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

db = CompetitionDatabase()


@app.post("/upload")
async def upload_images(images: list[UploadFile] = File(...)):
    saved_files = []
    for file in images:
        try:
            # Read image into a NumPy array
            image_bytes = await file.read()
            image_array = np.frombuffer(image_bytes, dtype=np.uint8)
            image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

            if image is None:
                raise ValueError("Invalid image file")

            # Save as JPG
            save_path = UPLOAD_DIR / f"{Path(file.filename).stem}.jpg"
            cv2.imwrite(str(save_path), image)
            saved_files.append(str(save_path))
        except Exception as e:
            raise HTTPException(
                status_code=400, detail=f"Error processing {file.filename}: {e}"
            )

    process_images()

    return {"message": "Sucessfully processed images.", "files": saved_files}


@app.get("/next")
async def get_result():
    result = db.fetch_next_scanned_result()

    if result is None:
        return {"message": "No more results available."}
    return result


@app.get("/all")
async def get_all():
    results = db.get_all()
    if results is None:
        raise HTTPException(
            status_code=500, detail="Failed to fetch results from the database"
        )

    return results
