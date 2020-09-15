import pytz
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.forms import inlineformset_factory
from django.shortcuts import render, redirect
from django.template.response import TemplateResponse
from .utility import get_attestation_current_time
from django.utils.encoding import iri_to_uri
import xlsxwriter
import io
from django.http import HttpResponse
from django.utils import timezone

from .models import TblAtt, TblA, TblAttQ, ATblAtt
from django.shortcuts import render, get_object_or_404
from .forms import UserDetailForm,  UsrProfileForm, UsrAnswerForm
from .utility import make_quest_and_answer, make_result_attestation_admin, make_result_attestation,\
    do_fill_user, make_quest_and_answer_done, make_list_user_admin, do_after_end_attestation,\
    view_user_result_attestation

# ------------------------------------------------------------------------------------------------------------------- #
# Профиль пользователя. Сюда он переходит после каждого входа в систему!!!
# Создается запись для аттестации -
# Запрашиваются поля город, отдел, схема
# Создается таблица Q&A
def profile(request):
    # Создаем TblAtt
    do_fill_user(request)
    post = TblAtt.objects.get(user_id=request.user)
    if not post.city or not post.otdel or not post.schema:
        if request.method == "POST":
            form = UsrProfileForm(request.POST, instance=post)
            if form.is_valid() and not form.cleaned_data['schema'] == None and not form.cleaned_data['city'] == None and not form.cleaned_data['otdel'] == None:
                post.save()
                # формируем вопросы и ответы согласно выбранной схемы
                make_quest_and_answer(post.pk)
                return redirect('index')
        else:
            form = UsrProfileForm(instance=post)
            form.user_id = request.user
        return render(request, 'profile.html', {'form': form, 'usr': post})
    return redirect('index')
# ------------------------------------------------------------------------------------------------------------------- #
# Главная страница пользователя - меню и список пройденных аттестаций
@login_required
def index(request):
    loc_att = TblAtt.objects.get(user_id=request.user)
    loc_archive = ATblAtt.objects.filter(user_id=request.user)
    context = ({'douser': loc_att, 'arch': loc_archive})
    return TemplateResponse(request, "index.html", context)
# ------------------------------------------------------------------------------------------------------------------- #
# Обработка меню Начало тестирования
@login_required
def do_attestation(request, pk):
    att = TblAtt.objects.get(pk=pk)
    att.start_test = timezone.now()
    att.save()
    # Список вопросов с ответами
    list_quest = TblAttQ.objects.filter(tblAtt=att)
    # Список УЖЕ отвеченных вопросов в процессе аттестации
    list_done = make_quest_and_answer_done(att.pk)
    att = TblAtt.objects.get(pk=pk)
    # Время на аттестацию
    loc = get_attestation_current_time(att.schema.schema_time, att.start_test)
    context = ({'quest': list_quest, "att": att, 'mins': loc, 'qdone': list_done})
    return TemplateResponse(request, "doattestat.html", context)
# ------------------------------------------------------------------------------------------------------------------- #
# Ответ аттестуемого на вопрос
@login_required
def get_answer(request, pk):
    quest = TblAttQ.objects.get(pk=pk)
    loc_title = quest.quest.tr_quest
    loc_tblatt = quest.tblAtt.pk
    att = TblAtt.objects.get(pk=loc_tblatt)
    list_quest = TblAttQ.objects.filter(tblAtt=att)
    loc = get_attestation_current_time(att.schema.schema_time, att.start_test)

    AnswerFormSet = inlineformset_factory(TblAttQ, TblA, form=UsrAnswerForm, extra=0, can_delete=False)
    answ = TblA.objects.filter(tblattq=quest)
    if request.method == 'POST':
        formset = AnswerFormSet(request.POST, instance=quest)
        formset.save()
        loc_quest = TblAttQ.objects.get(pk=pk)
        loc_quest.quest_done = True
        loc_quest.save()
        list_done = make_quest_and_answer_done(att.pk)
        return TemplateResponse(request, "doattestat.html", {'quest': list_quest, 'mins': loc, 'qdone': list_done})
    else:
        formset = AnswerFormSet(instance=quest)
    return render(request, "attestation.html", {"formset": formset, "loctitle": loc_title, 'mins': loc})
# ------------------------------------------------------------------------------------------------------------------- #
# Завершение аттестации
def attestation_done(request):
    curr_attestation = TblAtt.objects.get(user_id=request.user)
    curr_attestation.end_test = timezone.now()
    curr_attestation.att_done = True
    curr_attestation.save()
    # Перемещение в архив, очистка вопросов, удаление текущей схемы
    do_after_end_attestation(curr_attestation.pk)
    return redirect('logout')
# ------------------------------------------------------------------------------------------------------------------- #
# Администрирование аттестаций - просмотр по городам/отделам/пользователям.
# У пользователя - список прошедших аттестаций с просмотром и экспортом в Excel
@login_required
def usermanage(request):
    tblAtt = TblAtt.objects.all().order_by('user_id__last_name')
    list_users = make_list_user_admin()
    return TemplateResponse(request, "usermanager.html", {'att': tblAtt, 'list_usr': list_users})
