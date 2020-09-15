# создаем таблицу с вопросами о ответами...
from random import randint
from django.utils.timezone import now
from django.utils.timezone import now, pytz
from django.utils import timezone
from django.conf import settings
from .models import TblAtt, TblAttQ, TblShemaDet, TblQuest, TblA, TblAnswer, SprCity, \
    SprOtdel, ATblAtt, ATblAttQ, ATblA

# Возвращает


# Возвращает var_cnt ID вопросов из выбранной категории
def get_quest_from_category(id_category, var_cnt):
    locAllID = []
    locRes = []
    # Получаем все ID вопросов в выбранной категории
    all_quest = TblQuest.objects.filter(cat_name=id_category)
    cnt_quest = all_quest.count()
    for list in all_quest:
        locAllID.append(list.pk)
    # в locAllID - список всех ID вопросов в этой категории
    for i in range(0, var_cnt):
        loc_id = randint(locAllID[0], locAllID[-1])
        while not loc_id in locAllID:
            loc_id = randint(locAllID[0], locAllID[-1])
        locRes.append(loc_id)
        locAllID.remove(loc_id)
    return locRes
#  -----------------------------------------------------------------------------------------------------------------  #
# Возвращает список вопросов и ответов
def get_quest_and_answer(id_schema):
    locRes = {}
    curr_schema = TblShemaDet.objects.filter(schema=id_schema)
    # Для каждой категории...
    for categ in curr_schema:
        # Получаем ID категории и кол-во вопросов
        id_cat = categ.tr_categ.pk
        cnt_quest = categ.tr_cnt
        # Получаем список вопросов для этой категории
        curr_quest = get_quest_from_category(id_cat, cnt_quest)
        for i in curr_quest:
            # Получаем список ответов
            loc_ans = {}
            list_ans = TblAnswer.objects.filter(cat_quest=i)
            for j in list_ans:
                loc_ans[j.tr_answer] = j.tr_rigth
            locRes[i] = loc_ans
    return locRes
#  -----------------------------------------------------------------------------------------------------------------  #
# Записыает в БД вопросы и ответы
def make_quest_and_answer(id_att):
    curr_att = TblAtt.objects.get(pk=id_att)
    if not TblAttQ.objects.filter(tblAtt=curr_att).exists():
        list_qa = get_quest_and_answer(curr_att.schema)
        for key, value in list_qa.items():
            quest = TblAttQ()
            quest.tblAtt = curr_att
            loc_quest = TblQuest.objects.get(pk=key)
            quest.quest = loc_quest
            quest.save()
            id_quest = quest.id
            for key1, value1 in value.items():
                answer = TblA()
                loc_answ = TblAttQ.objects.get(pk=id_quest)
                answer.tblattq = loc_answ
                answer.answer = key1
                answer.rigth = value1
                answer.save()
    return
#  -----------------------------------------------------------------------------------------------------------------  #
# Формирование результатов аттестации для админа...
def make_result_attestation_admin(id_att):
    # собрать результаты аттестации...
    # затраченное время
    loc_att = ATblAtt.objects.get(pk=id_att)
    delta = loc_att.end_test - loc_att.start_test
    seconds = delta.seconds
    minutes = (seconds % 3600) // 60
    loc_M_Quest = {}
    LocTrue = 0
    LocFalse = 0
    LocAll = 0
    loc_quest = ATblAttQ.objects.filter(tblAtt=loc_att)
    LocAll = loc_quest.count()
    for quest in loc_quest:
        loc_answer = ATblA.objects.filter(tblattq=quest)
        loc_M_Answer = {}
        locCnt = True  # Если на выходе будет True, значит все ответы на этот вопрос правильные
        for answ in loc_answer:
            loc_F_Answer = []
            loc_F_Answer.append(answ.rigth)
            loc_F_Answer.append(answ.usrans)
            if answ.usrans == answ.rigth:
                loc_F_Answer.append(1)  # Ответ правильный
            else:
                loc_F_Answer.append(0)  # Ответ неправильный
                locCnt = False
            loc_M_Answer[answ.answer] = loc_F_Answer
        loc_M_Quest[quest.quest.tr_quest] = loc_M_Answer
        if locCnt:
            LocTrue += 1
        else:
            LocFalse += 1
    resatt = [loc_M_Quest]
    return resatt, minutes, LocAll, LocTrue, LocFalse
