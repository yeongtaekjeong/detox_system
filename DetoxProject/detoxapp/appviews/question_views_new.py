from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.urls import reverse
from detoxapp.models import User
import json
import pandas as pd
from detoxapp.DBConnection.db_sqlalchemy import dbSqlAlchemy
from sqlalchemy.sql import text
from datetime import datetime
import requests

from DetoxProject.system_sever_set import flask_server

def question_info(request, page):

    if page=='home':

        # querytext = "delete from tb_user where user_sq in "\
        #     "(select A.user_sq from public.tb_user A left join public.tb_question B "\
        #     "on A.user_sq = B.user_sq where B.user_sq is null);"
        # crud = CRUD()
        # crud.sql_cud(querytext)
        
        return render(request, 'detoxapp/question_new/question_info.html',{})
    
    elif page=='info':
        
        if request.method=='POST':
            # tb_user = createDataFrame.tb_user()
            user_data = dict(request.POST)
            get_data_df = pd.DataFrame(user_data).iloc[:,1:]

            id_data = str(datetime.today().strftime("%m%d_%H%M%S"))+'_'+str(user_data['user_phone'])[-6:-2]
            get_data_df.insert(0,'user_id',id_data)

            data_df = date_create(get_data_df)
            engine,session = dbSqlAlchemy.get_engine()
            data_df.to_sql(name='tb_user', con=engine, if_exists='append',index=False,schema='public')
            session.commit()


            context = {'age_option':list(range(20,99,1)),'paging':1,'user_id':id_data}
            
            # return render(request, 'detoxapp/question_new/question_content.html', context=context)
            return render(request, 'detoxapp/question_renew/renew_question_content.html', context=context)
    
        else:
            return render(request, 'detoxapp/question_new/question_info.html',{})
        
    elif page=='end':
         if request.method=='POST':
            return render(request, 'detoxapp/question_new/question_end.html',{})

    # elif page=='detox_question':

    #     context = {'age_option':list(range(20,99,1)),'paging':1,'user_id':''}
            
    #     return render(request, 'detoxapp/question_renew/renew_question_content.html',context=context)
    
    else:
        return render(request, 'detoxapp/question_new/question_info.html',{})


# 관련 table : tb_question, tb_digestion, tb_lifestyle, tb_healthlevel, tb_history 저장하는 함수
def question_submit(request, pagenum):
    # numbering = [0,list(range(1,10)),list(range(10,27)),list(range(27,51)),list(range(51,84)),list(range(84,91))]
    if request.method=='POST': 
        # renew question
        # pagenum 6 : tb_question, tb_digestion, tb_lifestyle
        # pagenum 7 : tb_healthlevel, tb_history
        if pagenum==1:
            get_data = dict(request.POST)
            print(get_data)
            get_data_df = pd.DataFrame(get_data).iloc[:,2:]

            tb_question_index = list(get_data_df.columns).index('reason_low')+1
            tb_digestion_index = list(get_data_df.columns).index('indegestion_after')+1
            tb_lifestyle_index = list(get_data_df.columns).index('breath_sort')+1

            tb_question_df = get_data_df.iloc[:,:tb_question_index]
            tb_digestion_df = get_data_df.iloc[:,tb_question_index:tb_digestion_index]
            tb_lifestyle_df = get_data_df.iloc[:,tb_digestion_index:tb_lifestyle_index]

            # tb_question 넣고 question_sq 생성
            savedata = data_save()
            savedata.tb_question_ft(get_data, tb_question_df)
            savedata.tb_digestion_ft(get_data, tb_digestion_df)
            question_sq = savedata.tb_lifestyle_ft(get_data, tb_lifestyle_df)

            # tb_digestion
            context = {'paging':2,'question_sq':question_sq}
            return render(request, 'detoxapp/question_renew/renew_question_content.html', context=context)
        
        elif pagenum==2:
            get_data = dict(request.POST)

            get_data['pmhx'] = str(get_data['pmhx'])
            get_data['medication'] = str(get_data['medication'])
            get_data['health_food'] = str(get_data['health_food'])

            get_data_df = pd.DataFrame(get_data).iloc[:,2:]

            tb_healthlevel_index = list(get_data_df.columns).index('digestion_sour_stomach')+1
            
            tb_healthlevel_df = get_data_df.iloc[:,:tb_healthlevel_index]
            tb_history_df = get_data_df.iloc[:,tb_healthlevel_index:]

            savedata = data_save()
            savedata.tb_healthlevel_ft(get_data, tb_healthlevel_df)
            question_sq = savedata.tb_history_ft(get_data, tb_history_df)

            context = {'question_sq': question_sq}
            return render(request, 'detoxapp/question_new/question_end.html', context=context)

        return render(request, 'detoxapp/question_new/question_content.html', context={})
    
    else:
        return redirect('/question_info/info')


