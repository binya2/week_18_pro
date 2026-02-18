from fastapi import APIRouter, UploadFile, status

from api_app.app.service.upload_service import UploadService
from shared import PizzaOrders

router = APIRouter(prefix="/uploadfile", tags=["upload_router"])


@router.post("/", status_code=status.HTTP_201_CREATED)
async def upload_file(file: UploadFile):
    data_config = await UploadService.process_and_save(file)
    return data_config
