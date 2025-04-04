# from starlette.responses import StreamingResponse
# from gzip import decompress
# from fastapi import FastAPI
#
# app = FastAPI()
# def get_file1(file_uuid: str):
#     def iterfile():
#         yield decompress(b"".join(
#             [element.chunk for element in get_file(file_uuid=file_uuid)]))
#
#     return StreamingResponse(iterfile(), media_type=get_file_(file_uuid=file_uuid).content_type)
#
# @app.get("/get_file/{file_uuid}")
# async def get_File(file_uuid: str):
#     return "get_file1(file_uuid=file_uuid)"
#