# ------------------------------------------------------------------------------------------------------------------- #
@login_required
def useredit(request, pk):
    post = get_object_or_404(TblAtt, pk=pk)
    id_tblatt = post.pk
    if request.method == "POST":
        form = UserDetailForm(request.POST, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
#            do_make_quest_and_answer(id_tblatt)
            return redirect('user-manage')
    else:
        form = UserDetailForm(instance=post)
        form.user_id = request.user
    return render(request, 'user_edit.html', {'form': form})
# ------------------------------------------------------------------------------------------------------------------- #


@login_required
def view_admin_result_user(request, pk):
    loc_att = ATblAtt.objects.get(pk=pk)
    resatt, minute, lall, ltrue, lfalse = make_result_attestation_admin(pk)
    return TemplateResponse(request, "view-result-admin.html", {'douser': loc_att, 'resatt': resatt, 'minute': minute,
                                                                'vall': lall, 'vtrue': ltrue, 'vfalse': lfalse})

# ------------------------------------------------------------------------------------------------------------------- #
def do_calc_row(lStr):
    # получаем остаток от деления
    return (len(lStr) // 80) * 15 + 15

# Формирование файла XLSX с результатами тестирования...
def make_result_into_excel(request, pk):
    loc_list, minutes, loc_all, loc_true, loc_false = make_result_attestation_admin(pk)
    loc_att = ATblAtt.objects.get(pk=pk)
    loc_name = loc_att.user_id.first_name+' '+loc_att.user_id.last_name+'  ('+loc_att.city.city_name+'  -  '+loc_att.otdel.otdel_name+')'
    user_timezone = pytz.timezone(settings.TIME_ZONE)
    loc_date_att = loc_att.start_test.astimezone(user_timezone).strftime("%d-%m-%Y %H:%M:%S")+' - '+loc_att.end_test.astimezone(user_timezone).strftime("%d-%m-%Y %H:%M:%S")+'     Всего : '+str(minutes)+' мин'
    loc_red = []
    try:
        output = io.BytesIO()
        file_xlsx_name = loc_att.user_id.first_name+'-'+loc_att.user_id.last_name+'.xlsx'
        # Создание книги и листа Excel.
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet()

        # Определим форматирование
        # колонка с ответом = 40 символов
        worksheet.set_column(1, 1, width=50)
        worksheet.set_column(2, 4, width=7)
        format_answer = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'border': True})
        format_cell = workbook.add_format({'italic': True, 'bold': True, 'border': True})
        cell_format = workbook.add_format()
        cell_format.set_text_wrap()
        cell_border_format = workbook.add_format()
        cell_border_format.set_text_wrap()
        cell_border_format.set_border()
        quest_format = workbook.add_format()
        quest_format.set_bold()
        quest_format.set_text_wrap()
        format_red = workbook.add_format({'align': 'center', 'valign': 'vcenter'})
        format_red.set_font_color('red')

        worksheet.write(0, 0, loc_name)
        worksheet.write(1, 0, loc_date_att)
        worksheet.write(2, 0, 'Схема : '+loc_att.schema.tr_name+'   '+str(loc_att.schema.schema_time)+'  мин. на аттестацию')

        Loc_Cnt = 5
        curr_list = loc_list[0]
        for quest, answ in curr_list.items():
            worksheet.write(Loc_Cnt, 0, 'Вопрос :', format_cell)
            vopros_pos = Loc_Cnt
            Loc_Cnt += 1
            worksheet.set_row(Loc_Cnt, do_calc_row(quest))
            worksheet.merge_range(Loc_Cnt, 0, Loc_Cnt, 4, quest, cell_format)
            worksheet.write(Loc_Cnt, 0, quest, quest_format)

            Loc_Cnt += 1
            worksheet.write(Loc_Cnt, 1, 'Ответ', format_cell)
            worksheet.write(Loc_Cnt, 2, 'БД', format_cell)
            worksheet.write(Loc_Cnt, 3, 'ОП', format_cell)
            worksheet.write(Loc_Cnt, 4, 'Баллы', format_cell)
            for key, values in answ.items():
                Loc_Cnt += 1
                worksheet.write(Loc_Cnt, 1, key, cell_border_format)
                if values[0]:
                    worksheet.write(Loc_Cnt, 2, 'ДА', format_answer)
                else:
                    worksheet.write(Loc_Cnt, 2, 'НЕТ', format_answer)
                if values[1]:
                    worksheet.write(Loc_Cnt, 3, 'ДА', format_answer)
                else:
                    worksheet.write(Loc_Cnt, 3, 'НЕТ', format_answer)
                worksheet.write(Loc_Cnt, 4, values[2], format_answer)
                if values[2] == 0:
                    loc_red.append(vopros_pos)
                                                    
            Loc_Cnt += 2
        Loc_Cnt += 2
        worksheet.write(Loc_Cnt, 1, 'Всего вопросов: '+str(loc_all)+'  Правильных ответов : '+str(loc_true)+'   Неправильных ответов: '+str(loc_false), format_cell)
        for i in loc_red:
            worksheet.set_row(i, None, format_red)
            worksheet.write(i, 0, 'ОТВЕТ НЕПРАВИЛЬНЫЙ', format_red)
    finally:
        workbook.close()
        output.seek(0)

#    response = HttpResponse(output, content_type='application/vnd.ms-excel')
#    response['Content-Disposition'] = f"attachment; filename={file_xlsx_name};"
#    output.save(response)

    response = HttpResponse(output, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename= "{}"'.format(iri_to_uri(file_xlsx_name))
#    output.save(response)
#    response['HTTP_CONTENT_DISPOSITION'] = f"attachment; filename=result.xlsx;"
#    output.close()
    return response
#  -----------------------------------------------------------------------------------------------------------------  #
@login_required
def view_user_attestation(request, pk):
    loc_att = ATblAtt.objects.get(pk=pk)
    resatt, minutes = view_user_result_attestation(loc_att)
    return TemplateResponse(request, "view-user-attestation.html", {'douser': loc_att, 'loctime': minutes, 'resatt': resatt})
