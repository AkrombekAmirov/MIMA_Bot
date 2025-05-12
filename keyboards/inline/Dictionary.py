from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

list_regioin = ["reg0", "reg1", "reg2", "reg3", "reg4", "reg5", "reg6", "reg7", "reg8", "reg9", "reg10", "reg11",
                "reg12", "reg13"]
list_region1 = ["Toshkent viloyati", "Toshkent shahri", "Samarqand viloyati", "Namangan viloyati", "Andijon viloyati",
                "Fargona viloyati", "Qashqadaryo viloyati", "Surxondaryo viloyati", "Jizzax viloyati",
                "Xorazm viloyati", "Navoiy viloyati", "Buxoro viloyati", "Sirdaryo viloyati",
                "Qoraqalpogʻiston Respublikasi"]

list_faculty = ["faculty0", "faculty1", "faculty2", "faculty3", "faculty4", "faculty5", "faculty6", "faculty7",
                "faculty8", "faculty9", "faculty10", "faculty11", "faculty12", "faculty13", "faculty14", "faculty15",
                "faculty16", "faculty17"]
# await db.add(FacultyBlock(faculty_val='1', subject_val='2', block_number=1))
# await db.add(FacultyBlock(faculty_val='1', subject_val='8', block_number=2))
# await db.add(FacultyBlock(faculty_val='1', subject_val='7', block_number=3))
# await db.add(FacultyBlock(faculty_val='2', subject_val='2', block_number=1))
# await db.add(FacultyBlock(faculty_val='2', subject_val='8', block_number=2))
# await db.add(FacultyBlock(faculty_val='2', subject_val='7', block_number=3))
# await db.add(FacultyBlock(faculty_val='3', subject_val='2', block_number=1))
# await db.add(FacultyBlock(faculty_val='3', subject_val='8', block_number=2))
# await db.add(FacultyBlock(faculty_val='3', subject_val='7', block_number=3))
# await db.add(FacultyBlock(faculty_val='4', subject_val='2', block_number=1))
# await db.add(FacultyBlock(faculty_val='4', subject_val='8', block_number=2))
# await db.add(FacultyBlock(faculty_val='4', subject_val='7', block_number=3))
# await db.add(FacultyBlock(faculty_val='5', subject_val='3', block_number=1))
# await db.add(FacultyBlock(faculty_val='5', subject_val='8', block_number=2))
# await db.add(FacultyBlock(faculty_val='5', subject_val='7', block_number=3))
# await db.add(FacultyBlock(faculty_val='6', subject_val='2', block_number=1))
# await db.add(FacultyBlock(faculty_val='6', subject_val='8', block_number=2))
# await db.add(FacultyBlock(faculty_val='6', subject_val='7', block_number=3))
# await db.add(FacultyBlock(faculty_val='7', subject_val='1', block_number=1))
# await db.add(FacultyBlock(faculty_val='7', subject_val='8', block_number=2))
# await db.add(FacultyBlock(faculty_val='7', subject_val='7', block_number=3))
# await db.add(FacultyBlock(faculty_val='8', subject_val='2', block_number=1))
# await db.add(FacultyBlock(faculty_val='8', subject_val='8', block_number=2))
# await db.add(FacultyBlock(faculty_val='8', subject_val='7', block_number=3))
# await db.add(FacultyBlock(faculty_val='9', subject_val='2', block_number=1))
# await db.add(FacultyBlock(faculty_val='9', subject_val='8', block_number=2))
# await db.add(FacultyBlock(faculty_val='9', subject_val='7', block_number=3))
# await db.add(FacultyBlock(faculty_val='2', subject_val='2', block_number=1))
# await db.add(Subject(name="Huquqshunoslik", subject_val='1', language="O'zbek tili"))
# await db.add(Subject(name="Matematika", subject_val='2', language="O'zbek tili"))
# await db.add(Subject(name="Psixologiya", subject_val='3', language="O'zbek tili"))
# await db.add(Subject(name="Huquqshunoslik", subject_val='4', language="Rus tili"))
# await db.add(Subject(name="Matematika", subject_val='5', language="Rus tili"))
# await db.add(Subject(name="Psixologiya", subject_val='6', language="Rus tili"))
# await db.add(Subject(name="Ingliz tili", subject_val='7', language="O'zbek tili"))
# await db.add(Subject(name="Ona tili", subject_val='8', language="O'zbek tili"))
# await db.add(Subject(name="Nemis tili", subject_val='9', language="O'zbek tili"))
# await db.add(Subject(name="Fransuz tili", subject_val='10', language="O'zbek tili"))

