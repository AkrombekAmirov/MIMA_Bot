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