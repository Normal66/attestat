from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field
from django import forms
from django.forms.models import inlineformset_factory, BaseInlineFormSet, ModelForm
from .models import TblAtt, TblAttQ, TblA


class UsrProfileForm(forms.ModelForm):
    class Meta:
        model = TblAtt
        fields = ('city', 'otdel', 'schema')


class UserDetailForm(forms.ModelForm):
    class Meta:
        model = TblAtt
        fields = ('user_id', 'schema', 'att_done', 'att_enable',)

class AttestatForm(forms.ModelForm):
    class Meta:
        model = TblAttQ
        fields = ('quest', )

# ------------------------------------------------------------------------------------------------------------------- #
class QuestForm(ModelForm):
    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(Field('quest'),)
        super(QuestForm, self).__init__(*args, **kwargs)

    class Meta:
        model = TblAttQ
        fields = ('quest',)


class AnswerForm(ModelForm):
    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(Field('answer', 'usrans'),)
        super(AnswerForm, self).__init__(*args, **kwargs)

    class Meta:
        model = TblA
        fields = ('answer', 'usrans',)
        widgets = {
            'answer': forms.Textarea(attrs={'rows': 3, 'cols': 120}),  # this is changeble.
        }
        widgets['answer'].attrs['readonly'] = True

# ------------------------------------------------------------------------------------------------------------------  #
class UsrAnswerForm(ModelForm):
    class Meta:
        model = TblA
        fields = ('usrans', 'answer', )
        widgets = {
            'answer': forms.Textarea(attrs={'rows': 3, 'cols': 120}),  # this is changeble.
        }
        widgets['answer'].attrs['readonly'] = True
