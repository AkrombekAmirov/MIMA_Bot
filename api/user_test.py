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
        response = [
            UserPassportResponse(
                id=user.id,
                name=user.name,
                faculty=user.faculty,
                telegram_id=user.telegram_id,
                passport=user.passport
            )
            for user in users
        ]

        return response
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

    results = await db.get(Result, filters={"user_id": str(user_id), "subject_id": subject_id, "status": False})
    if not results:
        raise HTTPException(status_code=404, detail="Foydalanuvchiga tegishli test topilmadi")

    result = results[0]
    result.status = True
    await db.update(result)

    total = len(loads(result.question_ids))
    correct = result.correct_answers
    accuracy = correct / total * 100 if total > 0 else 0

    # ✅ test_point ni keyingisiga oshiramiz
    user = (await db.get(User, filters={"id": user_id}))[0]
    current_tp = int(user.test_point or "1")
    new_tp = str(current_tp + 1)
    await db.update_by_field(User, "id", user.id, {"test_point": new_tp})

    return {
        "message": "Blok yakunlandi",
        "total_questions": total,
        "correct_answers": correct,
        "accuracy": round(accuracy, 2),
        "status": correct >= (total * 0.5)
    }


@router.get("/final-summary/{user_id}")
async def get_final_summary(user_id: int, db: DatabaseService1 = Depends(get_db_core)):
    user = await db.get(User, filters={"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="Foydalanuvchi topilmadi")

    user = user[0]
    results = await db.get(Result, filters={"user_id": str(user_id)})
    if not results:
        raise HTTPException(status_code=404, detail="Natijalar topilmadi")

    faculties = await db.get(Faculty, filters={"name": user.faculty})
    if not faculties:
        raise HTTPException(status_code=404, detail="Fakultet topilmadi")

    faculty = faculties[0]
    blocks = await db.get(FacultyBlock, filters={"faculty_val": faculty.faculty_val})

    block_map = {b.subject_val: b.block_number for b in blocks}
    block_results = {1: {"correct": 0, "total": 0}, 2: {"correct": 0, "total": 0}, 3: {"correct": 0, "total": 0}}

    for res in results:
        subject_id = res.subject_id
        block_number = block_map.get(int(subject_id))
        if not block_number:
            continue

        correct = res.correct_answers
        total = len(loads(res.question_ids))

        block_results[block_number]["correct"] += correct
        block_results[block_number]["total"] += total

    return {
        "block1": block_results[1],
        "block2": block_results[2],
        "block3": block_results[3],
        "total_correct": sum(b["correct"] for b in block_results.values()),
        "total_questions": sum(b["total"] for b in block_results.values())
    }
