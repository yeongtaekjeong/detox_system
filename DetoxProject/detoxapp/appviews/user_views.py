# accounts/views.py
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from detoxapp.models import User
from django.contrib.auth.models import Group, Permission
from django.contrib.auth.decorators import login_required, permission_required
from django.http import JsonResponse
from datetime import datetime, date
import json
import re

#######################################################################################################################
# 1. MethodName : [1]user
# 2. Comment    : 계정 관리 페이지 접근 (Post 접근시 계정 삭제)
# 3. 작성자      : 전준영
# 4. 작성일      : 2023. 08. 07.
#######################################################################################################################
# @permission_required('view_user_manage')
def user(request):
    if request.method == "GET":
        # 등록된 관리자계정 모두 가져오기
        users = User.objects.all()
        groups_list = Group.objects.all()
        permissions = []

        for g in groups_list:
            dict = {
            'id': g.id,
            'name': g.name,
            'permission': {}
            }
            dict['permission']['view_user_manage'] = g.permissions.filter(codename='view_user_manage').count()
            dict['permission']['view_question_manage'] = g.permissions.filter(codename='view_question_manage').count()
            permissions.append(dict)

        return render(request, 'detoxapp/user.html', {
            'curr': datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S'),
            'users': users,
            'groups': groups_list,
            'permissions': permissions,
        })
    if request.method == "POST":  # 계정삭제
        try:
            username = request.user.username
            userid = request.POST.get("Check")
            userpwd = request.POST.get("CheckPwd")
            user = User.objects.get(id=userid)
            req_user = User.objects.get(username=username)


            check = req_user.check_password(userpwd)
        except Exception as e:
            print(e)
            return render(request, 'detoxapp/alert.html', {
                'msg': '알 수 없는 에러 발생',
                'link': '/user',
            })
        if check:
            user.delete()
        else:
            return render(request, 'detoxapp/alert.html', {
                'msg': '잘못된 비밀번호 입니다.',
                'link': '/user',
            })

        return render(request, 'detoxapp/alert.html', {'msg': '계정이 삭제되었습니다.', 'link': '/user'})


#######################################################################################################################
# 1. MethodName : [2]changeAuthActiveAjax
# 2. Comment    : 계정 활성 상태 변경
# 3. 작성자      : 전준영
# 4. 작성일      : 2023. 08. 07.
#######################################################################################################################
@login_required
def changeAuthActiveAjax(request):
    if request.method == 'GET': return render(request, '404.html')
    if request.method == 'POST':
        try:
            result = json.loads(request.body)
            id = result['id']
            user = User.objects.get(id=id)
        except (ZeroDivisionError, Exception) as e:
            return JsonResponse({'statusCode': 404, 'msg': 'None', 'link': '404'})
        res = {
            "su": 1,
            "curr": datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S'),
        }

        if (user.is_active == True):
            user.is_active = False
            user.save()
            res['msg'] = user.username + " 계정을 비활성화 하였습니다."
        else:
            user.is_active = True
            user.save()
            res['msg'] = user.username + " 계정을 활성화 하였습니다."
        return JsonResponse(res)


#######################################################################################################################
# 1. MethodName : [4]changeAuthGroupAjax
# 2. Comment    : 계정 권한 변경
# 3. 작성자      : 전준영
# 4. 작성일      : 2022. 12. 14.
#######################################################################################################################
@login_required
def changeAuthGroupAjax(request):
    if request.method == 'GET': return render(request, '404.html')
    if request.method == 'POST':
        try:
            result = json.loads(request.body)
            id = result['id']
            groupid = result['groupid']
            user = User.objects.get(id=id)
            group = Group.objects.get(id=groupid)
        except (ZeroDivisionError, Exception) as e:
            return JsonResponse({'statusCode': 404, 'msg': 'None', 'link': '404'})

        res = {
            "su": 1,
            "curr": datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S'),
        }
        try:
            user.groups.set([group])
            res['msg'] = user.username + " 계정의 권한을 변경 하였습니다."
            res['groupname'] = group.name
            return JsonResponse(res)
        except (ZeroDivisionError, Exception) as e:
            return JsonResponse({"su": 0, "msg": "알 수 없는 오류 발생"})