faculty_file_map2 = {
    "faculty0": 'Mehnat muhofazasi va texnika xavfsizligi',
    "faculty1": 'Hayot faoliyati xavfsizligi',
    "faculty2": 'Inson resurslarini boshqarish',
    "faculty3": 'Ijtimoiy ish',
    "faculty4": 'Psixologiya',
    "faculty5": 'Menejment',
    "faculty6": 'Yurisprudensiya',
    "faculty7": 'Bugalteriya hisobi',
    "faculty8": 'Metrologiya va standartlashtirish'
}

Toshkent_viloyat = [
    "Bekobod tumani",
    "Boʻstonliq tumani",
    "Boʻka tumani",
    "Chinoz tumani",
    "Qibray tumani",
    "Ohangaron tumani",
    "Oqqoʻrgʻon tumani",
    "Parkent tumani",
    "Piskent tumani",
    "Quyi chirchiq tumani",
    "Oʻrta Chirchiq tumani",
    "Yangiyoʻl tumani",
    "Yuqori Chirchiq tumani",
    "Zangiota tumani",
    "Olmaliq shahri",
    'Angren shahri',
    'Nurafshon shahri',
    'Chirchiq shahri',
    'Piskent'
]

Toshkent_shahri = [
    "Bektemir tumani",
    "Chilonzor tumani",
    "Yashnaobod tumani",
    "Mirobod tumani",
    "Mirzo Ulugʻbek tumani",
    "Sergeli tumani",
    "Shayxontohur tumani",
    "Olmazor tumani",
    "Uchtepa tumani",
    "Yakkasaroy tumani",
    "Yunusobod tumani",
    "Yangihayot tumani",
]

Samarqand = [
    "Bulungʻur tumani",
    "Ishtixon tumani",
    "Jomboy tumani",
    "Kattaqoʻrgʻon tumani",
    "Qoʻshrabot tumani",
    "Narpay tumani",
    "Nurobod tumani",
    "Oqdaryo tumani",
    "Paxtachi tumani",
    "Payariq tumani",
    "Pastdargʻom tumani",
    "Samarqand tumani",
    "Samarqand shahri",
    "Toyloq tumani",
    "Urgut tumani"
]

Andijon = [
    "Andijon tuman",
    "Andijon shahri",
    "Asaka tumani",
    "Baliqchi tumani",
    "Bo'ston tuman",
    "Buloqboshi tumani",
    "Izboskan tuman",
    "Jalaquduq tuman",
    "Xoʻjaobod tumani",
    "Qoʻrgʻontepa tumani",
    "Marhamat tumani",
    "Oltinkoʻl tuman",
    "Paxtaobod tumani",
    "Shahrixon tuman",
    "Ulugʻnor tuman",
    'Xonobod shahri',
]

Buxoro = [
    "Olot tumani",
    "Buxoro tumani",
    "Gʻijduvon tumani",
    "Jondor tumani",
    "Kogon tumani",
    "Qorakoʻl tumani",
    "Qorovulbozor tumani",
    "Peshku tumani",
    "Romitan tumani",
    "Shofirkon tumani",
    "Vobkent tumani"
]

Navoiy = [
    "Konimex tumani",
    "Karmana tumani",
    "Qiziltepa tumani",
    "Xatirchi tumani",
    "Navbahor tumani",
    "Navoiy shahri",
    "Nurota tumani",
    "Tomdi tumani",
    "Uchquduq tumani",
    "Zarafshon shahri",
    "G'azg'on shahri"
]

