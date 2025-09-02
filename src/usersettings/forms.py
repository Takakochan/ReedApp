from django import forms
from .models import Checkbox_for_setting, data_preference
from .widgets import CustomCheckboxSelectMultiple


class ContactForm(forms.ModelForm):
    parameters = forms.MultipleChoiceField(choices=data_preference,
                                           widget=CustomCheckboxSelectMultiple)

    class Meta:
        model = Checkbox_for_setting
        fields = ('parameters', )
