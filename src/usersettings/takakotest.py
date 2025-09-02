data_preference = [
    ('temperature', 'Temperature'),
    ('humidity', 'Humidity'),
    ('cane_brand', 'Cane Brand'),
    ('harvest_year', 'Harvest Year'),
    ('gouging_machine', 'Gounging Machine'),
    ('cane_diamater', 'Diamater'),
    ('thicness', 'Thickness'),
    ('hardness', 'Hardness'),
    ('flexibility', 'Flexibility'),
    ('density', 'Density'),
    ('shaper', 'Shaper'),
]

fields = data_preference
print(type(fields))
for i in fields:
    print(i[0])

#    #####################データベースからのユーザーが選んだパラメーター#########
#    data = Checkbox_for_setting.objects.get(user_id=request.user.pk)
#    data = data.checkboxsetting  #これがユーザー別のusersettingのcheckboxsettingの中身
#    data = data.split()
#    print(data)
#    ####################################################################
