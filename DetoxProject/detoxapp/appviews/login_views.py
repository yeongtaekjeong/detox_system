# accounts/views.py
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect

from detoxapp.forms import UserForm
from detoxapp.models import User
from django.contrib.auth.models import Group

def signup(request): 
    if request.method == "POST":
        form = UserForm(request.POST)

        if form.is_valid():
            try:
            # postgre 저장
            #     crud = CRUD()
            #     name = form.cleaned_data.get('name')
            #     username = form.cleaned_data.get('username')
            #     email = form.cleaned_data.get('email')
            #     join_date = str(form.cleaned_data.get('join_date'))
            #
            #     insert_data = "'"+username+"',"+"'"+name+"',"+"'"+email+"',"+"'"+join_date+"'"
            #     crud.insertDB('USER_POSTGRES','user_id, username, email, created_on',insert_data)
            #
            #     state_db_insert = "insert into user_action_state(user_id) values('"+username+"')"
            #     crud.sql_cud(state_db_insert)

            # sqlite3 저장
                form.save()

                username = form.cleaned_data.get('username')
                raw_password = form.cleaned_data.get('password1')
                user = User.objects.get(username=username)
                group = Group.objects.get(id=2)
                user.groups.set([group])
                authenticate(username=username, password=raw_password)  # 사용자 인증
                # login(request, User)

                return render(request,'detoxapp/login.html',context={})
            except Exception as e:
                # review_info = User.objects.get(username=username)
                # review_info.delete()
                print(e)
                return render(request, 'detoxapp/signup.html', {'form':form})
    else:
        form = UserForm()
    return render(request, 'detoxapp/signup.html', {'form':form})


def mypage(request):
    return render(request, 'detoxapp/mypage.html', {})


def delete_user(request, id):
    isadmin = request.user.is_admin
    if not isadmin:
        try:
            # sqlite3 조회
            review_info = User.objects.get(id=id)

            # # postgre 삭제
            # crud = CRUD()
            # sqlcondition = "user_id = '"+ str(review_info.username) + "'"
            # crud.deleteDB(table='USER_POSTGRES', condition=sqlcondition)
            
            # sqlite3 삭제
            review_info.delete()

        except:
            return render(request, 'detoxapp/mypage.html', {})
    else:
        return redirect('/')
    return redirect('/')
