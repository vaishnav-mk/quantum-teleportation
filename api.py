from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
import quantum_teleportation.quantum_data_teleporter as qc
import os

app = FastAPI()


@app.post("/teleport")
async def quantum_teleport(
    text_to_send: str = Form(None),
    file: UploadFile = File(None),
    image: UploadFile = File(None),
    shots: int = Form(1),
    noise_model: bool = Form(False),
    compression: str = Form("adaptive"),
    logs: bool = Form(True),
):
    """
    Endpoint to teleport data. You can send text, file, or image.

    Args:
        text_to_send (str, optional): Text to be sent. Defaults to None.
        file (UploadFile, optional): A text file to be uploaded. Defaults to None.
        image (UploadFile, optional): An image file to be uploaded. Defaults to None.
        shots (int): Number of shots for the quantum simulation. Defaults to 1.
        noise_model (bool): Whether to use the noise model. Defaults to False.
        compression (str): Compression method ('adaptive', 'brotli', False). Defaults to 'adaptive'.
        logs (bool): Enable or disable logging. Defaults to True.

    Returns:
        JSONResponse: Sent and received data with a success flag.
    """

    if not text_to_send and not file and not image:
        raise HTTPException(status_code=400, detail="At least one of text, file, or image must be provided.")

    file_path, image_path = None, None

    if file:
        file_path = f"temp/{file.filename}"
        with open(file_path, "wb") as buffer:
            buffer.write(await file.read())

    if image:
        image_path = f"temp/{image.filename}"
        with open(image_path, "wb") as buffer:
            buffer.write(await image.read())

    quantum_comm = qc.QuantumDataTeleporter(
        file_path=file_path,
        image_path=image_path,
        text_to_send=text_to_send,
        shots=shots,
        noise_model=noise_model,
        logs=logs,
        compression=compression,
        output_path="output",
    )

    received_data, is_data_match, metadata = quantum_comm.run_simulation()

    if file_path and os.path.exists(file_path):
        os.remove(file_path)
    if image_path and os.path.exists(image_path):
        os.remove(image_path)

    return JSONResponse(
        content={
            "sent_data": text_to_send or "File/Image sent",
            "received_data": received_data,
            "is_data_match": is_data_match,
            "metadata": metadata
        }
    )


@app.get("/")
async def root():
    return {"message": "Quantum Data Teleportation API is up and running!"}