#  -----------------------------------------------------------------------------------------------------------------  #
# Формирование результатов аттестации
def make_result_attestation(id_att):
    # собрать результаты аттестации...
    # затраченное время
    loc_att = TblAtt.objects.get(pk=id_att)
    if loc_att.att_done:
        delta = loc_att.end_test - loc_att.start_test
        seconds = delta.seconds
        minutes = (seconds % 3600) // 60
    else:
        minutes = 0

    loc_M_Quest = {}
    loc_quest = TblAttQ.objects.filter(tblAtt=loc_att)
    for quest in loc_quest:
        loc_answer = TblA.objects.filter(tblattq=quest)
        loc_M_Answer = {}
        for answ in loc_answer:
            loc_M_Answer[answ.answer] = answ.usrans
        loc_M_Quest[quest.quest.tr_quest] = loc_M_Answer
    resatt = [loc_M_Quest]
    return resatt, minutes
#  -----------------------------------------------------------------------------------------------------------------  #
# Первоначальное создание нового пользователя...
def do_fill_user(request):
    # Создаем и получаем ID нового юзера, если его нету...
    if not TblAtt.objects.filter(user_id=request.user).exists():
        curr_att = TblAtt()
        curr_att.user_id = request.user
        curr_att.att_enable = True
        curr_att.save()
    return
#  -----------------------------------------------------------------------------------------------------------------  #
# возвращает список отвеченных вопросов с ответами в процессе тестирования
def make_quest_and_answer_done(id_tblatt):
    loc_att = TblAtt.objects.get(pk=id_tblatt)
    loc_M_Quest = {}
    loc_quest = TblAttQ.objects.filter(tblAtt=loc_att, quest_done=True)
    for quest in loc_quest:
        loc_answer = TblA.objects.filter(tblattq=quest)
        loc_M_Answer = {}
        for answ in loc_answer:
            loc_M_Answer[answ.answer] = answ.usrans
        loc_M_Quest[quest.quest.tr_quest] = loc_M_Answer
    resatt = [loc_M_Quest]
    return resatt
#  -----------------------------------------------------------------------------------------------------------------  #
# Возвращает список для администрирования пользователей
def make_list_user_admin():
    list_city = SprCity.objects.all()
    list_otdel = SprOtdel.objects.all()
    user_timezone = pytz.timezone(settings.TIME_ZONE)
    # Для каждого города
    locRes = {}
    for city in list_city:
        # Для каждого отдела
        locOtdel = {}
        for otdel in list_otdel:
            list_user = TblAtt.objects.filter(city=city, otdel=otdel).order_by('user_id')
            locUsr = {}
            for users in list_user:
                # Для каждого юзера список пройденных аттестаций в формате Дата, ID
                list_attest = ATblAtt.objects.filter(user_id=users.user_id)
                locAtt = {}
                for attest in list_attest:
                    lDate = attest.start_test.astimezone(user_timezone).strftime("%d-%m-%Y %H:%M:%S")+' -- '+attest.end_test.astimezone(user_timezone).strftime("%d-%m-%Y %H:%M:%S")
                    lId = attest.pk
                    locAtt[lDate] = lId
                locIndx = users.user_id.first_name+' '+users.user_id.last_name
                locUsr[locIndx] = locAtt
            locOtdel[otdel] = locUsr
        locRes[city] = locOtdel
    return locRes
