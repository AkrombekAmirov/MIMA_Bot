from utils import DatabaseService1, get_db_core, User, Faculty, FacultyBlock, Subject, Question, Result, UserAnswer
from fastapi import APIRouter, Depends, HTTPException, status
from .Basemodels import UserPassportResponse
from LoggingService import LoggerService
from typing import List, Dict, Any
from datetime import datetime, timedelta
from random import sample
from pytz import timezone
from json import dumps, loads

db = DatabaseService1(logger=LoggerService())

router = APIRouter(
    prefix="/api",
    tags=["Abituryent"],
    dependencies=[Depends(get_db_core)],
    responses={404: {"description": "Not found"}},
)


@router.get("/check-passport/", response_model=List[UserPassportResponse])
async def check_passport(passport: str, db: DatabaseService1 = Depends(get_db_core)):
    try:
        users = await db.get(User, filters={"passport": passport})

        if not users:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Foydalanuvchi topilmadi. Iltimos, passport ma'lumotlarini tekshirib qayta urinib ko'ring."
            )
        await db.update_by_field(User, "id", users[0].id, {"test_point": "1"})

        return [
            UserPassportResponse(
                id=user.id,
                name=user.name,
                faculty=user.faculty,
                telegram_id=user.telegram_id,
                passport=user.passport,
                status=user.status  # ✅ test topshirganmi — frontend tekshiradi
            )
            for user in users
        ]
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/start-test/{user_id}", response_model=Dict[str, Any])
async def start_test(user_id: int, db: DatabaseService1 = Depends(get_db_core)):
    """
    Testni boshlash sahifasi: foydalanuvchi ma'lumotlari, fakultet va 3 blok fanlari ro'yxatini qaytaradi.
    """
    # 1. Foydalanuvchini olish
    users = await db.get(User, filters={"id": user_id})
    if not users:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Foydalanuvchi topilmadi")
    user = users[0]

    # 2. Fakultet aniqlash
    faculties = await db.get(Faculty, filters={"name": user.faculty})
    if not faculties:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Fakultet topilmadi")
    faculty = faculties[0]

    # 3. Blok bo'yicha fanlar
    blocks = await db.get(FacultyBlock, filters={"faculty_id": faculty.faculty_val})
    if not blocks or len(blocks) < 1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Fakultet uchun bloklar topilmadi")

    # 4. Fan nomlarini bir martada olish
    # block.subject_val maydoniga bog‘langan bo‘lsa:
    subjects = []
    for block in sorted(blocks, key=lambda b: b.block_number):
        subs = await db.get(Subject, filters={"subject_val": block.subject_val})
        if not subs:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"{block.block_number}-blok uchun subject topilmadi")
        subject = subs[0]
        subjects.append({
            "block_number": block.block_number,
            "subject_name": subject.name
        })

    # 5. Javobni tuzish
    return {
        "welcome_message": f"Xush kelibsiz, {user.name}!",
        "faculty": faculty.name,
        "subjects": subjects
    }