# AI api 통신 함수
def question_result(request, type):

    if request.method=='POST':
        if type=='detox_type':
            table_list = ['tb_question','tb_digestion','tb_lifestyle','tb_healthlevel','tb_history']
            result_list = []

            question_sq = request.POST.get('question_sq')

            engine,session = dbSqlAlchemy.get_engine()
            
            #모든 문진 테이블 데이터 가져오기(리스트 result_list -> 데이터프레임 result_df 변환)
            for tb in table_list:
                try:
                    querytext = text("select * from "+tb+" where question_sq = "+str(question_sq)+" order by create_date desc limit 1;") #
                    result = pd.read_sql_query(querytext, engine)
                except:
                    querytext = text("select * from "+tb+" where question_sq = "+str(question_sq)+"::varchar order by create_date desc limit 1;") #
                    result = pd.read_sql_query(querytext, engine)

                result = result.iloc[:,1:-3]
                result_list.append(result)

            result_df = pd.concat([result_list[0],result_list[1],result_list[2],result_list[3],result_list[4]], axis=1)

            headers = {"Content-Type": "application/json" }
            survey_data = {"survey_title":list(result_df.columns),"survey_data":list(map(str,result_df.iloc[0].values))}
            jsondata = json.dumps(survey_data, ensure_ascii = False)

            url_type = flask_server.survey_server_type
            url_score = flask_server.survey_server_score
            type_urlstate = requests.post(url_type, json=jsondata, headers=headers)
            score_urlstate = requests.post(url_score, json=jsondata, headers=headers)

            if type_urlstate.status_code == 200 and score_urlstate.status_code == 200:
                #해독분류
                type_result = dict(json.loads(type_urlstate.text))

                #해독지수
                score_result = dict(json.loads(score_urlstate.text))

                #db 저장(tb_result_ai 테이블)
                result_col = ['decoding_type','decoding_score']+score_result['score_col']+['question_sq']
                ai_result_df = pd.DataFrame(columns=result_col)
                ai_list = []
                
                engine,session = dbSqlAlchemy.get_engine()
                query_execute = engine.connect()

                 ##AI 결과 df 생성
                for s in score_result['ai_score_data']:
                    ai_list.append(float(s))

                ai_list.insert(0,float(score_result['ai_total_score']))
                ai_list.insert(0,type_result['ai_detox_type'])
                ai_list.append(int(question_sq))
                ai_result_df.loc[0] = ai_list

                try:
                    querytext = text("select * from tb_result_ai where question_sq = "+str(question_sq)+";")
                    search = pd.read_sql_query(querytext, engine)
                except:
                    querytext = text("select * from tb_result_ai where question_sq = "+str(question_sq)+"::varchar;")
                    search = pd.read_sql_query(querytext, engine)

                if search.empty:
                    ai_result_df.to_sql(name='tb_result_ai', con=engine, if_exists='append',index=False, schema='public') #

                 ##전문가 결과 df 생성
                expert_result_df = pd.DataFrame(columns=result_col)
                expert_list = []
                for s in score_result['expert_score_data']:
                    expert_list.append(float(s))
                expert_list.insert(0,float(score_result['expert_total_score']))
                expert_list.insert(0,type_result['expert_detox_type'])
                expert_list.append(int(question_sq))
                expert_result_df.loc[0] = expert_list

                try:
                    querytext = text("select * from tb_result_expert where question_sq = "+str(question_sq)+";")
                    search = pd.read_sql_query(querytext, engine)
                except:
                    querytext = text("select * from tb_result_expert where question_sq = "+str(question_sq)+"::varchar;")
                    search = pd.read_sql_query(querytext, engine)

                if search.empty:
                    expert_result_df.to_sql(name='tb_result_expert', con=engine, if_exists='append',index=False, schema='public') #

                session.commit()

                # AI해독지수 진단 값 * 100
                score_result['ai_score_data'] = list(map(float, score_result['ai_score_data']))
                score_result['ai_total_score'] = str(int(float(score_result['ai_total_score'])*100))
                for i,v in enumerate(score_result['ai_score_data']):
                    score_result['ai_score_data'][i] = int(v*100)

                # 전문가해독지수 진단 값 * 100
                score_result['expert_score_data'] = list(map(float, score_result['expert_score_data']))
                score_result['expert_total_score'] = str(int(float(score_result['expert_total_score'])*100))
                for i,v in enumerate(score_result['expert_score_data']):
                    score_result['expert_score_data'][i] = int(v*100)
                
                context = {'detox_type_result': type_result, 'detox_score_result':score_result }

                return JsonResponse(context)

    return render(request, 'detoxapp/question_new/question_end.html', context={})

