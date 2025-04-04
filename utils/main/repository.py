from starlette.exceptions import HTTPException
from utils.main.database_core import create_file1, get_user_files1, create_user_info1, get_user_info1, get_user_by_id
from starlette import status
from gzip import compress
from mimetypes import guess_type

FILE_SIZE = 5242880
CHUNK_SIZE = 262144


async def file_create(contract_type, user_id, images):
    zipped_files = []
    for image in images:
        zipped_files.append((compress(image[0].read()), "application/pdf"))
        print(user_id[0])
        if len(compress(image[0].read())) > FILE_SIZE: raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="File too large")
    return {"data": [
        create_file1(contract_type=contract_type, user_id=str(user_id[0]), image=image[0],
                     contract_number=str(user_id[2]), content_type="application/pdf", file_uuid=str(user_id[1]))
        for image in zipped_files]}


async def get_file_user(user_id: str, contract_type: str):
    return get_user_files1(user_id=str(user_id), contract_type=contract_type)


async def create_user_info(**kwargs):
    return create_user_info1(**kwargs)


async def get_user_info(user_id: str):
    return get_user_info1(user_id)


async def user_id(telegram_id: str):
    return get_user_by_id(telegram_id=str(telegram_id))
