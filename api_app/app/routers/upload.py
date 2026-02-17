from fastapi import APIRouter, UploadFile, status

from api_app.app.service.upload_service import UploadService

router = APIRouter(prefix="/uploadfile", tags=["upload_router"])


@router.post("/", status_code=status.HTTP_201_CREATED)
async def upload_file(file: UploadFile):
    orders_list = await UploadService.process_json_upload_file(file)
    await UploadService.save_json_to_mongo(orders_list)
    await UploadService.push_orders_to_kafka(orders_list)
    return {
        "status": "success",
        "message": "File processed, saved to DB, and queued in Kafka",
        "items_processed": len(orders_list)
    }