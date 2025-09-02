from django.shortcuts import render, redirect
from .models import Checkbox_for_setting

from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User


def land_demand_form(request):
    if request.method == 'POST':
        if request.POST.get('checkboxsetting'):
            data = {"checkboxsetting": request.POST.get('checkboxsetting')}
            Checkbox_for_setting.objects.filter(
                user_id=request.user.pk).update(**data)

            return render(request, 'usersettings/top.html')
    else:
        return render(request, 'usersettings/top.html')


#こっちは更新でなく、新しくデーター作成する方
#def land_demand_form(request):
#
#    if request.method == 'POST':
#        #data = Checkbox_for_setting.objects.all().values()
#        #id = request.user.id
#        #print(data)
#        #print
#        if request.POST.get('checkboxsetting'):
#            savedata = Checkbox_for_setting()
#            savedata.checkboxsetting = request.POST.get('checkboxsetting')
#            savedata.user = request.user
#            savedata.save()
#
#            return render(request, 'usersettings/top.html')
#    else:
#        return render(request, 'usersettings/top.html')
#