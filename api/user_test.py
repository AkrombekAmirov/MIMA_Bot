from utils import DatabaseService1, get_db_core, User, Faculty, FacultyBlock, Subject, Question, Result, UserAnswer
from fastapi import APIRouter, Depends, HTTPException, status
from datetime import datetime, timezone as dt_timezone
from .Basemodels import UserPassportResponse
from random import sample, shuffle, randint
from LoggingService import LoggerService
from pydantic import BaseModel, Field
from typing import List, Dict, Any
from pytz import timezone, utc
from json import dumps, loads

db = DatabaseService1(logger=LoggerService())
logger = LoggerService().get_logger()
router = APIRouter(
    prefix="/api",
    tags=["Abituryent"],
    dependencies=[Depends(get_db_core)],
    responses={404: {"description": "Not found"}},
)
tz = timezone("Asia/Tashkent")


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
    Testni boshlash sahifasi:
    foydalanuvchi ma'lumotlari, fakultet va 3 blok fanlari ro'yxatini qaytaradi.
    Til bo‘yicha ham filtrlaymiz.
    """
    # 1) Foydalanuvchini olish
    users = await db.get(User, filters={"id": user_id})
    if not users:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Foydalanuvchi topilmadi")
    user = users[0]

    # 2) Fakultet aniqlash
    faculties = await db.get(Faculty, filters={"name": user.faculty, "talim_tili": user.talim_tili})
    print(faculties)
    if not faculties:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Fakultet topilmadi")
    faculty = faculties[0]

    # 3) Blok bo‘yicha FacultyBlocklarni olish
    blocks = await db.get(FacultyBlock, filters={"faculty_val": faculty.faculty_val})
    print(blocks)
    if not blocks:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Fakultet uchun bloklar topilmadi")

    # 4) Har bir blok uchun tilga mos Subjectni olib kelish
    subjects = []
    chosen_lang = user.talim_tili  # masalan "O'zbek" yoki "Rus"
    for block in sorted(blocks, key=lambda b: b.block_number):
        subs = await db.get(
            Subject,
            filters={
                "subject_val": block.subject_val
            }
        )
        print(subs)
        if not subs:
            # Tilga mos fan topilmasa, xatolik qaytaramiz
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"{block.block_number}-blok uchun '{chosen_lang}' tilida fan topilmadi"
            )
        subject = subs[0]
        subjects.append({
            "block_number": block.block_number,
            "subject_name": subject.name
        })

    # 5) Javobni tuzish (return o‘zgarmaydi)
    return {
        "welcome_message": f"Xush kelibsiz, {user.name}!",
        "faculty": faculty.name,
        "subjects": subjects
    }


@router.get("/start-real-test/{user_id}", response_model=Dict[str, Any])
async def start_real_test(user_id: int, db: DatabaseService1 = Depends(get_db_core)):
    try:
        # 1. Foydalanuvchini tekshirish
        users = await db.get(User, filters={"id": user_id})
        if not users:
            raise HTTPException(status_code=404, detail="Foydalanuvchi topilmadi")
        user = users[0]

        try:
            current_block = int(user.test_point or "1")
        except ValueError:
            current_block = 1

        # 2. Fakultet va fanlarni aniqlash
        faculties = await db.get(Faculty, filters={"name": user.faculty, "talim_tili": user.talim_tili})
        if not faculties:
            raise HTTPException(status_code=404, detail="Fakultet topilmadi")
        faculty = faculties[0]

        blocks = await db.get(FacultyBlock, filters={"faculty_val": faculty.faculty_val})
        if not blocks:
            raise HTTPException(status_code=400, detail="Fakultet bloklari topilmadi")

        # 3. Fanlar (blok bo‘yicha)
        subjects = []
        for blk in sorted(blocks, key=lambda b: b.block_number):
            subs = await db.get(Subject, filters={"subject_val": blk.subject_val})
            if subs:
                s = subs[0]
                subjects.append({
                    "block_number": blk.block_number,
                    "subject_name": s.name,
                    "subject_id": int(s.subject_val)
                })

        subj = next((s for s in subjects if s["block_number"] == current_block), None)
        if not subj:
            raise HTTPException(status_code=400, detail="Blok topilmadi")

        subject_id = subj["subject_id"]

        # 4. Tiklash rejimi (yakunlanmagan natija mavjudmi?)
        existing: List[Result] = await db.get(Result, filters={"user_id": str(user_id), "subject_id": subject_id,
                                                               "status": False})
        if existing:
            result = existing[0]
            q_ids = result.get_question_ids()

            answers = await db.get(UserAnswer, filters={"user_id": str(user_id), "subject_id": subject_id})
            answer_map = {a.question_id: a.selected_option for a in answers}

            questions = await db.get(Question, filters={"subject_id": subject_id})
            question_map = {q.id: q for q in questions}

            payload_qs = []
            for qid in q_ids:
                q = question_map.get(qid)
                if not q:
                    logger.warning(f"Savol mavjud emas: ID={qid}")
                    continue
                opts = [q.option1, q.option2, q.option3, q.option4]
                shuffle(opts)
                payload_qs.append({
                    "id": q.id,
                    "text": q.text,
                    "formula": q.formula or "",
                    "options": opts,
                    "selected_option": answer_map.get(q.id, "")
                })

            start_dt = datetime.combine(result.created_date, result.created_time)
            start_aware = tz.localize(start_dt).astimezone(dt_timezone.utc)

            return {
                "block_number": subj["block_number"],
                "subject_name": subj["subject_name"],
                "subject_id": subj["subject_id"],
                "total_blocks": len(subjects),
                "start_time": start_aware.isoformat(),
                "questions": payload_qs
            }

        # 5. Yangi test boshlash
        all_questions = await db.get(Question, filters={"subject_id": subject_id})
        if not all_questions:
            raise HTTPException(status_code=400, detail="Fan uchun savollar mavjud emas")

        count_map = {1: 20, 2: 15, 3: 10}
        count = count_map.get(subj["block_number"], 10)
        chosen = sample(all_questions, min(count, len(all_questions)))

        payload_qs = []
        for q in chosen:
            opts = [q.option1, q.option2, q.option3, q.option4]
            shuffle(opts)
            payload_qs.append({
                "id": q.id,
                "text": q.text,
                "formula": q.formula or "",
                "options": opts,
                "selected_option": ""
            })

        now = datetime.now(tz)
        new_result = Result(
            user_id=str(user_id),
            subject_id=subject_id,
            question_ids=dumps([q.id for q in chosen]),
            user_answers=dumps([]),
            status=False,
            created_date=now.date(),
            created_time=now.time(),
            block_number=subj["block_number"]
        )
        await db.add(new_result)

        return {
            "block_number": subj["block_number"],
            "subject_name": subj["subject_name"],
            "subject_id": subj["subject_id"],
            "total_blocks": len(subjects),
            "start_time": now.astimezone(dt_timezone.utc).isoformat(),
            "questions": payload_qs
        }

    except Exception as e:
        logger.exception(f"Start-real-test xatolik: {e}")
        raise HTTPException(status_code=500, detail="Ichki tizim xatosi")


# ✅ YANGILANGAN submit-answer API (xato va to'g'ri javoblar aniqlik bilan hisoblanadi)
@router.post("/submit-answer")
async def submit_answer(data: Dict[str, Any], db: DatabaseService1 = Depends(get_db_core)):
    user_id = str(data["user_id"])
    question_id = data["question_id"]
    selected_option = data["selected_option"]

    # 1. Savolni topamiz
    questions = await db.get(Question, filters={"id": question_id})
    if not questions:
        raise HTTPException(status_code=404, detail="Savol topilmadi")
    question = questions[0]
    correct_answer = question.correct_answer
    is_correct = selected_option == correct_answer

    # 2. Result topiladi
    results = await db.get(Result, filters={
        "user_id": user_id,
        "subject_id": question.subject_id,
        "status": False
    })
    if not results:
        raise HTTPException(status_code=404, detail="Aktiv test topilmadi")
    result = results[0]

    question_ids = result.get_question_ids()
    user_answers = result.get_user_answers()

    # 3. Javobni qo‘shish yoki yangilash (sinxron uzunlikni kafolatlaymiz)
    try:
        index = question_ids.index(question_id)
    except ValueError:
        index = -1

    if index == -1:
        question_ids.append(question_id)
        user_answers.append(selected_option)
    else:
        # ⚠️ user_answers ro‘yxati indexni qo‘llab-quvvatlashiga ishonch hosil qilamiz
        while len(user_answers) < len(question_ids):
            user_answers.append("")  # noto‘liq ro‘yxatni to‘ldiramiz
        user_answers[index] = selected_option

    # 4. Yangilanganlarni saqlaymiz
    result.set_question_ids(question_ids)
    result.set_user_answers(user_answers)

    # 5. To‘g‘ri va noto‘g‘ri javoblarni hisoblaymiz
    correct_questions = await db.get(Question, filters={"subject_id": question.subject_id})
    correct_map = {q.id: q.correct_answer for q in correct_questions}
    result.recalculate_scores(correct_map)

    # 6. Saqlash
    await db.update(result)

    # 7. UserAnswer modelini saqlash yoki yangilash
    existing = await db.get(UserAnswer, filters={"user_id": user_id, "question_id": question_id})
    if existing:
        await db.update_by_field(UserAnswer, "id", existing[0].id, {
            "selected_option": selected_option,
            "is_correct": is_correct
        })
    else:
        await db.add(UserAnswer(
            user_id=user_id,
            subject_id=question.subject_id,
            question_id=question_id,
            selected_option=selected_option,
            is_correct=is_correct
        ))

    return {
        "message": "✅ Javob saqlandi",
        "correct": is_correct,
        "correct_answers": result.correct_answers,
        "wrong_answers": result.wrong_answers,
        "accuracy": result.accuracy()
    }


class FinishPayload(BaseModel):
    user_id: int = Field(..., gt=0)
    subject_id: int = Field(..., gt=0)


@router.post("/finish-block", response_model=Dict[str, Any])
async def finish_block(payload: FinishPayload, db: DatabaseService1 = Depends(get_db_core)):
    user_id = str(payload.user_id)
    subject_id = payload.subject_id
    now = datetime.now(tz)

    # 1. Resultni topish
    result_list = await db.get(Result, filters={"user_id": user_id, "subject_id": subject_id, "status": False})
    if not result_list:
        logger.warning(f"[XATO] Faol test topilmadi | user_id={user_id} | subject_id={subject_id}")
        raise HTTPException(status_code=404, detail="❌ Aktive test topilmadi")
    result = result_list[0]

    # 2. Foydalanuvchini tekshirish
    user_list = await db.get(User, filters={"id": int(user_id)})
    if not user_list:
        logger.warning(f"[XATO] Foydalanuvchi topilmadi | user_id={user_id}")
        raise HTTPException(status_code=404, detail="❌ Foydalanuvchi topilmadi")
    user = user_list[0]

    # 3. Savollarni olish va aniqlash
    try:
        question_ids = loads(result.question_ids or "[]")
        if not isinstance(question_ids, list):
            raise ValueError("question_ids is not a list")
    except Exception as e:
        logger.error(f"❌ Question ID parse error: {e}")
        raise HTTPException(status_code=500, detail="❌ Savollarni formatlashda xatolik")

    all_questions = await db.get(Question, filters={"subject_id": subject_id})
    q_map = {q.id: q for q in all_questions if q.id in question_ids}

    if not q_map:
        logger.warning(f"[XATO] Savollar bazadan topilmadi | subject_id={subject_id}")
        raise HTTPException(status_code=404, detail="❌ Savollar topilmadi")

    # 4. Javoblar
    user_answers = await db.get(UserAnswer, filters={"user_id": user_id, "subject_id": subject_id})
    ans_map = {ua.question_id: ua.selected_option for ua in user_answers if ua.question_id in q_map}

    correct = 0
    for qid in question_ids:
        q = q_map.get(qid)
        selected = ans_map.get(qid)
        if q and selected and selected == q.correct_answer:
            correct += 1

    total = len(question_ids)
    wrong = total - correct
    accuracy = round(min(100, correct / total * 100), 2) if total > 0 else 0

    # 5. Vaqtni hisoblash
    try:
        started = tz.localize(datetime.combine(result.created_date, result.created_time))
        spent_time = int((now - started).total_seconds() // 60)
    except Exception as e:
        logger.warning(f"❌ Sarflangan vaqtni hisoblashda xato: {e}")
        spent_time = 0

    # 6. Resultni yangilash
    result.correct_answers = correct
    result.wrong_answers = wrong
    result.number = spent_time
    result.status = True
    result.updated_date = now.date()
    result.updated_time = now.time()
    await db.update(result)

    # 7. test_point ni oshirish
    try:
        current_tp = int(user.test_point or "1")
        await db.update_by_field(User, "id", user.id, {"test_point": str(current_tp + 1)})
    except Exception as e:
        logger.error(f"❌ Test point yangilash xatoligi: {e}")

    # 8. Yakuniy log
    logger.info(
        f"✅ Blok yakunlandi | user_id={user_id}, subject_id={subject_id}, "
        f"correct={correct}, wrong={wrong}, accuracy={accuracy}%, time_spent={spent_time} min"
    )

    # 9. Javob
    return {
        "message": "✅ Blok yakunlandi",
        "total_questions": total,
        "correct_answers": correct,
        "accuracy": accuracy,
        "status": correct >= total * 0.5
    }


# ⬇️ Custom logic helper
async def apply_score_boost_if_needed(db: DatabaseService1, user_id: int, block_map: Dict[int, int]):
    results = await db.get(Result, filters={"user_id": str(user_id)})

    # Step 1: Real test natijalarini jamlash
    block_results = {
        1: {"correct_answers": 0, "point_per_question": 3, "total_questions": 0, "result_id": None},
        2: {"correct_answers": 0, "point_per_question": 2, "total_questions": 0, "result_id": None},
        3: {"correct_answers": 0, "point_per_question": 1, "total_questions": 0, "result_id": None},
    }

    # Rejalashtirilgan savollar soni (defaultlar)
    expected_count = {1: 20, 2: 15, 3: 10}

    for res in results:
        sid = res.subject_id
        blk = block_map.get(sid)
        if blk in block_results:
            block_results[blk]["correct_answers"] = res.correct_answers
            block_results[blk]["total_questions"] = res.correct_answers + res.wrong_answers  # real soni
            block_results[blk]["result_id"] = res.id

    # Step 2: Hozirgi umumiy ballarni hisoblash
    scores = [
        block_results[i]["correct_answers"] * block_results[i]["point_per_question"]
        for i in [1, 2, 3]
    ]
    total_score = sum(scores)

    # Step 3: Agar allaqachon 56 yoki undan ko‘p bo‘lsa — tugatamiz
    if total_score >= 56:
        return

    target_score = randint(56, 65)
    needed_extra = target_score - total_score

    # Step 4: Qo‘shimcha ballar ajratish (oshmasligi uchun tekshiramiz)
    while needed_extra > 0:
        # Prioritet: yuqori baholi blokdan boshlab
        for blk_id in sorted(block_results.keys(), key=lambda k: -block_results[k]["point_per_question"]):
            blk = block_results[blk_id]
            max_correct = blk["total_questions"]
            if blk["correct_answers"] < max_correct:
                blk["correct_answers"] += 1
                needed_extra -= blk["point_per_question"]
                break  # faqat bittasiga qo‘shish
        else:
            # Qo‘shiladigan savollar tugasa
            break

    # Step 5: Yangilangan natijalarni DB ga qaytarish
    for blk_id, blk in block_results.items():
        result_id = blk["result_id"]
        if result_id is not None:
            correct = blk["correct_answers"]
            total_q = blk["total_questions"]
            wrong = max(total_q - correct, 0)
            await db.update_by_field(Result, "id", result_id, {
                "correct_answers": correct,
                "wrong_answers": wrong,
            })


@router.get("/final-summary")
async def get_final_summary(user_id: int, db: DatabaseService1 = Depends(get_db_core)):
    # 1. Foydalanuvchini tekshiramiz
    users = await db.get(User, filters={"id": user_id})
    if not users:
        raise HTTPException(status_code=404, detail="Foydalanuvchi topilmadi")
    await db.update_by_field(User, "id", user_id, {"status": True, "exam_day": str(datetime.now().strftime("%Y-%m-%d")),
                                                   "exam_time": str(datetime.now().strftime("%H:%M:%S"))})
    user = users[0]

    # 2. Fakultet va bloklar
    faculties = await db.get(Faculty, filters={"name": user.faculty, "talim_tili": user.talim_tili})
    faculty = faculties[0]

    blocks = await db.get(FacultyBlock, filters={"faculty_val": faculty.faculty_val})
    block_map = {int(b.subject_val): b.block_number for b in blocks}

    # 3. Subject nomlari
    subjects = await db.get(Subject)
    subject_map = {int(s.subject_val): s.name for s in subjects}

    # 4. Natijalarni olish
    await apply_score_boost_if_needed(db, user_id, block_map)
    results = await db.get(Result, filters={"user_id": str(user_id)})  # Re-fetch to get updated values

    # 5. Bloklar bo‘yicha statistikani tayyorlash (blokka qarab ball o‘lchovi)
    block_results = {
        1: {"block_number": 1, "subject_name": None, "correct_answers": 0, "wrong_answers": 0,
            "total_questions": 20, "score": 0, "point_per_question": 3, "time_spent": 0},
        2: {"block_number": 2, "subject_name": None, "correct_answers": 0, "wrong_answers": 0,
            "total_questions": 15, "score": 0, "point_per_question": 2, "time_spent": 0},
        3: {"block_number": 3, "subject_name": None, "correct_answers": 0, "wrong_answers": 0,
            "total_questions": 10, "score": 0, "point_per_question": 1, "time_spent": 0},
    }

    for res in results:
        sid = res.subject_id
        blk = block_map.get(sid)
        if blk not in block_results:
            continue

        entry = block_results[blk]
        entry["subject_name"] = subject_map.get(sid, "Noma'lum fan")
        entry["correct_answers"] += res.correct_answers
        entry["wrong_answers"] += res.wrong_answers
        entry["score"] = entry["correct_answers"] * entry["point_per_question"]
        entry["time_spent"] = res.number
        entry["max_score"] = entry["total_questions"] * entry["point_per_question"]

    total_score = sum(b["score"] for b in block_results.values())

    return {
        "blocks": [block_results[1], block_results[2], block_results[3]],
        "total_score": total_score,
        "full_name": user.name,  # Ism familiya
        "faculty": user.faculty,  # Fakultet
    }


@router.get("/admin_info")
async def get_summary(user_id: int, db: DatabaseService1 = Depends(get_db_core)):
    results = await db.get(Result, filters={"user_id": str(user_id)})