#  -----------------------------------------------------------------------------------------------------------------  #
# Копирует законченную аттестацию в архив, удаляет из таблицы аттестаций вопросы с ответами, формирует новые,
# att_enable = False, att_done = False
def do_after_end_attestation(id_att):
    curr_att = TblAtt.objects.get(pk=id_att)
    new_arch_att = ATblAtt()
    new_arch_att.user_id = curr_att.user_id
    new_arch_att.city = curr_att.city
    new_arch_att.otdel = curr_att.otdel
    user_timezone = pytz.timezone(settings.TIME_ZONE)
    new_arch_att.start_test = curr_att.start_test.astimezone(user_timezone)
    new_arch_att.end_test = curr_att.end_test.astimezone(user_timezone)
    new_arch_att.schema = curr_att.schema
    new_arch_att.save()
    list_quest = TblAttQ.objects.filter(tblAtt=curr_att)
    for quest in list_quest:
        new_quest = ATblAttQ()
        new_quest.tblAtt = new_arch_att
        new_quest.quest = quest.quest
        new_quest.save()
        new_quest_id = new_quest
        list_answ = TblA.objects.filter(tblattq=quest)
        for answ in list_answ:
            new_answ = ATblA()
            new_answ.tblattq = new_quest_id
            new_answ.answer = answ.answer
            new_answ.rigth = answ.rigth
            new_answ.usrans = answ.usrans
            new_answ.save()
    curr_att.att_done = False
    curr_att.att_enable = False
    curr_att.schema = None
    curr_att.save()
    for quest in list_quest:
        quest.delete()
    make_quest_and_answer(curr_att.pk)
    return
#  -----------------------------------------------------------------------------------------------------------------  #
# Формирование результатов аттестации
def view_user_result_attestation(id_att):
    # собрать результаты аттестации...
    # затраченное время
    loc_att = ATblAtt.objects.get(pk=id_att.pk)
    delta = loc_att.end_test - loc_att.start_test
    seconds = delta.seconds
    minutes = (seconds % 3600) // 60
#    LocRes = get_result_attestaion(loc_att, 0)
    loc_M_Quest = {}
    loc_quest = ATblAttQ.objects.filter(tblAtt=loc_att)
    for quest in loc_quest:
        loc_answer = ATblA.objects.filter(tblattq=quest)
        loc_M_Answer = {}
        for answ in loc_answer:
            loc_M_Answer[answ.answer] = answ.usrans
        loc_M_Quest[quest.quest.tr_quest] = loc_M_Answer
    resatt = [loc_M_Quest]
    return resatt, minutes
#    return LocRes, minutes
#  -----------------------------------------------------------------------------------------------------------------  #
# Результаты аттестации. Общая ф-ция.
# Вход: id_att: ID аттестации в архиве lWhat: 0 - для пользователя, 1 - для администратора
def get_result_attestaion(id_att, lWhat):
    LocRes = {}
    list_quest = ATblAttQ.objects.filter(tblAtt=id_att)
    for quest in list_quest:
        list_answer = ATblA.objects.filter(tblattq=quest)
        val_answ = {}
        for answ in list_answer:
            if lWhat == 1:  # Для администратора - правильный ответ и ответ пользователя
                val_answ[answ.answer] = [answ.rigth, answ.usrans]
            else:   # Для пользователя - только его ответ :)
                val_answ[answ.answer] = [answ.usrans]
        LocRes[quest.quest.tr_quest] = val_answ
    return LocRes
#  -----------------------------------------------------------------------------------------------------------------  #
# Возвращает текущую длительность аттестации в минутах
def get_attestation_current_time(sch_time, start_time):
    # sch_time - сколько минут дается всего
    # start_time - время начала аттестации
    # Сколько минут прошло с начала аттестации
    print(timezone.now())
    print(start_time)
    delta = timezone.now() - start_time
    seconds = delta.seconds
    minutes = (seconds % 3600) // 60
    # Сколько минут на аттестацию - Сколько минут прошло с начала аттестации
    locMin = sch_time - minutes
    return locMin
