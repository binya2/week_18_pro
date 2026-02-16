from fastapi import APIRouter, UploadFile

router = APIRouter(prefix="/uploadfile", tags=["upload_router"])

@router.post("/")
async def upload_file(file: UploadFile):
    # data = await data_processing(file)
    # response = await save_to_db(data)
    return {
        "filename": file.filename,
        "status": "processed",
        # "db_response": response
    }
