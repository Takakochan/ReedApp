from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView
from django.contrib.auth.decorators import login_required
import pandas as pd
from .models import Reedsdata, UserParameter, Parameter
from .forms import Caneform, ViewUser
from usersettings.models import Checkbox_for_setting
from .security import require_reed_owner, log_suspicious_activity, rate_limit_user
from .weather_service import get_location_weather_data
from django.http import JsonResponse
from django.utils import timezone
import json


def capture_weather_snapshot_for_impression(reed_obj, impression_type, weather_data):
    """
    Capture weather snapshot when a Global Quality impression is recorded.
    impression_type: 'first', 'second', or 'third'
    weather_data: dict containing weather information
    """
    if not weather_data:
        return
        
    field_prefix = f'global_quality_{impression_type}_weather_'
    
    # Set weather fields for this impression
    if 'location' in weather_data:
        setattr(reed_obj, f'{field_prefix}location', weather_data['location'])
    if 'temperature' in weather_data:
        setattr(reed_obj, f'{field_prefix}temperature', weather_data['temperature'])
    if 'humidity' in weather_data:
        setattr(reed_obj, f'{field_prefix}humidity', weather_data['humidity'])
    if 'air_pressure' in weather_data:
        setattr(reed_obj, f'{field_prefix}pressure', weather_data['air_pressure'])
    if 'weather_description' in weather_data:
        setattr(reed_obj, f'{field_prefix}description', weather_data['weather_description'])


# Create your views here.
class ReedsdataListView(ListView):
    model = Reedsdata
    template_name = 'reeddata_list.html'  # Customize this
    context_object_name = 'reed_list'

    def get_queryset(self):
        return Reedsdata.objects.filter(user=self.request.user)


#def chart_select_view(request):
#    #rd1 = pd.DataFrame(Reedsdata.objects.all().values())
#    rd1 = pd.DataFrame(
#        Reedsdata.objects.filter(reedauthor=request.user).values())
#    rd1 = rd1.replace(['NaN', 'None', ''], float('nan'))
#    rd1 = rd1.dropna(how='all')
#    print(rd1)
#
#    context = {
#        'reedeval': rd1.to_html,
#    }
#
#    return render(request, 'reedsdata/edit.html', context)


@login_required
@rate_limit_user(max_requests=30, window_minutes=15)
@log_suspicious_activity("DATA_ENTRY")
def data_entry(request):
    # Get user's last location from recent reeds
    last_location_data = {}
    recent_reed = Reedsdata.objects.filter(
        reedauthor=request.user,
        location__isnull=False
    ).exclude(location='').order_by('-date').first()
    
    if recent_reed:
        last_location_data = {
            'location': recent_reed.location,
            'temperature': float(recent_reed.temperature) if recent_reed.temperature else None,
            'humidity': float(recent_reed.humidity) if recent_reed.humidity else None,
            'air_pressure': float(recent_reed.air_pressure) if recent_reed.air_pressure else None,
            'altitude': recent_reed.altitude,
            'weather_description': recent_reed.weather_description,
        }
    
    if request.method == 'POST':
        form = Caneform(request.POST, user=request.user, mode='add')
        if form.is_valid():
            obj = form.save(commit=False)
            obj.reedauthor = request.user

            # Check if user selected 'density_auto' and calculate
            if 'density_auto' in ViewUser(request.user).get_field_list():
                m1 = form.cleaned_data.get('m1')
                m2 = form.cleaned_data.get('m2')
                if m1 is not None and m2:
                    try:
                        obj.density = m1 / (m1 + m2)
                    except ZeroDivisionError:
                        obj.density = None

            obj.save()
            # Clear the form after submission
            form = Caneform(user=request.user, mode='add')
    else:
        form = Caneform(user=request.user, mode='add')

    context = {
        'form': form,
        'last_location_data': json.dumps(last_location_data),
        'has_previous_location': bool(last_location_data),
        'last_location_display': last_location_data,
    }
    return render(request, 'reedsdata/add.html', context)


