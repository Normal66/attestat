from django.db import models
from django.contrib.auth.models import User

# Create your models here.
# Справочник категорий ( OKS, ZU, etc... )
class TblCategory(models.Model):
    tr_name = models.CharField(max_length=150, verbose_name='Название категории')

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.tr_name

# Справочник городов

class SprCity(models.Model):
    city_name = models.CharField(max_length=150, verbose_name='Город')

    class Meta:
        verbose_name = 'Город'
        verbose_name_plural = 'Города'

    def __str__(self):
        return self.city_name

# Справочник отделов
class SprOtdel(models.Model):
    otdel_name = models.CharField(max_length=150, verbose_name='Отдел')

    class Meta:
        verbose_name = 'Отдел'
        verbose_name_plural = 'Отделы'

    def __str__(self):
        return self.otdel_name

# Вопросы
class TblQuest(models.Model):
    cat_name = models.ForeignKey(TblCategory, on_delete=models.CASCADE, verbose_name='Категория')
    tr_quest = models.CharField(max_length=2000, verbose_name='Вопрос')

    class Meta:
        verbose_name = 'Вопрос'
        verbose_name_plural = 'Вопросы'

    def __str__(self):
        return self.tr_quest

# Ответы
class TblAnswer(models.Model):
    cat_quest = models.ForeignKey(TblQuest, on_delete=models.CASCADE, verbose_name='Вопрос')
    tr_answer = models.TextField(verbose_name='Ответ')
    tr_rigth = models.BooleanField(default=False, verbose_name='Правильный ответ')

    class Meta:
        verbose_name = 'Ответ'
        verbose_name_plural = 'Ответы'

    def __str__(self):
        return self.tr_answer

# ------------------------------------------------------------------------------------------------------------------- #
# Таблица схем
class TblSchema(models.Model):
    tr_name = models.CharField(max_length=150, verbose_name='Схема')
    schema_time = models.SmallIntegerField(default=20, blank=True, verbose_name='Кол-во Минут на прохождение')

    class Meta:
        verbose_name = 'Схема'
        verbose_name_plural = 'Схемы'

    def __str__(self):
        return self.tr_name


class TblShemaDet(models.Model):
    schema = models.ForeignKey(TblSchema, on_delete=models.CASCADE, verbose_name='Схема')
    tr_categ = models.ForeignKey(TblCategory, on_delete=models.CASCADE, verbose_name='Категория')
    tr_cnt = models.SmallIntegerField(default=0, verbose_name='Кол-во вопросов')

    class Meta:
        verbose_name = 'Схема Деталь'
        verbose_name_plural = 'Схемы Детали'

    def __str__(self):
        return 'Пока_не_знаю'

# -------------------------------------------------------------------------------------------------------------------- #
# Основная инфа о пользователе + данные об аттестации
class TblAtt(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, blank=False)
    city = models.ForeignKey(SprCity, null=True, on_delete=models.SET_NULL, blank=True, verbose_name='Город')
    otdel = models.ForeignKey(SprOtdel, null=True, on_delete=models.SET_NULL, blank=True, verbose_name='Отдел')
    start_test = models.DateTimeField(null=True, blank=True, verbose_name='Начало тестирования')
    end_test = models.DateTimeField(null=True, blank=True, verbose_name='Окончание тестирования')
    schema = models.ForeignKey(TblSchema, blank=True, null=True, on_delete=models.SET_NULL, verbose_name='Выбранная схема')
    att_done = models.BooleanField(default=False, verbose_name='Тестирование пройдена')
    att_enable = models.BooleanField(default=False, verbose_name='Разрешить тестирование')
    att_archive = models.BooleanField(default=False, verbose_name='В архиве')

    class Meta:
        verbose_name = 'Аттестация'
        verbose_name_plural = 'Аттестации'

    def __str__(self):
        return self.user_id.first_name+' '+self.user_id.last_name


class TblAttQ(models.Model):
    tblAtt = models.ForeignKey(TblAtt, on_delete=models.CASCADE, blank=False)
    quest = models.ForeignKey(TblQuest, on_delete=models.CASCADE, blank=False, verbose_name='Вопрос')
    quest_done = models.BooleanField(default=False, verbose_name='Отвечено')

    class Meta:
        verbose_name = 'Вопросы пользователя'
        verbose_name_plural = 'Ответы пользователя'

    def __str__(self):
        return self.quest.tr_quest


class TblA(models.Model):
    tblattq = models.ForeignKey(TblAttQ, on_delete=models.CASCADE)
    answer = models.TextField(verbose_name='Ответ')
    rigth = models.BooleanField(default=False, verbose_name='Правильный ответ')
    usrans = models.BooleanField(default=False, verbose_name='Да')

    def __str__(self):
        return self.answer

# ------------------------------------------------------------------------------------------------------------------- #
# АРХИВЫ АТТЕСТАЦИЙ
# -------------------------------------------------------------------------------------------------------------------- #
# Основная инфа о пользователе + данные об аттестации
class ATblAtt(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, blank=False)
    city = models.ForeignKey(SprCity, null=True, on_delete=models.SET_NULL, blank=True, verbose_name='Город')
    otdel = models.ForeignKey(SprOtdel, null=True, on_delete=models.SET_NULL, blank=True, verbose_name='Отдел')
    start_test = models.DateTimeField(null=True, blank=True, verbose_name='Начало тестирования')
    end_test = models.DateTimeField(null=True, blank=True, verbose_name='Окончание тестирования')
    schema = models.ForeignKey(TblSchema, blank=True, null=True, on_delete=models.SET_NULL, verbose_name='Выбранная схема')

    class Meta:
        verbose_name = 'Архив аттестаций'
        verbose_name_plural = 'Архивы аттестаций'

    def __str__(self):
        return self.user_id.first_name+' '+self.user_id.last_name


class ATblAttQ(models.Model):
    tblAtt = models.ForeignKey(ATblAtt, on_delete=models.CASCADE, blank=False)
    quest = models.ForeignKey(TblQuest, on_delete=models.CASCADE, blank=False, verbose_name='Вопрос')

    def __str__(self):
        return self.quest.tr_quest


class ATblA(models.Model):
    tblattq = models.ForeignKey(ATblAttQ, on_delete=models.CASCADE)
    answer = models.TextField(verbose_name='Ответ')
    rigth = models.BooleanField(default=False, verbose_name='Правильный ответ')
    usrans = models.BooleanField(default=False, verbose_name='Да')

    def __str__(self):
        return self.answer