#######################################################################################################################
# 1. MethodName : [5]changeGroupPermissionAjax
# 2. Comment    : 그룹 권한 수정
# 3. 작성자      : 전준영
# 4. 작성일      : 2022. 12. 14.
#######################################################################################################################
@login_required
def changeGroupPermissionAjax(request):
    if request.method == 'GET': return render(request, '404.html')
    if request.method == 'POST':
        result = json.loads(request.body)
        id = result['id']
        permission = result['permission']
        group = Group.objects.get(id=id)
        get_permission = Permission.objects.get(codename=permission)
        check_permission = group.permissions.filter(codename=permission).count()

        res = {
            "su": 1,
            "curr": datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S'),
        }

        try:
            if check_permission == 0:
                group.permissions.add(get_permission)
            else:
                group.permissions.remove(get_permission)
            return JsonResponse(res)
        except (ZeroDivisionError, Exception) as e:
            return JsonResponse({'statusCode': 404, 'msg': 'None', 'link': '500'})

#######################################################################################################################
# 1. MethodName : [6]addDeleteGroup
# 2. Comment    : 그룹 추가/삭제
# 3. 작성자      : 전준영
# 4. 작성일      : 2022. 12. 15.
#######################################################################################################################
@login_required
def addDeleteGroup(request):
    if request.method == 'POST' and request.POST.get("groupname") != None:
        try:
            groupname = request.POST.get("groupname")
            group_count = Group.objects.all().count()
            if group_count > 10:
                return render(request, 'detoxapp/alert.html', {'msg': '권한을 더 이상 생성할 수 없습니다.\n'
                                                             '다른 권한을 삭제하고 다시 시도하시거나, 관리자에게 문의해주세요.',
                                                      'link': '/user'})
            g = Group(name=groupname)
            g.save()
        except (ZeroDivisionError, Exception) as e:
            return render(request, '404.html')
        return render(request, 'detoxapp/alert.html', {'msg': '권한을 생성하였습니다.', 'link': '/user'})

    if request.method == 'POST' and request.POST.get("groupid") != None:
        try:
            groupid = request.POST.get("groupid")
            g = Group.objects.get(id=groupid)
            u = User.objects.all()
            for user in u:
                if user.groups.filter(id=groupid):
                    user.is_active = False
                    user.save()
            g.delete()
        except (ZeroDivisionError, Exception) as e:
            return render(request, '404.html')
        return render(request, 'detoxapp/alert.html', {'msg': '권한을 삭제하였습니다.', 'link': '/user'})

#######################################################################################################################
# 1. MethodName : [7]actAuthPasswordChangeAjax
# 2. Comment    : 계정 패스워드 변경
# 3. 작성자      : 전준영
# 4. 작성일      : 2023. 1. 5.
#######################################################################################################################
def actAuthPasswordChangeAjax(request):
    if request.method == 'GET': return render(request, '404.html')
    if request.method == 'POST':
        result = json.loads(request.body)
        username = result['username']
        password = result['password']
        bf_password = result['bf_password']
        res = {
            "su": 1,
        }
        try:
            user = User.objects.get(username=username)
            check = user.check_password(bf_password)
            if check:
                user.set_password(password)
                user.save()
                res['msg'] = user.username + " 계정의 패스워드를 변경 하였습니다."
            else:
                res['msg'] = "잘못된 패스워드 입니다."
            return JsonResponse(res)
        except (ZeroDivisionError, Exception) as e:
            return JsonResponse({"su": 0, "msg": "알 수 없는 오류 발생"})

#######################################################################################################################
# 1. MethodName : [8]actAuthPasswordCheckAjax
# 2. Comment    : 계정 확인 Ajax
# 3. 작성자      : 전준영
# 4. 작성일      : 2023. 6. 12.
#######################################################################################################################
def actAuthPasswordCheckAjax(request):
    if request.method == 'GET': return render(request, '404.html')
    if request.method == 'POST':
        result = json.loads(request.body)
        username = result['username']
        password = result['password']

        res = {
            "su": 1,
        }
        try:
            user = User.objects.get(username=username)
            check = user.check_password(password)
            res['check'] = check
            return JsonResponse(res)
        except (ZeroDivisionError, Exception) as e:
            return JsonResponse({"su": 0, "msg": "알 수 없는 오류 발생"})


def alert(request):
    try:
        msg = request.GET['msg']
        link = request.GET['link']
    except (ZeroDivisionError, Exception) as e:
        return render(request, '404.html')

    if link == "404": return render(request, '404.html')
    if link == "500": return render(request, '500.html')
    return render(request, 'alert.html',{
            'msg': msg,
            'link': link
    })