#!!!!!!ORIGINAL!!!!
#def data_entry(request):
#    form = Caneform(request.POST or None)
#    if form.is_valid():
#        obj = form.save(commit=False)
#        obj.reedauthor = request.user
#        obj.save()
#    context = {
#        'form': form,
#    }
#    return render(request, 'reedsdata/add.html', context)
#


@login_required
def reedsdata_list(request):
    reeds = Reedsdata.objects.filter(reedauthor=request.user).order_by('-date')
    return render(request, 'reedsdata/reedsdata_list.html', {'reeds': reeds})


@login_required
@require_reed_owner
@log_suspicious_activity("EDIT_REED")
def edit_reedsdata(request, pk):
    instance = get_object_or_404(Reedsdata, pk=pk, reedauthor=request.user)

    # Get next and previous objects for the same user
    next_obj = Reedsdata.objects.filter(reedauthor=request.user,
                                        pk__gt=pk).order_by('pk').first()
    prev_obj = Reedsdata.objects.filter(reedauthor=request.user,
                                        pk__lt=pk).order_by('-pk').first()

    if request.method == 'POST':
        form = Caneform(request.POST,
                        instance=instance,
                        user=request.user,
                        mode='edit')
        if form.is_valid():
            obj = form.save(commit=False)
            if 'density_auto' in ViewUser(request.user).get_field_list():
                m1 = form.cleaned_data.get('m1')
                m2 = form.cleaned_data.get('m2')
                if m1 is not None and m2:
                    try:
                        obj.density = m1 / (m1 + m2)
                    except ZeroDivisionError:
                        obj.density = None
            
            # Check if any Global Quality impressions were newly recorded and capture weather
            original_obj = get_object_or_404(Reedsdata, pk=pk, reedauthor=request.user)
            weather_data_str = request.POST.get('current_weather')  # From JavaScript
            
            if weather_data_str:
                try:
                    weather_data = json.loads(weather_data_str)
                    
                    # Check which impressions are newly recorded
                    if (obj.global_quality_first_impression is not None and 
                        original_obj.global_quality_first_impression is None):
                        capture_weather_snapshot_for_impression(obj, 'first', weather_data)
                        obj.global_quality_first_impression_date = timezone.now()
                    
                    if (obj.global_quality_second_impression is not None and 
                        original_obj.global_quality_second_impression is None):
                        capture_weather_snapshot_for_impression(obj, 'second', weather_data)
                        obj.global_quality_second_impression_date = timezone.now()
                    
                    if (obj.global_quality_third_impression is not None and 
                        original_obj.global_quality_third_impression is None):
                        capture_weather_snapshot_for_impression(obj, 'third', weather_data)
                        obj.global_quality_third_impression_date = timezone.now()
                        
                except json.JSONDecodeError:
                    pass  # Ignore if weather data is malformed
            
            obj.save()
            return redirect('reeds:reedsdata_list')
    else:
        form = Caneform(instance=instance, user=request.user, mode='edit')

    # Get user parameters for flexible field display
    user_field_list = ViewUser(request.user).get_field_list()
    
    return render(request, 'reedsdata/edit_reedsdata.html', {
        'form': form,
        'next_obj': next_obj,
        'prev_obj': prev_obj,
        'user_field_list': user_field_list,
    })


@login_required
@require_reed_owner
@log_suspicious_activity("DELETE_REED")
def delete_reedsdata(request, pk):
    instance = get_object_or_404(Reedsdata, pk=pk, reedauthor=request.user)
    if request.method == 'POST':
        instance.delete()
        return redirect('reeds:reedsdata_list')
    return render(request, 'reedsdata/confirm_delete.html',
                  {'object': instance})


from django.forms import modelformset_factory
from .forms import Caneform, ViewUser
from .models import Reedsdata
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from django.forms import modelformset_factory
from .forms import Caneform, ViewUser
from .models import Reedsdata
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.utils import timezone


