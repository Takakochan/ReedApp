from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView
from django.contrib.auth.decorators import login_required
import pandas as pd
from .models import Reedsdata, UserParameter, Parameter, PinnedReed
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


INSTRUMENT_PREFIX = {
    'oboe': 'O', 'english_horn': 'E', 'oboe_damore': 'A',
    'bassoon': 'B', 'contrabassoon': 'C',
}
PERIOD_PREFIX = {'modern': 'M', 'classical': 'C', 'baroque': 'B'}


def get_next_reed_number(prefix, user):
    """Find the highest existing number for this prefix and return next."""
    import re
    pattern = re.compile(r'^' + re.escape(prefix) + r'(\d+)$')
    existing = Reedsdata.objects.filter(
        reedauthor=user, reed_ID__startswith=prefix
    ).values_list('reed_ID', flat=True)
    max_num = 0
    for rid in existing:
        m = pattern.match(rid)
        if m:
            max_num = max(max_num, int(m.group(1)))
    return max_num + 1


def get_next_numbers_by_prefix(user):
    """Return a dict of prefix → next_number for all known prefixes."""
    result = {}
    for instrument, ip in INSTRUMENT_PREFIX.items():
        for period, pp in PERIOD_PREFIX.items():
            prefix = pp + ip
            result[prefix] = get_next_reed_number(prefix, user)
    return result


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
        'next_numbers': json.dumps(get_next_numbers_by_prefix(request.user)),
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
    pinned_ids = set(PinnedReed.objects.filter(user=request.user).values_list('reed_id', flat=True))
    return render(request, 'reedsdata/reedsdata_list.html', {'reeds': reeds, 'pinned_ids': pinned_ids})


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


