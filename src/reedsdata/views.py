from django.shortcuts import render
from .models import Reedsdata
import pandas as pd
from .forms import Caneform, ViewUser
from usersettings.models import Checkbox_for_setting
from django.views.generic import ListView
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required


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
def data_entry(request):
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
def edit_reedsdata(request, pk):
    instance = get_object_or_404(Reedsdata, pk=pk, reedauthor=request.user)

    # Get next and previous objects for the same user
    next_obj = Reedsdata.objects.filter(reedauthor=request.user, pk__gt=pk).order_by('pk').first()
    prev_obj = Reedsdata.objects.filter(reedauthor=request.user, pk__lt=pk).order_by('-pk').first()

    if request.method == 'POST':
        form = Caneform(request.POST, instance=instance, user=request.user, mode='edit')
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
            obj.save()
            return redirect('reeds:reedsdata_list')
    else:
        form = Caneform(instance=instance, user=request.user, mode='edit')

    return render(request, 'reedsdata/edit_reedsdata.html', {
        'form': form,
        'next_obj': next_obj,
        'prev_obj': prev_obj,
    })


@login_required
def delete_reedsdata(request, pk):
    instance = get_object_or_404(Reedsdata, pk=pk, reedauthor=request.user)
    if request.method == 'POST':
        instance.delete()
        return redirect('reedsdata_list')
    return render(request, 'reedsdata/confirm_delete.html',
                  {'object': instance})