Namangan = [
    "Chortoq tumani",
    "Chust tumani",
    "Kosonsoy tumani",
    "Mingbuloq tumani",
    "Namangan tumani",
    "Norin tumani",
    "Pop tumani",
    "Toʻraqoʻrgʻon tumani",
    "Uchqoʻrgʻon tumani",
    "Uychi tumani",
    "Yangiqoʻrgʻon tumani",
    'Namangan shahar',
    'Yangi Namangan',
    'Davlatobod tumani',
]

# Namangan viloyati tumanlari
namangan = [
    "Chortoq tumani",
    "Kosonsoy tumani",
    "Mingbuloq tumani",
    "Namangan tumani",
    "Norin tumani",
    "Pop tumani",
    "To'raqo'rg'on tumani",
    "Uchko'prik tumani",
]

# Farg'ona viloyati tumanlari
Fargona = [
    "Oltiariq tumani",
    "Bagʻdod tumani",
    "Beshariq tumani",
    "Buvayda tumani",
    "Dangʻara tumani",
    "Fargʻona tumani",
    'Farg‘ona shahri'
    "Furqat tumani",
    "Qoʻshtepa tumani",
    "Quva tumani",
    "Rishton tumani",
    "Soʻx tumani",
    "Toshloq tumani",
    "Uchkoʻprik tumani",
    "Oʻzbekiston tumani",
    "Yozyovon tumani",
    "Quvasoy shahri",
    "Margʻilon tumani",
    'Qo‘qon shahri',
]

# Qashqadaryo viloyati tumanlari
Qashqadaryo = [
    "Chiroqchi tumani",
    "Dehqonobod tumani",
    "Gʻuzor tumani",
    "Qamashi tumani",
    "Qarshi tumani",
    "Koson tumani",
    "Kasbi tumani",
    "Kitob tumani",
    "Mirishkor tumani",
    "Muborak tumani",
    "Nishon tumani",
    "Shahrisabz tumani",
    "Yakkabogʻ tumani",
    "Koʻkdala tumani"
]

# Surxondaryo viloyati tumanlari
Surxondaryo = [
    "Angor tumani",
    "Boysun tumani",
    "Denov tumani",
    "Jarqoʻrgʻon tumani",
    "Qiziriq tumani",
    "Qumqoʻrgʻon tumani",
    "Muzrabot tumani",
    "Oltinsoy tumani",
    "Sariosiyo tumani",
    "Sherobod tumani",
    "Shoʻrchi tumani",
    "Termiz tumani",
    "Uzun tumani",
    'Termiz shahri',
    'Bandixon tumani',
]

# Jizzax viloyati tumanlari
Jizzax = [
    "Arnasoy tumani",
    "Baxmal tumani",
    "Doʻstlik tumani",
    "Forish tumani",
    "Gʻallaorol tumani",
    "Sharof Rashidov tumani",
    "Mirzachoʻl tumani",
    "Paxtakor tumani",
    "Yangiobod tumani",
    "Zomin tumani",
    "Zafarobod tumani",
    "Zarbdor tumani",
    'Jizzax shahri'
]

# Xorazm viloyati tumanlari
Xorazm = [
    "Bogʻot tumani",
    "Gurlan tumani",
    "Xonqa tumani",
    "Hazorasp tumani",
    "Xiva tumani",
    "Qoʻshkoʻpir tumani",
    "Shovot tumani",
    "Urganch tumani",
    "Yangiariq tumani",
    "Yangibozor tumani",
    "Tuproqqalʼa tumani",
    "Urganch shahri",
    "Xiva shahri"
]

# Sirdaryo viloyati tumanlari
Sirdaryo = [
    "Oqoltin tumani",
    "Boyovut tumani",
    "Guliston tumani",
    "Xovos tumani",
    "Mirzaobod tumani",
    "Sayxunobod tumani",
    "Sardoba tumani",
    "Sirdaryo tumani",
    "Yangiyer shahri",
    "Shirin shahri",
    "Guliston shahri"
]

