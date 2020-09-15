from django.contrib import admin
from .models import TblCategory, TblQuest, TblAnswer, TblAtt, TblSchema, TblShemaDet, ATblAtt, SprCity, SprOtdel

# Register your models here.
class TblAnswerInline(admin.StackedInline):
    model = TblAnswer


class TblQuestAdmin(admin.ModelAdmin):
    inlines = [TblAnswerInline, ]


class TblQuestInline(admin.StackedInline):
    model = TblQuest


class TblCategoryAdmin(admin.ModelAdmin):
    inlines = [TblQuestInline, ]


class TblSchemaDetInline(admin.StackedInline):
    model = TblShemaDet


class TblSchemaAdmin(admin.ModelAdmin):
    inlines = [TblSchemaDetInline, ]


class SprCityAdmin(admin.ModelAdmin):
    model = SprCity


class SprOtdelAdmin(admin.ModelAdmin):
    model = SprOtdel

@admin.register(TblAtt)
class TblAttAdmin(admin.ModelAdmin):
    list_display = ('otdel', 'user_id', 'schema', 'start_test', 'end_test')
    list_filter = ('user_id', 'otdel', 'schema', 'start_test')

class ATblAttAdmin(admin.ModelAdmin):
    model = ATblAtt

admin.site.register(TblCategory, TblCategoryAdmin)
admin.site.register(TblQuest, TblQuestAdmin)
admin.site.register(TblSchema, TblSchemaAdmin)
admin.site.register(ATblAtt, ATblAttAdmin)
admin.site.register(SprCity, SprCityAdmin)
admin.site.register(SprOtdel, SprOtdelAdmin)