@login_required
def add_batch(request):
    from django.contrib import messages
    from .templatetags.custom_filters import is_evaluation_field

    # Fields that are "common" (set once for all reeds)
    COMMON_FIELDS = ['instrument', 'period', 'cane_brand', 'gouging_machine',
                     'shaper', 'shaper_model', 'staple_model']

    # Get user's per-reed measurement fields from their settings
    field_list_str = ViewUser(request.user).get_field_list()
    selected_fields = [f.strip() for f in field_list_str.split(',') if f.strip()] if field_list_str else []
    # Expand density_auto → m1, m2
    per_reed_fields = []
    for f in selected_fields:
        if f in COMMON_FIELDS or f in ['reed_ID', 'instrument', 'period']:
            continue
        if f == 'density_auto':
            per_reed_fields.extend(['m1', 'm2'])
        else:
            per_reed_fields.append(f)
    # Add evaluation fields
    user_params_all = UserParameter.objects.filter(user=request.user).select_related('parameter')
    for up in user_params_all:
        if is_evaluation_field(up.parameter.name) and up.parameter.name not in per_reed_fields:
            per_reed_fields.append(up.parameter.name)

    def generate_prefix(instrument, period):
        i = INSTRUMENT_PREFIX.get(instrument, '')
        p = PERIOD_PREFIX.get(period, '')
        return p + i

    if request.method == 'POST' and request.POST.get('action') == 'save_common':
        # Step 1 submitted — save to session and redirect back (GET)
        for f in COMMON_FIELDS:
            request.session[f'batch_{f}'] = request.POST.get(f, '')
        # Auto-generate prefix from instrument + period
        instrument = request.POST.get('instrument', '')
        period = request.POST.get('period', '')
        auto_prefix = generate_prefix(instrument, period)
        request.session['batch_prefix'] = auto_prefix
        request.session['batch_next_num'] = get_next_reed_number(auto_prefix, request.user)
        request.session['batch_num'] = request.POST.get('num_reeds', '5')
        return redirect('reeds:add_batch')

    elif request.method == 'POST' and request.POST.get('action') == 'save_reeds':
        # Step 2 submitted — save reeds
        num = int(request.POST.get('num_reeds', 0))
        common = {f: request.session.get(f'batch_{f}', '') for f in COMMON_FIELDS}
        saved, skipped, errors = 0, 0, []

        for i in range(num):
            reed_id = request.POST.get(f'reed_id_{i}', '').strip()
            if not reed_id:
                skipped += 1
                continue
            try:
                obj, created = Reedsdata.objects.get_or_create(
                    reed_ID=reed_id, reedauthor=request.user
                )
                # Apply common values
                for f, v in common.items():
                    if v:
                        setattr(obj, f, v)
                # Apply per-reed values
                for f in per_reed_fields:
                    val = request.POST.get(f'{f}_{i}', '').strip()
                    if val:
                        # Convert numeric fields
                        field_obj = Reedsdata._meta.get_field(f)
                        if field_obj.get_internal_type() in ('FloatField', 'IntegerField'):
                            try:
                                val = float(val) if field_obj.get_internal_type() == 'FloatField' else int(val)
                            except ValueError:
                                continue
                        setattr(obj, f, val)
                # Auto density
                m1 = request.POST.get(f'm1_{i}', '')
                m2 = request.POST.get(f'm2_{i}', '')
                if m1 and m2:
                    try:
                        obj.density = float(m1) / (float(m1) + float(m2))
                    except (ValueError, ZeroDivisionError):
                        pass
                obj.save()
                saved += 1
            except Exception as e:
                errors.append(f'Row {i+1}: {e}')

        if errors:
            messages.error(request, 'Some rows had errors: ' + '; '.join(errors))
        if saved:
            messages.success(request, f'Successfully saved {saved} reed(s).' + (f' {skipped} empty rows skipped.' if skipped else ''))
            return redirect('reeds:reedsdata_list')
        else:
            messages.warning(request, 'No reeds were saved. Please fill in at least one Reed ID.')

    # GET (or failed POST) — render page
    # Load session values for Step 1
    common_vals = {f: request.session.get(f'batch_{f}', '') for f in COMMON_FIELDS}
    prefix = request.session.get('batch_prefix', '')
    next_num = request.session.get('batch_next_num', 1)
    num_reeds = int(request.session.get('batch_num', 5))

    # Get field labels for per-reed fields
    param_labels = {}
    for up in user_params_all:
        param_labels[up.parameter.name] = up.parameter.display_name
    param_labels['m1'] = 'Dry Mass'
    param_labels['m2'] = 'Wet Mass'

    instrument_choices = [
        ('', '---------'),
        ('Oboe Family', [('oboe', 'Oboe'), ('english_horn', 'English Horn'), ('oboe_damore', "Oboe d'Amore")]),
        ('Bassoon Family', [('bassoon', 'Bassoon'), ('contrabassoon', 'Contrabassoon')]),
    ]
    period_choices = [('', '---------'), ('modern', 'Modern'), ('classical', 'Classical'), ('baroque', 'Baroque')]

    return render(request, 'reedsdata/add_batch.html', {
        'common_vals': common_vals,
        'common_fields': COMMON_FIELDS,
        'per_reed_fields': per_reed_fields,
        'param_labels': param_labels,
        'prefix': prefix,
        'next_num': next_num,
        'num_reeds': num_reeds,
        'instrument_choices': instrument_choices,
        'period_choices': period_choices,
        'cane_brand_choices': Reedsdata.CANE_BRAND_CHOICES,
        'gouging_machine_choices': Reedsdata.GOUGING_MACHINE_CHOICES,
        'shaper_choices': Reedsdata.SHAPER_CHOICES,
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
@require_reed_owner
def quick_evaluate(request, pk):
    """AJAX endpoint for quick evaluation of a reed from the list page."""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'POST required'}, status=405)

    ALLOWED_FIELDS = {
        'playing_ease', 'intonation', 'tone_color', 'response',
        'global_quality_first_impression', 'global_quality_second_impression',
        'global_quality_third_impression',
        'counts_rehearsal', 'counts_concert', 'note',
    }
    INTEGER_FIELDS = {
        'playing_ease', 'intonation', 'tone_color', 'response',
        'global_quality_first_impression', 'global_quality_second_impression',
        'global_quality_third_impression',
        'counts_rehearsal', 'counts_concert',
    }

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)

    reed = get_object_or_404(Reedsdata, pk=pk, reedauthor=request.user)

    for field, value in data.items():
        if field not in ALLOWED_FIELDS:
            continue
        if value == '' or value is None:
            setattr(reed, field, None)
        elif field in INTEGER_FIELDS:
            try:
                int_val = int(value)
                if field in {'playing_ease', 'intonation', 'tone_color', 'response',
                             'global_quality_first_impression', 'global_quality_second_impression',
                             'global_quality_third_impression'}:
                    if not (0 <= int_val <= 10):
                        return JsonResponse({'success': False, 'error': f'{field} must be between 0 and 10'}, status=400)
                setattr(reed, field, int_val)
            except (ValueError, TypeError):
                return JsonResponse({'success': False, 'error': f'Invalid value for {field}'}, status=400)
        else:
            # TextField (note)
            setattr(reed, field, str(value)[:45])

    reed.save()
    return JsonResponse({'success': True})


