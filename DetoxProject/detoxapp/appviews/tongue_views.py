from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from pathlib import Path
from detoxapp.DBConnection.db_sqlalchemy import dbSqlAlchemy
from sqlalchemy.sql import text
import pandas as pd
from operator import itemgetter
import datetime
import requests
import json
import base64

# Create your views here.
def main(request):
    return render(request, 'detoxapp/index.html',{})

def tongue_list(request, page):  
    user_list = []    
    user_list_0 = []
    user_list_1 = []
    user_list_2 = []
    condition_date = ''

    condition_date = str(request.GET.get('selectdate'))

    if condition_date == 'None':
        todaydate = datetime.datetime.today()
        todaydate = todaydate.strftime("%Y-%m-%d")
        condition_date = todaydate

    try:
        engine, session = dbSqlAlchemy.get_engine()
        
        # 문진 번호, 사용자 번호를 통해 문진 완료 고객 뽑기
        querytext = text(f"""select a.*,b.user_gender,b.user_birth,b.question_sq 
                        from tb_user a, tb_question b, tb_result_ai c 
                        where b.question_sq = c.question_sq and a.user_sq = b.user_sq
                        and b.create_date::varchar like '{condition_date}%';""")
        suvey_result = pd.read_sql_query(querytext, engine)

        # 문진 완료 고객 중 설진이 완료된 고객 찾는 쿼리 짜야함
        # 고객 데이터에 'state' 값 변경
        # ---------------------------------------- 
        querytext = """
        select a.question_sq, a.orgn_img_num, b.orgn_img_num
        from tb_orgn_tongue a, tb_tongue_label b
        where a.orgn_img_num = b.orgn_img_num
        and a.question_sq in (select q.question_sq 
            from tb_user u, tb_question q, tb_result_ai r
            where q.question_sq = r.question_sq and u.user_sq = q.user_sq);
        """
        tongue_result = pd.read_sql_query(text(querytext), engine)

        querytext = """
        select question_sq
        from tb_medicine_expert
        where question_sq in (select a.question_sq
            from tb_orgn_tongue a, tb_tongue_label b
            where a.orgn_img_num = b.orgn_img_num
            and a.question_sq in (select q.question_sq 
                from tb_user u, tb_question q, tb_result_ai r
                where q.question_sq = r.question_sq and u.user_sq = q.user_sq));
        """
        complete_result = pd.read_sql_query(text(querytext), engine)

        for i in range(0,len(suvey_result)):
            dictuser = dict(suvey_result.loc[i])
            dictuser['state'] = 1

            if suvey_result.loc[i]['question_sq'] in list(tongue_result['question_sq']):   
                if suvey_result.loc[i]['question_sq'] in list(complete_result['question_sq']):
                    dictuser['state'] = 0
                    user_list_0.append(dictuser)
                else:
                    dictuser['state'] = 2
                    user_list_2.append(dictuser)
                    user_list.append(dictuser)
            else:
                user_list_1.append(dictuser)
                user_list.append(dictuser)

            

    
    except:
        return redirect('/')

    if page == 'tongue':
        user_list = sorted(user_list, key=itemgetter('state'),reverse=True)
    elif page == 'prescription':
        user_list = sorted(user_list,key=itemgetter('state'))
    else:
        return render(request, 'detoxapp/index.html',{})

    context = {'user_info':user_list, 'user_info_0':user_list_0,
               'user_info_1':len(user_list_1), 'user_info_2':len(user_list_2),
               'pageinfo':page, 'condition_date':condition_date}

    return render(request, 'detoxapp/tongue/tongue_list.html',context=context)