@router.get("/start-real-test/{user_id}")
async def start_real_test(user_id: int, db: DatabaseService1 = Depends(get_db_core)):
    users = await db.get(User, filters={"id": user_id})
    if not users:
        raise HTTPException(status_code=404, detail="Foydalanuvchi topilmadi")
    user = users[0]

    # test_point dan qaysi blokni boshlash kerakligini aniqlaymiz
    try:
        current_point = int(user.test_point or "1")  # default = 1-blok
    except ValueError:
        current_point = 1

    faculties = await db.get(Faculty, filters={"name": user.faculty})
    if not faculties:
        raise HTTPException(status_code=404, detail="Fakultet topilmadi")
    faculty = faculties[0]

    blocks = await db.get(FacultyBlock, filters={"faculty_val": faculty.faculty_val})
    if not blocks:
        raise HTTPException(status_code=400, detail="Fakultet bloklari topilmadi")

    subjects = []
    for block in sorted(blocks, key=lambda b: b.block_number):
        subs = await db.get(Subject, filters={"subject_val": block.subject_val})
        if not subs:
            continue
        subject = subs[0]
        subjects.append({
            "block_number": block.block_number,
            "subject_name": subject.name,
            "subject_id": int(subject.subject_val)
        })

    now = datetime.now(timezone("Asia/Tashkent"))

    for subject in subjects:
        if subject["block_number"] != current_point:
            continue  # faqat kerakli blokni ishlaymiz

        existing_result = await db.get(Result, filters={
            "user_id": str(user_id),
            "subject_id": subject["subject_id"]
        })

        for res in existing_result:
            if res.status is False:
                question_ids = loads(res.question_ids)
                user_answers = loads(res.user_answers) if res.user_answers else []
                answered = len(user_answers)

                all_questions = await db.get(Question)
                selected_questions = [q for q in all_questions if q.id in question_ids][answered:]

                return {
                    "block_number": subject["block_number"],
                    "subject_name": subject["subject_name"],
                    "subject_id": subject["subject_id"],
                    "total_blocks": len(subjects),
                    "questions": [
                        {
                            "id": q.id,
                            "text": q.text,
                            "options": [q.option1, q.option2, q.option3, q.option4]
                        } for q in selected_questions
                    ]
                }

        # blok hali boshlanmagan bo‘lsa — yaratamiz
        if not existing_result:
            selected_questions = await db.get(Question, filters={"subject_id": subject["subject_id"]})
            if not selected_questions:
                continue

            count = 30 if subject["block_number"] == 1 else 10
            selected_questions = sample(selected_questions, min(count, len(selected_questions)))

            await db.add(Result(
                user_id=str(user_id),
                subject_id=subject["subject_id"],
                question_ids=dumps([q.id for q in selected_questions]),
                user_answers=dumps([]),
                start_time=now,
                end_time=now + timedelta(hours=1) if subject["block_number"] == 1 else None,
                status=False
            ))

            return {
                "block_number": subject["block_number"],
                "subject_name": subject["subject_name"],
                "subject_id": subject["subject_id"],
                "total_blocks": len(subjects),
                "questions": [
                    {
                        "id": q.id,
                        "text": q.text,
                        "options": [q.option1, q.option2, q.option3, q.option4]
                    } for q in selected_questions
                ]
            }

    raise HTTPException(status_code=204, detail="Barcha bloklar yakunlangan.")