# Qoraqalpog'iston Respublikasi tumanlari
Qoraqalpogiston = [
    "Amudaryo tumani",
    "Beruniy tumani",
    "Chimboy tumani",
    "Ellikqalʼa tumani",
    "Kegeyli tumani",
    "Moʻynoq tumani",
    "Nukus tumani",
    "Nukus shahri",
    "Qanlikoʻl tumani",
    "Qoʻngʻirot tumani",
    "Qoraoʻzak tumani",
    "Shumanay tumani",
    "Taxtakoʻpir tumani",
    "Toʻrtkoʻl tumani",
    "Xoʻjayli tumani",
    "Taxiatosh tumani",
    "Boʻzatov tumani"
]

list_tuman = ["Amudaryo tumani", "Beruniy tumani", "Chimboy tumani", "Ellikqalʼa tumani", "Kegeyli tumani",
              "Moʻynoq tumani", "Nukus tumani", "Nukus shahri", "Qanlikoʻl tumani", "Qoʻngʻirot tumani",
              "Qoraoʻzak tumani",
              "Shumanay tumani", "Taxtakoʻpir tumani", "Toʻrtkoʻl tumani", "Xoʻjayli tumani", "Taxiatosh tumani",
              "Boʻzatov tumani", "Oqoltin tumani", "Boyovut tumani", "Guliston tumani", "Xovos tumani",
              "Mirzaobod tumani", "Sayxunobod tumani", "Sardoba tumani", "Sirdaryo tumani", "Yangiyer shahri",
              "Shirin shahri", "Guliston shahri", "Bogʻot tumani", "Gurlan tumani", "Xonqa tumani", "Hazorasp tumani",
              "Xiva tumani", "Qoʻshkoʻpir tumani", "Shovot tumani", "Urganch tumani", "Yangiariq tumani",
              "Yangibozor tumani", "Tuproqqalʼa tumani", "Arnasoy tumani", "Baxmal tumani", "Doʻstlik tumani",
              "Forish tumani", "Gʻallaorol tumani", "Sharof Rashidov tumani", "Mirzachoʻl tumani", "Paxtakor tumani",
              "Yangiobod tumani", "Zomin tumani", "Zafarobod tumani", "Zarbdor tumani", "Angor tumani", "Boysun tumani",
              "Denov tumani", "Jarqoʻrgʻon tumani", "Qiziriq tumani", "Qumqoʻrgʻon tumani", "Muzrabot tumani",
              "Oltinsoy tumani", "Sariosiyo tumani", "Sherobod tumani", "Shoʻrchi tumani", "Termiz tumani",
              "Uzun tumani", "Chiroqchi tumani", "Dehqonobod tumani", "Gʻuzor tumani", "Qamashi tumani",
              "Qarshi tumani", "Koson tumani", "Kasbi tumani", "Kitob tumani", "Mirishkor tumani", "Muborak tumani",
              "Nishon tumani", "Shahrisabz tumani", "Yakkabogʻ tumani", "Koʻkdala tumani", "Oltiariq tumani",
              "Bagʻdod tumani", "Beshariq tumani", "Buvayda tumani", "Dangʻara tumani", "Fargʻona tumani",
              "Furqat tumani", "Qoʻshtepa tumani", "Quva tumani", "Rishton tumani", "Soʻx tumani", "Toshloq tumani",
              "Uchkoʻprik tumani", "Oʻzbekiston tumani", "Yozyovon tumani", "Quvasoy shahri", "Chortoq tumani",
              "Kosonsoy tumani", "Mingbuloq tumani", "Namangan tumani", "Norin tumani", "Pop tumani",
              "To'raqo'rg'on tumani", "Uchko'prik tumani", "Konimex tumani", "Karmana tumani", "Qiziltepa tumani",
              "Xatirchi tumani", "Navbahor tumani", "Nurota tumani", "Tomdi tumani", "Uchquduq tumani",
              "Chortoq tumani", "Chust tumani", "Kosonsoy tumani", "Mingbuloq tumani", "Namangan tumani",
              "Norin tumani", "Pop tumani", "Toʻraqoʻrgʻon tumani", "Uchqoʻrgʻon tumani", "Uychi tumani",
              "Yangiqoʻrgʻon tumani", "Olot tumani", "Buxoro tumani", "Gʻijduvon tumani", "Jondor tumani",
              "Kogon tumani", "Qorakoʻl tumani", "Qorovulbozor tumani", "Peshku tumani", "Romitan tumani",
              "Shofirkon tumani", "Vobkent tumani", "Andijon tuman", "Asaka tumani", "Baliqchi tumani", "Bo'stontuman",
              "Buloqboshi tumani", "Izboskan tuman", "Jalaquduq tuman", "Xoʻjaobod tumani", "Qoʻrgʻontepa tumani",
              "Marhamat tumani", "Oltinkoʻl tuman", "Paxtaobod tumani", "Shahrixon tuman", "Ulugʻnor tuman",
              "Bektemir tumani", "Chilonzor tumani", "Yashnaobod tumani", "Mirobod tumani", "Mirzo Ulugʻbek tumani",
              "Sergeli tumani", "Shayxontohur tumani", "Olmazor tumani", "Uchtepa tumani", "Yakkasaroy tumani",
              "Yunusobod tumani", "Yangihayot tumani", "Bulungʻur tumani", "Ishtixon tumani", "Jomboy tumani",
              "Kattaqoʻrgʻon tumani", "Qoʻshrabot tumani", "Narpay tumani", "Nurobod tumani", "Oqdaryo tumani",
              "Paxtachi tumani", "Payariq tumani", "Pastdargʻom tumani", "Samarqand tumani", "Toyloq tumani",
              "Urgut tumani", "Bekobod tumani", "Boʻstonliq tumani", "Boʻka tumani", "Chinoz tumani", "Qibray tumani",
              "Ohangaron tumani", "Oqqoʻrgʻon tumani", "Parkent tumani", "Piskent tumani", "Quyi chirchiq tumani",
              "Oʻrta Chirchiq tumani", "Yangiyoʻl tumani", "Yuqori Chirchiq tumani", "Zangiota tumani", "Navoiy shahri",
              "Zarafshon tumani", "Margʻilon tumani","Olmaliq shahri", 'Angren shahri', 'Nurafshon shahri', 'Chirchiq shahri', 'Piskent',
              "Samarqand shahri", 'Xonobod shahri', "Andijon shahri", 'Farg‘ona shahri', 'Qo‘qon shahri', 'Namangan shahar',
              'Yangi Namangan', 'Davlatobod tumani', 'Bandixon tumani', 'Termiz shahri', 'Jizzax shahri', "Urganch shahri", "Xiva shahri",
              "Zarafshon shahri", "G'azg'on shahri"
              ]


