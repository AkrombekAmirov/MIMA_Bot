from utils.main.database_core import get_file1, check_uuid
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi import HTTPException, status
from traceback import print_stack
from fastapi import FastAPI
from re import match
import html


def sanitize_input(input_str):
    # HTML taglarini olib tashlash uchun lxml kutubxonasi yordamida
    from lxml import etree

    # XML elementini yaratamiz
    root = etree.Element("root")
    element = etree.Element("element")
    element.text = input_str
    root.append(element)

    # Elementni matnga o'zgartiramiz
    sanitized_str = etree.tostring(root, method="text", encoding="utf-8").decode("utf-8")
    blacklisted_phrases = ["<script>", "</script>", "javascript:", "onerror", "onload"]
    for phrase in blacklisted_phrases:
        sanitized_str = sanitized_str.replace(phrase, "")
    sanitized_str = html.escape(input_str)

    return sanitized_str


class XSSMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        # Requestdan kelgan ma'lumotlarni tekshirib chiqing
        for key, value in request.query_params.items():
            request.query_params[key] = sanitize_input(value)
        for key, value in request.path_params.items():
            request.path_params[key] = sanitize_input(value)
        for key, value in request.headers.items():
            request.headers[key] = sanitize_input(value)

        response = await call_next(request)

        # Response ma'lumotlarni tekshirib chiqing
        response_body = response.body.decode("utf-8")
        sanitized_response = sanitize_input(response_body)
        response.body = sanitized_response.encode("utf-8")

        return response


class ExceptionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        try:
            response = await call_next(request)
        except HTTPException as http_exc:
            # Qaytariladigan xato haqida to'liq ma'lumotlarni olish
            error_detail = {
                "status_code": http_exc.status_code,
                "detail": http_exc.detail,
            }
            return JSONResponse(content=error_detail, status_code=http_exc.status_code)
        except Exception as exc:
            # Qandaydir umumiy xato haqida ma'lumotlarni olish
            error_detail = {
                "status_code": 500,
                "detail": "Internal Server Error",
                "error_message": str("Bad request"),
            }
            return JSONResponse(content=error_detail, status_code=500)
        return response


app = FastAPI(docs_url=None, redoc_url=None)
app.debug = False


@app.get("/get_file/{file_uuid}")
async def get_File(file_uuid: str):
    path_ = None
    if file_uuid[0:3] == 'Inv':
        file_uuid = file_uuid[3:]
        path_ = 'Inv'

    if await check_uuid(file_uuid=file_uuid):
        if match(r'^[\da-f]{8}-([\da-f]{4}-){3}[\da-f]{12}$', file_uuid):
            return get_file1(file_uuid=file_uuid, path_=path_)
        else:
            print(file_uuid)
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Bad Request")
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Bad Request")


@app.exception_handler(Exception)
async def exception_handler(request, exc):
    return JSONResponse(str(exc), status_code=401)


# app.add_middleware(XSSMiddleware)
app.add_middleware(ExceptionMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["Content-Type", "Strict-Transport-Security", "X-Content-Type-Options"],
)
