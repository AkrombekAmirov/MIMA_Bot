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


@app.get("/courses")
async def read_courses_page(request: Request):
    return templates.TemplateResponse("courses.html", {"request": request})


@app.get("/groups")
async def read_groups_page(request: Request):
    return templates.TemplateResponse("groups.html", {"request": request})


@app.get("/teachers")
async def read_teachers_page(request: Request):
    return templates.TemplateResponse("teachers.html", {"request": request})

@app.get("/subjects")
async def read_subjects_page(request: Request):
    return templates.TemplateResponse("subjects.html", {"request": request})

@app.get("/rooms")
async def read_rooms_page(request: Request):
    return templates.TemplateResponse("rooms.html", {"request": request})

@app.get("/timetable")
async def read_timetable_page(request: Request):
    return templates.TemplateResponse("tajriba1.html", {"request": request})
# Add similar CRUD operations for Group, Teacher, Room, ClassSchedule, Week, and Timetable

@app.get("/teachers_timetable")
async def read_teachers_timetable_page(request: Request):
    return templates.TemplateResponse("teachersA.html", {"request": request})