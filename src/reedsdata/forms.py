from django import forms
from .models import Reedsdata
from usersettings.models import Checkbox_for_setting
from django.core.exceptions import ValidationError
import re


class ViewUser:

    def __init__(self, user):
        self.current_user = user

    def get_field_list(self):
        try:
            data = Checkbox_for_setting.objects.get(user=self.current_user)
            l = data.checkboxsetting
            l = 'instrument,reed_ID,' + l
            return l
        except Checkbox_for_setting.DoesNotExist:
            return []


class Caneform(forms.ModelForm):
    density_auto_display = forms.FloatField(label="Calculated Density",
                                            required=False,
                                            disabled=True)

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        mode = kwargs.pop('mode', 'add')
        super().__init__(*args, **kwargs)
        
        # Store mode for use in validation
        self._mode = mode

        # In batch mode, make Reed ID optional (rows without Reed ID will be ignored)
        if mode == 'batch' and 'reed_ID' in self.fields:
            self.fields['reed_ID'].required = False

        # Set custom labels for mass fields
        if 'm1' in self.fields:
            self.fields['m1'].label = 'Dry Mass'
        if 'm2' in self.fields:
            self.fields['m2'].label = 'Wet Mass'
            
        # Set custom labels for global quality fields
        if 'global_quality_first_impression' in self.fields:
            self.fields['global_quality_first_impression'].label = 'Global Quality (1st Impression)'
        if 'global_quality_second_impression' in self.fields:
            self.fields['global_quality_second_impression'].label = 'Global Quality (2nd Impression)'
        if 'global_quality_third_impression' in self.fields:
            self.fields['global_quality_third_impression'].label = 'Global Quality (3rd Impression)'
            
        # Set custom labels for count fields
        if 'counts_rehearsal' in self.fields:
            self.fields['counts_rehearsal'].label = 'Rehearsal Count'
        if 'counts_concert' in self.fields:
            self.fields['counts_concert'].label = 'Concert Count'
            
        # Set custom labels for gouging machine fields
        if 'bed_diameter' in self.fields:
            self.fields['bed_diameter'].label = 'Bed Diameter (mm)'
        if 'blade_diameter' in self.fields:
            self.fields['blade_diameter'].label = 'Blade Diameter (mm)'
            
        # Set custom label for shaper model field
        if 'shaper_model' in self.fields:
            self.fields['shaper_model'].label = 'Shaper Model'
            
        # Set custom label for diameter field
        if 'diameter' in self.fields:
            self.fields['diameter'].label = 'Cane Diameter'
            
        # Set custom labels for chamber condition fields
        if 'chamber_temperature' in self.fields:
            self.fields['chamber_temperature'].label = 'Chamber Temperature'
        if 'chamber_humidity' in self.fields:
            self.fields['chamber_humidity'].label = 'Chamber Humidity'

        # In batch mode, use same filtered fields as the parameter selector
        if mode == 'batch' and user:
            # Get the user's selected field list from settings
            settings_selected_fields = ViewUser(user).get_field_list()
            if settings_selected_fields:
                settings_selected_list = [field.strip() for field in settings_selected_fields.split(',') if field.strip()]
            else:
                settings_selected_list = []
            
            # Add related fields if their parent fields are selected
            additional_fields = []
            if 'gouging_machine' in settings_selected_list:
                additional_fields.extend(['bed_diameter', 'blade_diameter'])
            if 'shaper' in settings_selected_list:
                additional_fields.append('shaper_model')
            if 'density_auto' in settings_selected_list:
                additional_fields.extend(['m1', 'm2', 'density_auto_display'])
            
            # Always include mandatory fields
            mandatory_fields = ['reed_ID', 'instrument', 'cane_brand']
            
            # Combine all included fields
            all_form_fields = list(set(mandatory_fields + settings_selected_list + additional_fields))
            
            # Add all evaluation fields
            from .templatetags.custom_filters import is_evaluation_field
            from .models import UserParameter
            user_params_all = UserParameter.objects.filter(user=user)
            for up in user_params_all:
                if is_evaluation_field(up.parameter.name):
                    all_form_fields.append(up.parameter.name)
            
            # Remove conflicting fields
            if 'density_auto' in all_form_fields and 'density' in all_form_fields:
                all_form_fields.remove('density')  # Remove regular density when using density_auto
            
            # Create selected_fields string (remove duplicates)
            selected_fields = ','.join(list(set(all_form_fields)))
        else:
            selected_fields = ViewUser(user).get_field_list() if user else []

        edit_only_fields = [
            'perceived_stiffness', 'playing_ease', 
            'global_quality_first_impression', 'global_quality_second_impression', 
            'global_quality_third_impression', 'intonation', 'tone_color', 
            'response', 'counts_rehearsal', 'counts_concert', 'note'
        ]

        # Density auto logic
        if 'density_auto' in selected_fields:
            # Add m1, m2, and density_auto_display to selected fields
            if 'm1' not in selected_fields:
                selected_fields = selected_fields + ',m1'
            if 'm2' not in selected_fields:
                selected_fields = selected_fields + ',m2'
            if 'density_auto_display' not in selected_fields:
                selected_fields = selected_fields + ',density_auto_display'
            # Remove density field since we're using auto calculation (in all modes)
            if 'density' in self.fields:
                self.fields.pop('density')

        # In batch mode, don't automatically add related fields - let user control them
        # In other modes, add related fields automatically
        if mode != 'batch':
            # Gouging machine logic - add bed and blade diameter fields automatically
            if 'gouging_machine' in selected_fields:
                if 'bed_diameter' not in selected_fields:
                    selected_fields = selected_fields + ',bed_diameter'
                if 'blade_diameter' not in selected_fields:
                    selected_fields = selected_fields + ',blade_diameter'

            # Shaper logic - add shaper model field automatically
            if 'shaper' in selected_fields:
                if 'shaper_model' not in selected_fields:
                    selected_fields = selected_fields + ',shaper_model'

        # Weather and chamber fields will be handled automatically, exclude from form
        fields_to_exclude = ['location', 'altitude', 'temperature', 'humidity', 'air_pressure', 'weather_description', 
                             'chamber_temperature', 'chamber_humidity']
        
        # Remove unselected fields
        for field_name in list(self.fields):
            # Exclude weather and chamber fields (handled automatically)
            if field_name in fields_to_exclude:
                self.fields.pop(field_name)
                continue
            # In batch mode, keep evaluation fields even if not in selected_fields
            elif mode == 'batch' and field_name in edit_only_fields:
                continue  # Keep evaluation fields in batch mode
            elif field_name not in selected_fields and field_name not in edit_only_fields:
                self.fields.pop(field_name)
            # Remove evaluation fields in regular add mode only
            elif field_name in edit_only_fields and mode == 'add':
                self.fields.pop(field_name)

        # クラス付与（フォームセット用）
        for field_name in ['m1', 'm2', 'density_auto_display']:
            if field_name in self.fields:
                cls = 'density-auto' if field_name == 'density_auto_display' else field_name
                existing = self.fields[field_name].widget.attrs.get(
                    'class', '')
                if field_name == 'density_auto_display':
                    # Make calculated density field gray
                    self.fields[field_name].widget.attrs.update(
                        {'class': f'{existing} {cls} bg-gray-100'})
                else:
                    self.fields[field_name].widget.attrs.update(
                        {'class': f'{existing} {cls}'})

        # Reorder fields to put density_auto_display after m1 and m2
        if 'density_auto_display' in self.fields and ('m1' in self.fields or 'm2' in self.fields):
            field_order = []
            for field_name in self.fields:
                if field_name == 'density_auto_display':
                    continue
                field_order.append(field_name)
                # Insert density_auto_display after m2
                if field_name == 'm2' and 'density_auto_display' in self.fields:
                    field_order.append('density_auto_display')
            
            # Rebuild fields in the new order
            ordered_fields = {}
            for field_name in field_order:
                if field_name in self.fields:
                    ordered_fields[field_name] = self.fields[field_name]
            self.fields = ordered_fields

    def clean_reed_ID(self):
        """Validate reed ID for security"""
        reed_id = self.cleaned_data.get('reed_ID')
        if reed_id:
            # Only allow alphanumeric, hyphens, and underscores
            if not re.match(r'^[A-Za-z0-9_-]+$', reed_id):
                raise ValidationError('Reed ID can only contain letters, numbers, hyphens, and underscores')
            if len(reed_id) > 20:
                raise ValidationError('Reed ID must be 20 characters or less')
        return reed_id
    
    def clean_note(self):
        """Sanitize and validate notes field"""
        note = self.cleaned_data.get('note')
        if note:
            # Remove potentially dangerous HTML/script tags
            note = re.sub(r'<script.*?>.*?</script>', '', note, flags=re.IGNORECASE | re.DOTALL)
            note = re.sub(r'<.*?>', '', note)  # Remove all HTML tags
            # Limit length
            if len(note) > 500:
                raise ValidationError('Note must be 500 characters or less')
        return note
    
    def clean_hardness(self):
        """Validate hardness range"""
        hardness = self.cleaned_data.get('hardness')
        if hardness is not None:
            if hardness < 0 or hardness > 100:
                raise ValidationError('Hardness must be between 0 and 100')
        return hardness
    
    def clean_flexibility(self):
        """Validate flexibility range"""
        flexibility = self.cleaned_data.get('flexibility')
        if flexibility is not None:
            if flexibility < 0 or flexibility > 100:
                raise ValidationError('Flexibility must be between 0 and 100')
        return flexibility
    
    def clean_density(self):
        """Validate density range"""
        density = self.cleaned_data.get('density')
        if density is not None:
            if density < 0 or density > 2.0:
                raise ValidationError('Density must be between 0 and 2.0')
        return density
    
    def clean(self):
        """Custom validation for the entire form"""
        cleaned_data = super().clean()
        
        # In batch mode, allow forms without Reed ID (they'll be ignored)
        if hasattr(self, '_mode') and self._mode == 'batch':
            reed_id = cleaned_data.get('reed_ID')
            
            # If no Reed ID, this row will be ignored - don't validate other fields
            if not reed_id or reed_id.strip() == '':
                return cleaned_data
        
        return cleaned_data
    
    class Meta:
        model = Reedsdata
        fields = '__all__'
        widgets = {
            'location': forms.TextInput(attrs={
                'class': 'w-full px-2 py-1 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500 bg-white',
                'placeholder': 'e.g., Boston, MA or Concert Hall Name',
                'id': 'id_location'
            }),
            'altitude': forms.NumberInput(attrs={
                'class': 'form-control',
                'readonly': True
            }),
            'temperature': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.1',
                'placeholder': '°C'
            }),
            'humidity': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': '%',
                'min': '0',
                'max': '100'
            }),
            'air_pressure': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': 'hPa'
            }),
            'weather_description': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Clear sky, Light rain'
            }),
            'chamber_temperature': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.1',
                'placeholder': '°C'
            }),
            'chamber_humidity': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.1',
                'placeholder': '%',
                'min': '0',
                'max': '100'
            }),
        }


PARAM_CHOICES = [
    ('thickness', 'Thickness'),
    ('diameter', 'Diameter'),
    ('hardness', 'Hardness'),
    ('flexibility', 'Flexibility'),
    ('m1', 'Dry Mass'),
    ('m2', 'Wet Mass'),
    ('bed_diameter', 'Bed Diameter (mm)'),
    ('blade_diameter', 'Blade Diameter (mm)'),
]


class BatchSettingsForm(forms.Form):
    parameters = forms.MultipleChoiceField(choices=PARAM_CHOICES,
                                           widget=forms.CheckboxSelectMultiple,
                                           label="Select Parameters to Enter")
    num_can = forms.IntegerField(min_value=1,
                                 max_value=50,
                                 initial=10,
                                 label="Number of Canes")
