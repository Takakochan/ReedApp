from operator import methodcaller
from django import forms
from .models import Reedsdata
from usersettings.models import Checkbox_for_setting


######################################completed###############################
class ViewUser:

    def __init__(self, user):
        self.current_user = user

    def get_field_list(self):
        try:
            data = Checkbox_for_setting.objects.get(user=self.current_user)
            l = data.checkboxsetting
            l = 'instrument,reed_ID,' + l
            print(l)
            return l
        except Checkbox_for_setting.DoesNotExist:
            return []


class Caneform(forms.ModelForm):
    density_auto_display = forms.FloatField(label="Auto Calculated Density",
                                            required=False,
                                            disabled=True)

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        mode = kwargs.pop('mode', 'add')
        super().__init__(*args, **kwargs)

        selected_fields = ViewUser(user).get_field_list() if user else []

        edit_only_fields = [
            'perceived_stiffness', 'playing_ease', 'global_quality',
            'intonation', 'tone_color', 'response_time', 'evaluation'
        ]

        # If user selected density_auto:
        if 'density_auto' in selected_fields:
            # Show m1, m2, and density_auto_display
            selected_fields += 'm1' + 'm2' + 'density_auto_display'
            # Remove regular density field
            if 'density' in self.fields:
                self.fields.pop('density')

        # Clean up fields based on selection
        for field_name in list(self.fields):
            if field_name not in selected_fields and field_name not in edit_only_fields:
                self.fields.pop(field_name)
            if field_name in edit_only_fields and mode == 'add':
                self.fields.pop(field_name)

        # Show auto-calculated density
        if self.instance:
            self.fields[
                'density_auto_display'].initial = self.instance.density_auto

    class Meta:
        model = Reedsdata
        fields = '__all__'


#######################################################
