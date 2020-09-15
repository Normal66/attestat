from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from okszu.models import TblCategory, TblQuest, TblAnswer
from django.utils.encoding import iri_to_uri
import xlsxwriter
import io


# Create your views here.
def get_category(request):
    categ = TblCategory.objects.all()
    return render(request,
                  'admwrap.html',
                  {'categ': categ})


def do_calc_row(lStr):
    # получаем остаток от деления
    return (len(lStr) // 80) * 15 + 15


def get_excel_by_categ(request, pk):
    tbl_cat = TblCategory.objects.get(pk=pk)
    tbl_quest = TblQuest.objects.filter(cat_name=tbl_cat)
    try:
        output = io.BytesIO()
        file_xlsx_name = tbl_cat.tr_name + '.xlsx'
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

        Loc_Cnt = 0
        for quest in tbl_quest:
            worksheet.write(Loc_Cnt, 0, 'Вопрос :', format_cell)
            Loc_Cnt += 1
            worksheet.set_row(Loc_Cnt, do_calc_row(quest.tr_quest))
            worksheet.merge_range(Loc_Cnt, 0, Loc_Cnt, 4, quest.tr_quest, cell_format)
            worksheet.write(Loc_Cnt, 0, quest.tr_quest, quest_format)

            tbl_ans = TblAnswer.objects.filter(cat_quest=quest)
            for answ in tbl_ans:
                Loc_Cnt += 1
                worksheet.write(Loc_Cnt, 1, 'Ответ', format_cell)
                Loc_Cnt += 1
                worksheet.write(Loc_Cnt, 1, answ.tr_answer, cell_border_format)
            Loc_Cnt += 2
        Loc_Cnt += 2
    finally:
        workbook.close()
        output.seek(0)
    response = HttpResponse(
        output,
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename={}'.format(iri_to_uri(file_xlsx_name))
    output.close()
    return response