@router.post("/submit-answer")
async def submit_answer(data: Dict[str, Any], db: DatabaseService1 = Depends(get_db_core)):
    user_id = str(data["user_id"])
    question_id = data["question_id"]
    selected_option = data["selected_option"]

    # Savol va to'g'ri javobni olish
    questions = await db.get(Question, filters={"id": question_id})
    if not questions:
        raise HTTPException(status_code=404, detail="Savol topilmadi")
    question = questions[0]
    is_correct = (selected_option == question.correct_answer)

    # UserAnswer modelda mavjud javobni tekshirish
    existing_answer = await db.get(UserAnswer, filters={
        "user_id": user_id,
        "question_id": question_id
    })

    if existing_answer:
        # Update
        await db.update_by_field(UserAnswer, "id", existing_answer[0].id, {
            "selected_option": selected_option,
            "is_correct": is_correct
        })
    else:
        # Create
        await db.add(UserAnswer(
            user_id=user_id,
            subject_id=question.subject_id,
            question_id=question_id,
            selected_option=selected_option,
            is_correct=is_correct
        ))

    # Result jadvalidagi mavjud yozuvni yangilash
    results = await db.get(Result, filters={"user_id": user_id, "subject_id": question.subject_id, "status": False})
    if not results:
        raise HTTPException(status_code=404, detail="Result topilmadi")

    result = results[0]
    question_ids = loads(result.question_ids)
    user_answers = loads(result.user_answers) if result.user_answers else []

    # Savol indexini aniqlab yangilash
    try:
        index = question_ids.index(question_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Savol resultda mavjud emas")

    # Eski javobni tahlil qilish (agar bor bo‘lsa)
    previous_answer = user_answers[index] if index < len(user_answers) else None
    if index < len(user_answers):
        user_answers[index] = selected_option
    else:
        user_answers.append(selected_option)

    # To‘g‘ri va noto‘g‘ri sonini yangilash
    correct = result.correct_answers
    wrong = result.wrong_answers

    if previous_answer:
        if previous_answer == question.correct_answer:
            correct -= 1
        else:
            wrong -= 1

    if is_correct:
        correct += 1
    else:
        wrong += 1

    await db.update_by_field(Result, "id", result.id, {
        "user_answers": dumps(user_answers),
        "correct_answers": correct,
        "wrong_answers": wrong
    })

    return {"message": "Javob yangilandi", "correct": is_correct}


@router.post("/finish-block")
async def finish_block(payload: dict, db: DatabaseService1 = Depends(get_db_core)):
    user_id = payload.get("user_id")
    subject_id = payload.get("subject_id")
    spent_time = payload.get("spent_time")  # daqiqalarda

    results = await db.get(Result, filters={"user_id": str(user_id), "subject_id": subject_id, "status": False})
    if not results:
        raise HTTPException(status_code=404, detail="Foydalanuvchiga tegishli test topilmadi")

    result = results[0]
    result.status = True
    result.updated_date = datetime.now(timezone("Asia/Tashkent")).strftime("%Y-%m-%d")
    result.updated_time = datetime.now(timezone("Asia/Tashkent")).strftime("%H:%M:%S")

    if spent_time:
        result.number = spent_time  # daqiqalarda ishlagan vaqt (shu maydonni ishlatyapmiz)

    await db.update(result)

    total = len(loads(result.question_ids))
    correct = result.correct_answers
    accuracy = correct / total * 100 if total > 0 else 0

    user = (await db.get(User, filters={"id": user_id}))[0]
    current_tp = int(user.test_point or "1")
    await db.update_by_field(User, "id", user.id, {"test_point": str(current_tp + 1)})

    return {
        "message": "Blok yakunlandi",
        "total_questions": total,
        "correct_answers": correct,
        "accuracy": round(accuracy, 2),
        "status": correct >= (total * 0.5)
    }


@router.get("/final-summary")
async def get_final_summary(user_id: int, db: DatabaseService1 = Depends(get_db_core)):
    # 1. Foydalanuvchini tekshiramiz
    users = await db.get(User, filters={"id": user_id})
    if not users:
        raise HTTPException(status_code=404, detail="Foydalanuvchi topilmadi")
    await db.update_by_field(User, "id", user_id, {"status": True})
    user = users[0]

    # 2. Fakultet va bloklar
    faculties = await db.get(Faculty, filters={"name": user.faculty})
    if not faculties:
        raise HTTPException(status_code=404, detail="Fakultet topilmadi")
    faculty = faculties[0]

    blocks = await db.get(FacultyBlock, filters={"faculty_val": faculty.faculty_val})
    block_map = {int(b.subject_val): b.block_number for b in blocks}

    # 3. Subject nomlari
    subjects = await db.get(Subject)
    subject_map = {int(s.subject_val): s.name for s in subjects}

    # 4. Resultlarni yig‘ish
    results = await db.get(Result, filters={"user_id": str(user_id)})
    if not results:
        raise HTTPException(status_code=404, detail="Natijalar topilmadi")

    # 5. Bloklar bo‘yicha statistikani tayyorlaymiz
    block_results = {
        1: {
            "block_number": 1,
            "subject_name": None,
            "correct_answers": 0,
            "wrong_answers": 0,
            "total_questions": 30,
            "score": 0,
            "max_score": 60
        },
        2: {
            "block_number": 2,
            "subject_name": None,
            "correct_answers": 0,
            "wrong_answers": 0,
            "total_questions": 10,
            "score": 0,
            "max_score": 20
        },
        3: {
            "block_number": 3,
            "subject_name": None,
            "correct_answers": 0,
            "wrong_answers": 0,
            "total_questions": 10,
            "score": 0,
            "max_score": 20
        }
    }

    for res in results:
        sid = res.subject_id
        block_number = block_map.get(sid)
        if block_number not in block_results:
            continue

        correct = res.correct_answers
        wrong = res.wrong_answers
        subject_name = subject_map.get(sid, "Noma'lum fan")

        block = block_results[block_number]
        block["correct_answers"] += correct
        block["wrong_answers"] += wrong
        block["subject_name"] = subject_name
        block["score"] = round((correct / block["total_questions"]) * block["max_score"], 2)

    total_score = sum(b["score"] for b in block_results.values())

    return {
        "blocks": [block_results[1], block_results[2], block_results[3]],
        "total_score": total_score
    }