@login_required
def toggle_pin(request, pk):
    """Toggle pinned status for a reed. Returns JSON {pinned: bool}."""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    reed = get_object_or_404(Reedsdata, pk=pk, reedauthor=request.user)
    pin, created = PinnedReed.objects.get_or_create(user=request.user, reed=reed)
    if not created:
        pin.delete()
        return JsonResponse({'pinned': False})
    return JsonResponse({'pinned': True})


EVALUATION_FIELDS = [
    'stiffness', 'playing_ease', 'intonation', 'tone_color', 'response',
    'global_quality_first_impression', 'global_quality_second_impression',
    'global_quality_third_impression',
    'counts_rehearsal', 'counts_concert',
    'location', 'temperature', 'humidity', 'air_pressure', 'weather_description',
    'chamber_temperature', 'chamber_humidity',
    'note',
]

INTEGER_EVAL_FIELDS = {
    'stiffness', 'playing_ease', 'intonation', 'tone_color', 'response',
    'global_quality_first_impression', 'global_quality_second_impression',
    'global_quality_third_impression',
    'counts_rehearsal', 'counts_concert',
}

FLOAT_EVAL_FIELDS = {
    'temperature', 'humidity', 'air_pressure', 'chamber_temperature', 'chamber_humidity',
}


@login_required
def evaluate_list(request):
    """Card view for evaluating multiple reeds at once."""
    tab = request.GET.get('tab', 'recent')
    all_reeds = Reedsdata.objects.filter(reedauthor=request.user).order_by('-date')
    pinned_ids = set(PinnedReed.objects.filter(user=request.user).values_list('reed_id', flat=True))

    if tab == 'selected':
        reeds = all_reeds.filter(pk__in=pinned_ids)
    else:
        reeds = all_reeds[:6]

    if request.method == 'POST':
        from django.contrib import messages
        saved, errors = 0, []

        # Card fields submitted per reed (excluding global_quality which is handled separately)
        CARD_FIELDS = [
            'stiffness', 'playing_ease', 'intonation', 'tone_color', 'response',
            'counts_rehearsal', 'counts_concert', 'note',
        ]
        INT_CARD_FIELDS = {'stiffness', 'playing_ease', 'intonation', 'tone_color', 'response',
                           'counts_rehearsal', 'counts_concert'}

        for reed in all_reeds:
            pk = str(reed.pk)
            gq_raw = request.POST.get(f'global_quality_{pk}', '').strip()
            card_vals = {f: request.POST.get(f'{f}_{pk}', '').strip() for f in CARD_FIELDS}
            if not gq_raw and not any(card_vals.values()):
                continue

            changed = False

            # Global Quality → assign to next available impression slot
            if gq_raw:
                try:
                    gq_val = int(gq_raw)
                    if not (0 <= gq_val <= 10):
                        errors.append(f'{reed.reed_ID}: Global Quality must be 0–10')
                    else:
                        if reed.global_quality_first_impression is None:
                            reed.global_quality_first_impression = gq_val
                        elif reed.global_quality_second_impression is None:
                            reed.global_quality_second_impression = gq_val
                        else:
                            reed.global_quality_third_impression = gq_val
                        changed = True
                except ValueError:
                    errors.append(f'{reed.reed_ID}: invalid Global Quality value')

            # Other card fields
            for field, raw in card_vals.items():
                if not raw:
                    continue
                if field in INT_CARD_FIELDS:
                    try:
                        val = int(raw)
                        if field in {'stiffness', 'playing_ease', 'intonation', 'tone_color', 'response'}:
                            if not (0 <= val <= 10):
                                errors.append(f'{reed.reed_ID} {field}: must be 0–10')
                                continue
                        setattr(reed, field, val)
                        changed = True
                    except ValueError:
                        errors.append(f'{reed.reed_ID} {field}: invalid number')
                else:
                    setattr(reed, field, raw[:45])
                    changed = True

            if changed:
                try:
                    reed.save()
                    saved += 1
                except Exception as e:
                    errors.append(f'{reed.reed_ID}: {e}')

        if errors:
            messages.error(request, 'Some errors: ' + '; '.join(errors))
        if saved:
            messages.success(request, f'Saved {saved} reed(s).')
        return redirect('reeds:evaluate_list')

    playing_fields = [
        ('stiffness', 'Stiffness'),
        ('playing_ease', 'Playing Ease'),
        ('intonation', 'Intonation'),
        ('tone_color', 'Tone Color'),
        ('response', 'Response'),
    ]

    return render(request, 'reedsdata/evaluate_list.html', {
        'reeds': reeds,
        'playing_fields': playing_fields,
        'tab': tab,
        'pinned_ids': pinned_ids,
    })


