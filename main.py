from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from api import router

app = FastAPI()

app.include_router(router=router)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/")
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/start-test/{user_id}")
async def read_test_page(request: Request, user_id: int):
    return templates.TemplateResponse("start_test.html", {
        "request": request,
        "user_id": user_id
    })


@app.get("/start-real-test/{user_id}")
async def read_test_page(request: Request, user_id: int):
    return templates.TemplateResponse("answer_test.html", {
        "request": request,
        "user_id": user_id
    })

@app.post("/answer-test/{user_id}")
async def read_test_page(request: Request, user_id: int):
    return templates.TemplateResponse("answer_test.html", {
        "request": request,
        "user_id": user_id
    })

@app.post("/finish-block/{user_id}")
async def finish_test(request: Request, user_id:int):
    return templates.TemplateResponse("finish_test.html", {
        "request": request,
        "user_id": user_id
    })

@app.get("/final-summary")
async def read_test_page(request: Request, user_id: int):
    return templates.TemplateResponse("summary.html", {
        "request": request,
        "user_id": user_id
    })


'''
# main.py
import uvicorn
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.gzip import GZipMiddleware
from settings import settings
from api import router as api_router

app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG,
    version="1.0.0",
)

# 1) CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2) HTTPS ga yo'naltirish (agar productionda HTTPS orqasida bo'lsa)
app.add_middleware(HTTPSRedirectMiddleware)

# 3) Trusted Host (CEO Injection oldini oladi)
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "127.0.0.1", "*.yourdomain.com"],
)

# 4) GZip kompressiya (bandwidthni tejash uchun)
app.add_middleware(GZipMiddleware, minimum_size=1000)

# 5) Sessiya cookie (secure, httpOnly, sameSite)
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SESSION_SECRET,
    session_cookie="mima_session",
    https_only=not settings.DEBUG,
    max_age=14 * 24 * 3600,  # 2 haftaga sessiya muddat
)

# Routerni qo'shish
app.include_router(api_router, prefix="/api")

# Statik fayllar va templatelar
app.mount("/static", StaticFiles(directory=settings.STATIC_DIR), name="static")
templates = Jinja2Templates(directory=settings.TEMPLATES_DIR)

# Sahifalarni taqdim etish
@app.get("/", include_in_schema=False)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/start-test/{user_id}", include_in_schema=False)
async def start_test_page(request: Request, user_id: int):
    return templates.TemplateResponse("start_test.html", {"request": request, "user_id": user_id})

@app.get("/start-real-test/{user_id}", include_in_schema=False)
async def answer_test_page(request: Request, user_id: int):
    return templates.TemplateResponse("answer_test.html", {"request": request, "user_id": user_id})

@app.post("/finish-block", include_in_schema=False)
async def finish_block_page(request: Request):
    data = await request.json()
    return templates.TemplateResponse("finish_test.html", {"request": request, **data})

@app.get("/final-summary", include_in_schema=False)
async def summary_page(request: Request, user_id: int):
    return templates.TemplateResponse("summary.html", {"request": request, "user_id": user_id})

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8002,
        reload=settings.DEBUG,
        log_level="debug" if settings.DEBUG else "info",
    )

'''