@login_required
def data_entry_batch(request):
    # Default number of canes to display
    default_num_can = 5

    # Determine how many rows the user wants
    num_can = default_num_can
    if request.method == 'POST' and 'num_can' in request.POST:
        try:
            num_can = int(request.POST.get('num_can', default_num_can))
            if num_can < 1:
                num_can = default_num_can
        except ValueError:
            num_can = default_num_can

    # Create a formset with dynamic number of extra forms
    CaneFormSet = modelformset_factory(Reedsdata,
                                       form=Caneform,
                                       extra=num_can,
                                       can_delete=False)

    if request.method == 'POST' and 'num_can' not in request.POST:
        # Actual submission of forms
        formset = CaneFormSet(request.POST,
                              queryset=Reedsdata.objects.none(),
                              form_kwargs={
                                  'user': request.user,
                                  'mode': 'batch'
                              })
        if formset.is_valid():
            for form in formset:
                obj = form.save(commit=False)
                obj.reedauthor = request.user

                # Auto-calculate density if selected
                if 'density_auto' in ViewUser(request.user).get_field_list():
                    m1 = form.cleaned_data.get('m1')
                    m2 = form.cleaned_data.get('m2')
                    if m1 is not None and m2:
                        try:
                            obj.density = m1 / (m1 + m2)
                        except ZeroDivisionError:
                            obj.density = None
                obj.save()
            return redirect('reeds:reedsdata_list')
    else:
        # Display empty formset
        formset = CaneFormSet(queryset=Reedsdata.objects.none(),
                              form_kwargs={
                                  'user': request.user,
                                  'mode': 'batch'
                              })

    context = {
        'formset': formset,
        'num_can': num_can,
    }
    return render(request, 'reedsdata/add_batch.html', context)


from .forms import BatchSettingsForm


@login_required
def batch_settings(request):
    if request.method == 'POST':
        form = BatchSettingsForm(request.POST)
        if form.is_valid():
            # store choices in session for next step
            request.session['batch_parameters'] = form.cleaned_data[
                'parameters']
            request.session['batch_num_can'] = form.cleaned_data['num_can']
            return redirect('reeds:add_batch')
    else:
        form = BatchSettingsForm()

    return render(request, 'reedsdata/batch_settings.html', {'form': form})


from django.shortcuts import render, redirect
from .forms import Caneform
from django.forms import modelformset_factory
from .models import Reedsdata


