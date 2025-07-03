import io

from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse, StreamingResponse
from PIL import Image, ImageDraw
from ultralytics import YOLO

app = FastAPI()

# Load model
model = YOLO("yolov8n.pt")


@app.get("/")
def home():
    return HTMLResponse(
        content="""
    <html>
        <head>
            <title>Image Classification</title>
            <style>
                body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
                form { margin: 20px 0; }
                img { max-width: 100%; margin-top: 20px; }
                .button-container { display: flex; gap: 10px; margin: 20px 0; }
                button { padding: 10px 20px; cursor: pointer; }
                #result { margin-top: 20px; }
            </style>
        </head>
        <body>
            <h1>Image Classification</h1>
            <div class="button-container">
                <form action="/predict-default" method="get">
                    <button type="submit">Predict Default Image</button>
                </form>
                <form action="/predict" method="post" enctype="multipart/form-data">
                    <input type="file" name="file" accept="image/*">
                    <button type="submit">Predict Uploaded Image</button>
                </form>
            </div>
            <div id="result"></div>
        </body>
    </html>
    """
    )


@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    # Read image
    contents = await file.read()
    image = Image.open(io.BytesIO(contents))

    # Run inference
    results = model(image)
    draw = ImageDraw.Draw(image)

    # Process results list
    for box in results[0].boxes:
        bbox = box.xyxy[0].tolist()
        draw.rectangle(bbox, outline="red", width=3)

    # Convert image to bytes
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format="PNG")
    img_byte_arr.seek(0)

    return StreamingResponse(img_byte_arr, media_type="image/png")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
