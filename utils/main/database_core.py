from ..db_api.postgresql1 import *
from starlette.responses import StreamingResponse
from gzip import decompress
from uuid import UUID


def create_file1(contract_type: str, user_id: str, contract_number: str, image: bytes, content_type: str,
                 file_uuid: str):
    create_file_chunk(contract_type=contract_type, image=image, file_uuid=file_uuid)
    return create_file(contract_type=contract_type, user_id=user_id, contract_number=contract_number,
                       content_type=content_type, file_id=file_uuid)


def get_file1(file_uuid: str, path_: str):
    def iterfile():
        yield decompress(b"".join(
            [element.chunk for element in get_file(file_uuid=file_uuid, path_=path_)]))

    return StreamingResponse(iterfile(), media_type='application/pdf')


def create_user_info1(**kwargs):
    return create_user_info(**kwargs)


def get_user_info1(user_id: str):
    return get_user_info(user_id=user_id)


def get_user_id(telegram_id: str):
    return get_user_by_id(telegram_id=telegram_id)


def get_user_files1(user_id: str, contract_type: str):
    return get_file_user_id(user_id=user_id, contract_type=contract_type)


async def check_uuid(file_uuid):
    try:
        return str(UUID(file_uuid, version=4)) == file_uuid
    except ValueError:
        return False