#---------------------views 기능 끝----------------------------------

# 데이터프레임에 현재 날짜/시간을 붙여 출력해줌
def date_create(dataframe):
    now_time = datetime.today().strftime("%Y/%m/%d %H:%M:%S")

    df = dataframe.copy()
    df['create_date'] = now_time
    df['update_date'] = now_time

    return df


# 5가지 table에 data 넣는 기능 class
class data_save():

    def tb_question_ft(self, get_data, df_data):
        #post 데이터 문진 내용 부터 가져오기
        get_data = get_data
        get_data_df = df_data
        
        #postgres 연결 및 접속 user에 해당하는 고유 sq 값 조회(tb_user에서 user_sq조회)
        engine,session = dbSqlAlchemy.get_engine()
        query_execute =engine.connect()
        querytext = text("select user_sq from tb_user where user_id = '"+get_data['user_id'][0]+"' order by create_date desc limit 1;") #
        result = query_execute.execute(querytext).all()

        if result != []:
            user_sq = result[0][0] #

            # DB에 insert를 위해 위 정의된 date_create()로 date 및 user_sq 붙여 df 완성
            data_df = date_create(get_data_df)
            data_df['user_sq'] = user_sq #

            # tb_question에 insert 진행
            data_df.to_sql(name='tb_question', con=engine, if_exists='append',index=False, schema='public') #
            session.commit()

            #다음 시작 페이지 및 값 설정 (tb_question에서 user_sq 조회)
            engine,session = dbSqlAlchemy.get_engine()
            query_execute = engine.connect()
            querytext = text("select question_sq from tb_question where user_sq = "+str(user_sq)+";") #
            question_sq = query_execute.execute(querytext).all() #
            session.commit()
        
        return 0


    def tb_digestion_ft(self, get_data, df_data):
        #post 데이터 문진 내용 부터 가져오기
        get_data = get_data
        get_data_df = df_data
        user_id = get_data['user_id'][0]
        
        #postgres 연결 및 접속 sq 값 조회(tb_question에서 question_sq 조회)
        engine,session = dbSqlAlchemy.get_engine()
        query_execute =engine.connect()

        querytext = text(f"""select question_sq from tb_question where user_sq in
                    (select user_sq from tb_user where user_id = '{user_id}') 
                    order by question_sq desc limit 1;""") #
        result = query_execute.execute(querytext).all()
        question_sq = result[0][0]

        if question_sq:
        # DB에 insert를 위해 위 정의된 date_create()로 date 및 user_sq 붙여 df 완성
            data_df = date_create(get_data_df)
            data_df['question_sq'] = question_sq

            try:
                querytext = text("select * from tb_digestion where question_sq = "+str(question_sq)+"::varchar;")
                search = pd.read_sql_query(querytext, engine)
            except:
                querytext = text("select * from tb_digestion where question_sq = "+str(question_sq)+";")
                search = pd.read_sql_query(querytext, engine)

            if search.empty:
                # tb_question에 insert 진행
                data_df.to_sql(name='tb_digestion', con=engine, if_exists='append',index=False, schema='public')

            session.commit()


    def tb_lifestyle_ft(self, get_data, df_data):
        #post 데이터 문진 내용 부터 가져오기
        get_data = get_data
        get_data_df = df_data
        user_id = get_data['user_id'][0]
        
        #postgres 연결 및 접속 sq 값 조회(tb_question에서 question_sq 조회)
        engine,session = dbSqlAlchemy.get_engine()
        query_execute =engine.connect()

        querytext = text(f"""select a.question_sq from tb_digestion a, tb_question b, tb_user c
                        where a.question_sq::varchar = b.question_sq::varchar
                        and c.user_id = '{user_id}'
                        order by a.question_sq desc limit 1;""") #
        result = query_execute.execute(querytext).all()
        question_sq = result[0][0]

        if question_sq:
            # DB에 insert를 위해 위 정의된 date_create()로 date 및 user_sq 붙여 df 완성
            data_df = date_create(get_data_df)
            data_df['question_sq'] = question_sq #

            try:
                querytext = text("select * from tb_lifestyle where question_sq = "+str(question_sq)+"::varchar;")
                search = pd.read_sql_query(querytext, engine)
            except:
                querytext = text("select * from tb_lifestyle where question_sq = "+str(question_sq)+";")
                search = pd.read_sql_query(querytext, engine)

            if search.empty:
                # tb_question에 insert 진행
                data_df.to_sql(name='tb_lifestyle', con=engine, if_exists='append',index=False, schema='public') #

            session.commit()

            return question_sq
        

    def tb_healthlevel_ft(self, get_data, df_data):
    #post 데이터 문진 내용 부터 가져오기
        get_data = get_data
        get_data_df = df_data
        question_sq = get_data['question_sq'][0]

        totaldf = get_data_df.copy()
        totaldf = (totaldf.iloc[:,0:20]).astype('int')
        healthy_total_score = totaldf.sum(axis=1)
        totaldf['healthy_total_score'] = healthy_total_score
        
        sweatdf = get_data_df.iloc[:,20:26]

        digestiondf = get_data_df.copy()
        digestiondf = (digestiondf.iloc[:,26:34]).astype('int')
        digestion_total = digestiondf.sum(axis=1)
        digestiondf['digestion_total'] = digestion_total

        get_data_df = pd.concat([totaldf, sweatdf, digestiondf], axis=1)

        #postgres 연결 및 접속 sq 값 조회(tb_question에서 question_sq 조회)
        engine,session = dbSqlAlchemy.get_engine()
        query_execute = engine.connect()

        if question_sq:
            # DB에 insert를 위해 위 정의된 date_create()로 date 및 user_sq 붙여 df 완성
            data_df = date_create(get_data_df)
            data_df['question_sq'] = question_sq #

            try:
                querytext = text("select * from tb_healthlevel where question_sq = "+str(question_sq)+"::varchar;")
                search = pd.read_sql_query(querytext, engine)
            except:
                querytext = text("select * from tb_healthlevel where question_sq = "+str(question_sq)+";")
                search = pd.read_sql_query(querytext, engine)

            if search.empty:
                # tb_question에 insert 진행
                data_df.to_sql(name='tb_healthlevel', con=engine, if_exists='append',index=False, schema='public') #

            session.commit()

    def tb_history_ft(self, get_data, df_data):
        #post 데이터 문진 내용 부터 가져오기
        get_data = get_data

        get_data['pmhx'] = str(get_data['pmhx'])
        get_data['medication'] = str(get_data['medication'])
        get_data['health_food'] = str(get_data['health_food'])
        
        #불러오기 코드 get_data['pmhx'][1:-1].replace("'","").split(','))

        get_data_df = df_data
        question_sq = get_data['question_sq'][0] #
        
        #postgres 연결 및 접속 sq 값 조회(tb_question에서 question_sq 조회)
        engine,session = dbSqlAlchemy.get_engine()
        query_execute =engine.connect()

        if question_sq:
            # DB에 insert를 위해 위 정의된 date_create()로 date 및 user_sq 붙여 df 완성
            data_df = date_create(get_data_df)
            data_df['question_sq'] = question_sq #

            try:
                querytext = text("select * from tb_history where question_sq = "+str(question_sq)+"::varchar;")
                search = pd.read_sql_query(querytext, engine)
            except:
                querytext = text("select * from tb_history where question_sq = "+str(question_sq)+";")
                search = pd.read_sql_query(querytext, engine)

            if search.empty:
                # tb_question에 insert 진행
                data_df.to_sql(name='tb_history', con=engine, if_exists='append',index=False, schema='public') #

            session.commit()

            return question_sq