@login_required
@require_reed_owner
def evaluate_detail(request, pk):
    """Single reed evaluation page."""
    reed = get_object_or_404(Reedsdata, pk=pk, reedauthor=request.user)
    reeds_qs = Reedsdata.objects.filter(reedauthor=request.user).order_by('-date')
    pks = list(reeds_qs.values_list('pk', flat=True))
    idx = pks.index(pk) if pk in pks else None
    prev_pk = pks[idx + 1] if idx is not None and idx + 1 < len(pks) else None
    next_pk = pks[idx - 1] if idx is not None and idx > 0 else None

    if request.method == 'POST':
        for field in EVALUATION_FIELDS:
            raw = request.POST.get(field, '').strip()
            if raw == '':
                setattr(reed, field, None)
                continue
            if field in INTEGER_EVAL_FIELDS:
                try:
                    setattr(reed, field, int(raw))
                except ValueError:
                    pass
            elif field in FLOAT_EVAL_FIELDS:
                try:
                    setattr(reed, field, float(raw))
                except ValueError:
                    pass
            else:
                setattr(reed, field, raw[:100])
        reed.save()
        if next_pk:
            return redirect('reeds:evaluate_detail', pk=next_pk)
        return redirect('reeds:evaluate_list')

    playing_fields = [
        ('stiffness', 'Stiffness'),
        ('playing_ease', 'Playing Ease'),
        ('intonation', 'Intonation'),
        ('tone_color', 'Tone Color'),
        ('response', 'Response'),
    ]
    global_fields = [
        ('global_quality_first_impression', '1st Impression'),
        ('global_quality_second_impression', '2nd Impression'),
        ('global_quality_third_impression', '3rd Impression'),
    ]

    return render(request, 'reedsdata/evaluate_detail.html', {
        'reed': reed,
        'prev_pk': prev_pk,
        'next_pk': next_pk,
        'playing_fields': playing_fields,
        'global_fields': global_fields,
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