@login_required
def add_batch(request):
    # ViewUser と同じロジックを使って、フォームに表示される実際のフィールドを取得
    from .forms import ViewUser
    field_list_str = ViewUser(request.user).get_field_list()
    if field_list_str:
        # カンマ区切りの文字列を分割
        selected_field_names = [field.strip() for field in field_list_str.split(',') if field.strip()]
    else:
        selected_field_names = []

    # フィールド名の処理
    mapped_field_names = []
    for field_name in selected_field_names:
        # density_auto の場合は、それ自体を追加せずに m1, m2, density_auto_display を追加
        if field_name == 'density_auto':
            mapped_field_names.extend(['m1', 'm2', 'density_auto_display'])
        else:
            mapped_field_names.append(field_name)

    # Get user's selected parameters from settings plus all evaluation fields
    from .forms import ViewUser
    from .templatetags.custom_filters import is_evaluation_field
    
    # Get the user's selected field list from settings
    selected_field_list = ViewUser(request.user).get_field_list()
    if selected_field_list:
        selected_fields = [field.strip() for field in selected_field_list.split(',') if field.strip()]
    else:
        selected_fields = []
    
    # Get UserParameters that are either selected OR evaluation fields
    user_params = UserParameter.objects.filter(
        user=request.user
    ).select_related('parameter')
    
    # Add related fields if their parent fields are selected
    additional_fields = []
    if 'gouging_machine' in selected_fields:
        additional_fields.extend(['bed_diameter', 'blade_diameter'])
    if 'shaper' in selected_fields:
        additional_fields.append('shaper_model')
    if 'density_auto' in selected_fields:
        additional_fields.extend(['m1', 'm2', 'density_auto_display'])
    
    # Always include mandatory fields (like add.html)
    mandatory_fields = ['reed_ID', 'instrument', 'cane_brand']
    
    # Combine all included fields: mandatory + selected + related
    all_included_fields = list(set(mandatory_fields + selected_fields + additional_fields))
    
    # Filter to include: mandatory fields, selected fields, related fields, OR evaluation fields
    filtered_params = []
    for up in user_params:
        param_name = up.parameter.name
        if (param_name in all_included_fields or 
            is_evaluation_field(param_name)):
            filtered_params.append(up)
    
    # Sort by order, but group related fields with their parents
    def get_sort_key(up):
        param_name = up.parameter.name
        base_order = up.order
        
        # Adjust order for related fields to appear right after their parent
        if param_name == 'bed_diameter':
            # Find gouging_machine order and add 0.1
            gouging_param = next((p for p in filtered_params if p.parameter.name == 'gouging_machine'), None)
            return gouging_param.order + 0.1 if gouging_param else base_order
        elif param_name == 'blade_diameter':
            # Find gouging_machine order and add 0.2
            gouging_param = next((p for p in filtered_params if p.parameter.name == 'gouging_machine'), None)
            return gouging_param.order + 0.2 if gouging_param else base_order
        elif param_name == 'shaper_model':
            # Find shaper order and add 0.1
            shaper_param = next((p for p in filtered_params if p.parameter.name == 'shaper'), None)
            return shaper_param.order + 0.1 if shaper_param else base_order
        elif param_name == 'm1':
            # Find density_auto_display order and add 0.1
            density_auto_param = next((p for p in filtered_params if p.parameter.name == 'density_auto_display'), None)
            return density_auto_param.order + 0.1 if density_auto_param else base_order
        elif param_name == 'm2':
            # Find density_auto_display order and add 0.2  
            density_auto_param = next((p for p in filtered_params if p.parameter.name == 'density_auto_display'), None)
            return density_auto_param.order + 0.2 if density_auto_param else base_order
        elif param_name == 'density_auto_display':
            # density_auto_display should come first, then m1, then m2
            return base_order
        else:
            return base_order
    
    user_params = sorted(filtered_params, key=get_sort_key)

    # デフォルト行数
    num_can = request.POST.get('num_can', 5)

    # フォームセット作成
    CaneFormSet = modelformset_factory(Reedsdata,
                                       form=Caneform,
                                       extra=int(num_can),
                                       can_delete=False)

    if request.method == "POST" and 'form-TOTAL_FORMS' in request.POST:
        # This is a data submission (has formset management data)
        formset = CaneFormSet(request.POST,
                              queryset=Reedsdata.objects.none(),
                              form_kwargs={'user': request.user, 'mode': 'batch'})
        
        # Custom validation - only validate forms with actual data
        valid_forms = []
        has_errors = False
        reed_ids_in_batch = []  # Track reed_IDs in this batch for uniqueness
        
        for form in formset:
            if form.has_changed():
                # First check if form is valid before accessing cleaned_data
                if form.is_valid():
                    # Check if form has any meaningful data (not just empty strings)
                    non_empty_data = {k: v for k, v in form.cleaned_data.items() 
                                     if v is not None and v != '' and k != 'DELETE'}
                    
                    if len(non_empty_data) > 0:
                        # This form has data, check if it has a Reed ID
                        reed_id = form.cleaned_data.get('reed_ID')
                        
                        if not reed_id or reed_id.strip() == '':
                            # No Reed ID provided - ignore this row (don't save it)
                            print(f"Skipping row without Reed ID (has other data but no Reed ID)")
                            continue
                        else:
                            # Reed ID is provided, check for duplicates within this batch
                            if reed_id in reed_ids_in_batch:
                                has_errors = True
                                print(f"Form error: Duplicate reed_ID '{reed_id}' in batch")
                                form.add_error('reed_ID', f'Reed ID "{reed_id}" must be unique - already used in this batch.')
                            else:
                                reed_ids_in_batch.append(reed_id)
                                valid_forms.append(form)
                else:
                    # Form is invalid but has changes - check if it has Reed ID before treating as error
                    form_data = form.data
                    reed_id_field = None
                    
                    # Find the reed_ID field for this form
                    for field_name in form_data:
                        if field_name.endswith('-reed_ID'):
                            reed_id_field = form_data.get(field_name)
                            break
                    
                    if not reed_id_field or reed_id_field.strip() == '':
                        # No Reed ID, ignore this invalid form
                        print(f"Ignoring invalid form without Reed ID")
                        continue
                    else:
                        # Has Reed ID but form is invalid - this is an error
                        has_errors = True
                        print(f"Form validation errors for Reed ID '{reed_id_field}': {form.errors}")
        
        # Check formset-level errors (but these are less important now)
        if formset.non_form_errors():
            print(f"Formset non-form errors: {formset.non_form_errors()}")
            # Don't treat formset errors as blocking since we're doing custom validation
        
        if not has_errors and len(valid_forms) > 0:
            saved_count = 0
            updated_count = 0
            for form in valid_forms:
                try:
                    instance = form.save(commit=False)
                    reed_id = form.cleaned_data.get('reed_ID')
                    
                    # Check if a reed with this ID already exists for this user
                    existing_reed = Reedsdata.objects.filter(reed_ID=reed_id, reedauthor=request.user).first()
                    
                    if existing_reed:
                        # Update existing reed with new data
                        for field_name, field_value in form.cleaned_data.items():
                            if field_name != 'reed_ID' and field_value is not None and field_value != '':
                                setattr(existing_reed, field_name, field_value)
                        
                        # Auto-calculate density if needed
                        if 'density_auto' in ViewUser(request.user).get_field_list():
                            m1 = form.cleaned_data.get('m1')
                            m2 = form.cleaned_data.get('m2')
                            if m1 is not None and m2 is not None and m2 != 0:
                                try:
                                    existing_reed.density = m1 / (m1 + m2)
                                except (ZeroDivisionError, TypeError):
                                    existing_reed.density = None
                        
                        existing_reed.save()
                        updated_count += 1
                    else:
                        # Create new reed
                        instance.reedauthor = request.user
                        
                        # Auto-calculate density if needed
                        if 'density_auto' in ViewUser(request.user).get_field_list():
                            m1 = form.cleaned_data.get('m1')
                            m2 = form.cleaned_data.get('m2')
                            if m1 is not None and m2 is not None and m2 != 0:
                                try:
                                    instance.density = m1 / (m1 + m2)
                                except (ZeroDivisionError, TypeError):
                                    instance.density = None
                        
                        instance.save()
                        saved_count += 1
                        
                except Exception as e:
                    print(f"Error saving reed {reed_id}: {e}")
                    # Continue with other forms
            
            # Show success message and redirect to reed list
            from django.contrib import messages
            total_count = saved_count + updated_count
            if total_count > 0:
                if saved_count > 0 and updated_count > 0:
                    messages.success(request, f'Successfully created {saved_count} new reed(s) and updated {updated_count} existing reed(s).')
                elif saved_count > 0:
                    messages.success(request, f'Successfully created {saved_count} new reed(s).')
                else:
                    messages.success(request, f'Successfully updated {updated_count} existing reed(s).')
                return redirect('reeds:reedsdata_list')
            else:
                messages.warning(request, 'No data was entered. Please fill in at least one row with data.')
        else:
            # Show validation errors with details
            from django.contrib import messages
            error_details = []
            
            # Collect specific errors from our custom validation
            for i, form in enumerate(formset):
                if form.errors:
                    for field, errors in form.errors.items():
                        for error in errors:
                            error_details.append(f"Row {i+1} - {error}")
            
            if error_details:
                messages.error(request, f'Please fix these errors: {"; ".join(error_details)}')
            else:
                messages.error(request, 'Please check your data and try again.')
    else:
        # This is either GET request or POST request with just num_can (update rows)
        formset = CaneFormSet(queryset=Reedsdata.objects.none(),
                              form_kwargs={'user': request.user, 'mode': 'batch'})

    return render(request, "reedsdata/add_batch.html", {
        "formset": formset,
        "user_params": user_params,
        "num_can": num_can,
    })


