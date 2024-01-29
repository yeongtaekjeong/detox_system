from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
import json
from detoxapp.DBConnection.db_sqlalchemy import dbSqlAlchemy
from sqlalchemy.sql import text
from datetime import datetime
import pandas as pd
import requests
from DetoxProject.system_sever_set import flask_server

def prescription(request):

    # if request.method == 'POST':
    userinfo = dict(request.POST)
    user_sq = userinfo['user_sq'][0]
    question_sq = userinfo['question_sq'][0]
    
    engine,session = dbSqlAlchemy.get_engine()
    query_execute = engine.connect()


    # 처방ai(flask)
    headers = {"Content-Type": "application/json" }
    question_sq_data = {'question_sq':question_sq}
    jsondata = json.dumps(question_sq_data, ensure_ascii = False)

    #Flask 주소---------(local)
    url_prescription = flask_server.prescription_server
    prescription_data = requests.post(url_prescription, json=jsondata, headers=headers)

    try:
        prescription_result = eval(prescription_data.text)
    except:
        prescription_result = prescription_data.text
    

    # 1번 : tb_user, tb_question, tb_history, 설진
    first_tab = []
    querytext = text("select u.*, q.*, h.* "+
                    "from tb_user u,tb_question q, tb_history h "+
                    "where u.user_sq = "+user_sq+" and q.question_sq = "+question_sq+" "+
                    "and u.user_sq = q.user_sq " +
                    "and q.question_sq::varchar = h.question_sq;") #
    result_1_survey = pd.read_sql_query(querytext, engine) #
    result_1_survey_pre = result_1_survey.iloc[:,:10]
    result_1_survey_post = (result_1_survey.iloc[:,10:]).drop(['create_date','update_date','question_sq','user_sq'],axis=1)
    result_1_survey = pd.concat([result_1_survey_pre,result_1_survey_post], axis=1)

    querytext = text("select s.file_path, s.file_name, l.*, o.date_taken, o.file_extns " +
                    "from tb_user u,tb_orgn_tongue o, tb_segmented_tongue s, tb_tongue_label l "+
                    "where u.user_sq = "+user_sq+" and o.question_sq = "+question_sq+" "+
                    "and o.orgn_img_num = s.orgn_img_num "+ 
                    "and o.orgn_img_num = l.orgn_img_num;") #
    result_1_tongue = pd.read_sql_query(querytext, engine) #
    result_1 = pd.concat([result_1_survey,result_1_tongue], axis=1)
    
    first_tab = dict(result_1.loc[0])   
    
    # 2번 : tb_user, tb_question, tb_digestion, tb_lifestyle, tb_healtylevel
    second_tab = {}
    querytext = text("select u.*,q.user_gender,q.user_birth,d.*,l.*,h.* "+
                "from tb_user u, tb_question q, tb_digestion d, tb_lifestyle l, tb_healthlevel h "+
	            "where (u.user_sq = "+user_sq+" and q.user_sq = "+user_sq+") "+
                "and (q.question_sq = "+question_sq+") "+
	            "and (q.question_sq = d.question_sq) "+
	            "and (q.question_sq = l.question_sq) "+
	            "and (q.question_sq = h.question_sq);")
    result_2 = pd.read_sql_query(querytext, engine) #
    result_2_pre = result_2.iloc[:,:10]
    result_2_post = (result_2.iloc[:,10:]).drop(['create_date','update_date','question_sq'],axis=1)
    result_2 = pd.concat([result_2_pre, result_2_post], axis=1)
    
    second_tab = dict(result_2.loc[0])

    # 3번 : tb_user, tb_question, tb_result_ai
    third_tab = {}
    querytext = text("select u.*, q.user_gender,q.user_birth, r.* from tb_user u, tb_question q, tb_result_ai r "+
                    "where (u.user_sq = "+user_sq+" and q.user_sq = "+user_sq+")" +
                    "and (q.question_sq = "+question_sq+" and r.question_sq = "+question_sq+");")

    result_3 = pd.read_sql_query(querytext, engine) #
    third_tab = dict(result_3.loc[0])
    session.commit()

    context = {'first_tab':first_tab,'second_tab':second_tab, 'third_tab':third_tab, 'prescription_result':prescription_result}

    return render(request, 'detoxapp/prescription/prescription_result.html', context=context)

def prescription_result(request):
    tabno = 0
    if request.method == 'POST':
        tabno = request.POST.get('no')

        tabval = {"tabno":tabno}

        return JsonResponse(tabval)
    else:
        return render(request, 'detoxapp/prescription/prescription_result.html', {})
    

def prescription_save(request):
    expert = request.POST.get('expert')
    question_sq = request.POST.get('question_sq')
    question_sq = int(float(question_sq))

    col_ko = ['청일수', '청이장', '청삼혈', '청사심', '청오식', '청육행', '청칠위', '청팔보', '청구력', '청시원']
    col = ['medi_one','medi_two','medi_three','medi_four','medi_five','medi_six','medi_seven','medi_eight','medi_nine','medi_ten','life_style','question_sq']
    expertdata = pd.DataFrame(columns=col)

    value = []

    for i in list(range(10)):
        if col_ko[i] in expert:
            value.append(1)
        else:
            value.append(0)
    value.append('')
    value.append(question_sq)
    
    expertdata.loc[0] = value

    engine,session = dbSqlAlchemy.get_engine()
    query_execute = engine.connect()

    querytext = text(f"select * from tb_medicine_expert where question_sq = '{question_sq}' limit 1;") #
    result = query_execute.execute(querytext).all()

    if result == []:
        expertdata.to_sql(name='tb_medicine_expert', con=engine, if_exists='append',index=False, schema='public') #
        session.commit()

    return redirect('/')