from .models import TblCategory, TblQuest, TblAnswer
from django.utils.encoding import iri_to_uri
import xlsxwriter
import io


def do_calc_row(lStr):
    # получаем остаток от деления
    return (len(lStr) // 80) * 15 + 15


def get_excel_by_categ(pk):
# Возвращает для загрузки XLS файл с вопросами и ответами для выбранной категории
    tbl_cat = TblCategory.objects.get(pk=pk)
    tbl_quest = TblQuest.objects.filter(cat_name=tbl_cat)
    try:
        output = io.BytesIO()
        file_xlsx_name = tbl_cat.tr_name+'.xlsx'
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

        Loc_Cnt = 5
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
#                    loc_red.append(Loc_Cnt)

            Loc_Cnt += 2
        Loc_Cnt += 2
        worksheet.write(Loc_Cnt, 1, 'Всего вопросов: '+str(loc_all)+'  Правильных ответов : '+str(loc_true)+'   Неправильных ответов: '+str(loc_false), format_cell)
        for i in loc_red:
            worksheet.set_row(i, None, format_red)
            worksheet.write(i, 0, 'ОТВЕТ НЕПРАВИЛЬНЫЙ', format_red)
    finally:
        workbook.close()
        output.seek(0)
    for lst_quest in tbl_quest:
        tbl_answ = TblAnswer.objects.filter(cat_quest=lst_quest)
        for lst_answ in tbl_answ:
            print(lst_answ.tr_answer)
    return