from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.db.models import Count, Q
import json


@csrf_exempt
@login_required
def save_parameter_settings(request):
    if request.method == "POST":
        data = json.loads(request.body)
        for item in data:
            try:
                param = Parameter.objects.get(name=item["field"])
                up, _ = UserParameter.objects.get_or_create(user=request.user,
                                                            parameter=param)
                up.active = item["active"]
                up.order = item["order"]
                up.save()
            except Parameter.DoesNotExist:
                continue
        return JsonResponse({"success": True})
    return JsonResponse({"status": "error"}, status=400)


@csrf_exempt
@login_required
def get_reed_data(request):
    """Get reed data by reed_ID or range for populating batch forms"""
    if request.method == "POST":
        data = json.loads(request.body)
        reed_id = data.get('reed_id')
        reed_id_from = data.get('reed_id_from')
        reed_id_to = data.get('reed_id_to')
        reed_ids = data.get('reed_ids')  # For checking existing IDs
        
        try:
            # Check for existing reed IDs (for confirmation dialog)
            if reed_ids:
                existing_ids = []
                for rid in reed_ids:
                    if Reedsdata.objects.filter(reed_ID=rid, reedauthor=request.user).exists():
                        existing_ids.append(rid)
                return JsonResponse({"success": True, "existing_reed_ids": existing_ids})
            
            elif reed_id:
                # Single reed lookup
                reed = Reedsdata.objects.get(reed_ID=reed_id, reedauthor=request.user)
                reed_data = get_reed_field_data(reed)
                return JsonResponse({"success": True, "data": reed_data})
                
            elif reed_id_from and reed_id_to:
                # Range lookup
                reed_ids = generate_reed_id_range(reed_id_from, reed_id_to)
                reeds_data = []
                
                for rid in reed_ids:
                    try:
                        reed = Reedsdata.objects.get(reed_ID=rid, reedauthor=request.user)
                        reed_data = get_reed_field_data(reed)
                        reeds_data.append({"reed_id": rid, "data": reed_data})
                    except Reedsdata.DoesNotExist:
                        reeds_data.append({"reed_id": rid, "data": None, "error": "Not found"})
                
                return JsonResponse({"success": True, "reeds": reeds_data})
                
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})
    
    return JsonResponse({"success": False, "error": "Invalid request"}, status=400)