# Tumanlar uchun InlineKeyboardMarkup yaratish


def create_tumanlar_keyboard(tumanlar):
    tumanlar_keyboard = InlineKeyboardMarkup(row_width=1)
    for tuman in tumanlar:
        tumanlar_keyboard.add(InlineKeyboardButton(tuman, callback_data=f"{tuman}"))
    return tumanlar_keyboard


async def inline_tumanlar(viloyat):
    region = None
    if viloyat == "reg0":
        region = Toshkent_viloyat
    elif viloyat == "reg1":
        region = Toshkent_shahri
    elif viloyat == "reg2":
        region = Samarqand
    elif viloyat == "reg3":
        region = Namangan
    elif viloyat == "reg4":
        region = Andijon
    elif viloyat == "reg5":
        region = Fargona
    elif viloyat == "reg6":
        region = Qashqadaryo
    elif viloyat == "reg7":
        region = Surxondaryo
    elif viloyat == "reg8":
        region = Jizzax
    elif viloyat == "reg9":
        region = Xorazm
    elif viloyat == "reg10":
        region = Navoiy
    elif viloyat == "reg11":
        region = Buxoro
    elif viloyat == "reg12":
        region = Sirdaryo
    elif viloyat == "reg13":
        region = Qoraqalpogiston

    if region:
        return create_tumanlar_keyboard(region)