def get_reed_field_data(reed):
    """Extract field data from a reed object"""
    data = {}
    for field in Reedsdata._meta.fields:
        field_name = field.name
        field_value = getattr(reed, field_name)
        
        # Skip fields that can't be serialized or aren't needed for form population
        if field_name in ['reedauthor', 'id']:
            continue
        
        # Convert to appropriate format for JSON
        if field_value is not None:
            if hasattr(field_value, 'isoformat'):  # DateTime field
                data[field_name] = field_value.isoformat()
            else:
                data[field_name] = field_value
        else:
            data[field_name] = None
    
    # Add calculated density if applicable
    if hasattr(reed, 'density_auto'):
        data['density_auto_display'] = reed.density_auto
    
    return data


def generate_reed_id_range(from_id, to_id):
    """Generate a list of reed IDs from from_id to to_id"""
    import re
    
    # Extract prefix and number from reed IDs
    from_match = re.match(r'([A-Za-z]*)(\d+)', from_id)
    to_match = re.match(r'([A-Za-z]*)(\d+)', to_id)
    
    if not from_match or not to_match:
        raise ValueError("Invalid Reed ID format. Use format like R001, R002, etc.")
    
    from_prefix, from_num = from_match.groups()
    to_prefix, to_num = to_match.groups()
    
    if from_prefix != to_prefix:
        raise ValueError("Reed ID prefixes must match")
    
    from_number = int(from_num)
    to_number = int(to_num)
    num_width = len(from_num)  # Preserve leading zeros
    
    if from_number > to_number:
        raise ValueError("From number must be less than or equal to To number")
    
    reed_ids = []
    for i in range(from_number, to_number + 1):
        reed_id = f"{from_prefix}{str(i).zfill(num_width)}"
        reed_ids.append(reed_id)
    
    return reed_ids


def get_weather_data(request):
    """Get weather data for a given location or coordinates"""
    if request.method == "GET":
        location = request.GET.get('location', '').strip()
        lat = request.GET.get('lat')
        lon = request.GET.get('lon')
        
        if not location and not (lat and lon):
            return JsonResponse({
                "success": False, 
                "error": "Location name or coordinates are required"
            })
        
        try:
            if lat and lon:
                # Use coordinates to get weather data
                from .weather_service import get_weather_for_coordinates
                weather_data = get_weather_for_coordinates(float(lat), float(lon))
            else:
                # Use location name to get weather data
                weather_data = get_location_weather_data(location)
            
            if weather_data.get('error'):
                return JsonResponse({
                    "success": False,
                    "error": weather_data['error']
                })
            
            # Convert Decimal to float for JSON serialization
            for key in ['latitude', 'longitude', 'temperature', 'humidity', 'air_pressure']:
                if weather_data.get(key) is not None:
                    weather_data[key] = float(weather_data[key])
            
            return JsonResponse({
                "success": True,
                "data": weather_data
            })
            
        except Exception as e:
            return JsonResponse({
                "success": False,
                "error": f"Failed to fetch weather data: {str(e)}"
            })
    
    return JsonResponse({
        "success": False,
        "error": "Only GET method allowed"
    })


@login_required
def data_overview(request):
    """Data overview page showing recent reeds and basic statistics"""
    from django.db.models import Count, Avg, Q
    from datetime import datetime, timedelta

    # Get all user's reeds ordered by date (most recent first)
    reeds = Reedsdata.objects.filter(reedauthor=request.user).order_by('-date')

    # Get recent reeds (last 100)
    recent_reeds = reeds[:100]

    # Total reeds count
    total_reeds = reeds.count()

    # Breakdown by instrument
    instrument_stats = Reedsdata.objects.filter(reedauthor=request.user).values('instrument').annotate(
        count=Count('id')
    ).order_by('-count')

    # Breakdown by cane brand
    cane_brand_stats = Reedsdata.objects.filter(reedauthor=request.user).values('cane_brand').annotate(
        count=Count('id')
    ).order_by('-count')

    # Recent activity trends (last 7 days, last 30 days, last 90 days)
    today = timezone.now().date()
    last_7_days = reeds.filter(date__gte=today - timedelta(days=7)).count()
    last_30_days = reeds.filter(date__gte=today - timedelta(days=30)).count()
    last_90_days = reeds.filter(date__gte=today - timedelta(days=90)).count()

    # Average quality metrics (if available)
    quality_metrics = Reedsdata.objects.filter(reedauthor=request.user).aggregate(
        avg_playing_ease=Avg('playing_ease'),
        avg_intonation=Avg('intonation'),
        avg_response=Avg('response'),
        avg_global_quality_first=Avg('global_quality_first_impression'),
    )

    context = {
        'recent_reeds': recent_reeds,
        'total_reeds': total_reeds,
        'instrument_stats': instrument_stats,
        'cane_brand_stats': cane_brand_stats,
        'last_7_days': last_7_days,
        'last_30_days': last_30_days,
        'last_90_days': last_90_days,
        'quality_metrics': quality_metrics,
    }

    return render(request, 'reedsdata/data_overview.html', context)
