from flask import request, Response
from flask_restx import Resource, Namespace, fields

import requests
import random
import json
import re
import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow.keras.metrics import BinaryAccuracy 
from sklearn.metrics import f1_score

import os
import psycopg2

from tqdm import tqdm
tqdm.pandas()

Todo3 = Namespace('flask_medicine', description='FLASK MEDICINE')

############################ model ###################################
medicine_recommend = Todo3.model('Medicine_recommend', 
                        {   
                            'question_sq': fields.String(required=True,
                                                          description='question sq')
                        })

###########################  API  ####################################
class FM(tf.keras.Model):
    def __init__(self, p, k, t):
        super(FM, self).__init__()

        # 모델의 파라미터 정의
        self.t = t
        self.w = tf.Variable(tf.zeros((t, p)))
        self.V = tf.Variable(tf.random.normal(shape=(t, p, k)))
        self.w_0 = tf.Variable(t*[0.0])

    def _get_yhat(self, inputs, w, V, w_0):
        linear_terms = tf.reduce_sum(tf.math.multiply(w, inputs), axis=1)

        interactions = 0.5 * tf.reduce_sum(
            tf.math.pow(tf.matmul(inputs, V), 2)
            - tf.matmul(tf.math.pow(inputs, 2), tf.math.pow(V, 2)),
            1,
            keepdims=False
        )
        
        y_hat = tf.math.sigmoid(w_0 + linear_terms + interactions)
        return y_hat

    def call(self, inputs):
        y_hat_full = None
        for i in range(self.t):
            y_hat = self._get_yhat(inputs, self.w[i], self.V[i], self.w_0[i])
            y_hat = tf.reshape(y_hat, y_hat.shape+1)

            if y_hat_full is None:
                y_hat_full = y_hat
            else:
                y_hat_full = tf.concat([y_hat_full, y_hat], 1)

        return y_hat_full

    def model_output(x):
        tf.keras.backend.set_floatx('float32')
        columns = ['나이', '키', '현재 체중', '20대 초중반 체중', '20대 이후 최고 체중', '20대 이후 최저 체중', '대변횟수', '냄새', '후중감', '대변색', '대변모양', '설사경향모양', '소변횟수', '수분섭취', '구갈(갈증)', '구건(입마름)', '소화불량_20대이전', '소화불량_20대이후', '육식', '가공식품', '인스턴트식품', '단 음식', '맵고 짠 음식', '밀가루 음식', '기름진 음식', '과일', '채소', '외식 주 끼니', '음주', '흡연', '자다깨는횟수', '입면시간', '기상시 개운함', '식욕', '소화', '대변', '소변', '수면', '스트레스', '부종', '갈증', '소화력_식체', '소화력_가스헛배', '소화력_속더부룩함', '소화력_트림', '소화력_신물', '소화력_명치답답함', '소화력_메스꺼움', '소화력_속쓰림', '주소증', '과거력', '기타 병력', '청일수 점수', '청이장 점수', '청삼혈 점수', '청사심 점수', '청오식 점수', '청육행 점수', '청칠위 점수', '청팔보 점수', '청구력 점수', '청시원 점수']
        
        df = pd.DataFrame(x, columns=columns)
        
        x_test = df.loc[:, ['대변횟수', '냄새', '후중감', '대변색', '대변모양','설사경향모양', '소변횟수', '수분섭취', '구갈(갈증)', '구건(입마름)', '소화불량_20대이전', '소화불량_20대이후', '육식', '가공식품', '인스턴트식품', '단 음식', '맵고 짠 음식', '밀가루 음식', '기름진 음식', '과일', '채소', '외식 주 끼니', '음주', '흡연', '자다깨는횟수', '입면시간', '기상시 개운함', '식욕', '소화', '대변', '소변', '수면', '스트레스', '부종', '갈증', '소화력_식체', '소화력_가스헛배', '소화력_속더부룩함', '소화력_트림', '소화력_신물', '소화력_명치답답함', '소화력_메스꺼움', '소화력_속쓰림', '과거력', '청일수 점수', '청이장 점수', '청삼혈 점수', '청사심 점수', '청오식 점수', '청육행 점수', '청칠위 점수', '청팔보 점수', '청구력 점수', '청시원 점수']]

        p = x_test.shape[1]
        t = 10
        k = 50

        # 과거병력
        if len(x_test[x_test['과거력'].str.contains('위암', na=False)]) != 0:
            x_test['과거력'] = 2
        elif len(x_test[x_test['과거력'].str.contains('자가면역질환|피부질환|암', na=False)]) != 0:
            x_test['과거력'] = 3
        elif len(x_test[x_test['과거력'].str.contains('치매', na=False)]) != 0:
            x_test['과거력'] = 4
        elif len(x_test[x_test['과거력'].str.contains('당뇨|고혈압|고지혈증|심혈관질환|뇌혈관질환', na=False)]) != 0:
            x_test['과거력'] = 1
        else:
            x_test['과거력'] = 0

        x_test = x_test.fillna(0)
        x_test = pd.get_dummies(x_test)

        model = FM(p, k, t)
        model.load_weights('./model_v1/medicine_model_v1') # k = 50

        y_pred = model(x_test.values)
        result = [int(i) for i in y_pred[0]]
        return result


@Todo3.route('/Medicine_recommend')
class SearchPost1(Resource):
    @Todo3.expect(medicine_recommend)
    def post(self):
        req = request.get_json(force=True)
        req = json.loads(req)
        question_sq = req['question_sq']

        conn = psycopg2.connect(host='221.150.59.202', dbname='aidb', user='kca', password='kca21!@#', port=5432)
        cur = conn.cursor()

        medi_score = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

        # 나이, 키, 현재 체중, 20대 초중반 체중, 20대 이후 최고 체중, 20대 이후 최저 체중 - 기본문진 테이블
        sql_Q1 = "select user_birth, height, weight, weight_20age, weight_high, weight_low from tb_question where question_sq = " + str(question_sq)
        cur.execute(sql_Q1)
        res1 = cur.fetchall()

        # 대변횟수, 냄새, 후중감, 대변색, 대변모양, 설사경향모양, 소변횟수, 수분섭취, 구갈(갈증)여부, 구건(입마름) 여부, 소화불량_20대이전, 소화불량_20대이후 - 소화문진 테이블
        sql_Q2 = "select poo_count, poo_smell, poo_feel, poo_color, poo_shape, diarrhea_shape, pee_count, water_amount, mouth_thirsty, mouth_dry, indigestion_before, indegestion_after from tb_digestion where question_sq = " + str(question_sq)
        cur.execute(sql_Q2)
        res2 = cur.fetchall()

        if res2[0][0] < 1: # 대변횟수 < 1 청이장
            medi_score[1] += 1
        if res2[0][1] == 1: # 냄새 = 1 청이장
            medi_score[1] += 1
        if res2[0][2] >= 1: # 후중감 >= 1 청이장
            medi_score[1] += 1
        if res2[0][3] >= 3: # 대변색 >= 3 청이장
            medi_score[1] += 1
        if res2[0][4] <= 3: # 대변모양 <= 3 청이장
            medi_score[1] += 1
        if res2[0][5] <= 3: # 설사경향모양 <= 3 청이장
            medi_score[1] += 1
        if res2[0][6] <= 4: # 소변횟수 <= 4 청일수
            medi_score[0] += 1
        if res2[0][7] < 2: # 수분섭취 < 2 청일수
            medi_score[0] += 1
        if res2[0][8] == 1: # 구갈(갈증) 여부 = 1 청일수
            medi_score[0] += 1
        if res2[0][9] == 1: # 구건(입마름) 여부 = 1 청일수
            medi_score[0] += 1
        if res2[0][10] == 1: # 소화불량_20대이전 = 1 청칠위
            medi_score[6] += 1
        if res2[0][11] == 1: # 소화불량_20대이후 = 1 청칠위
            medi_score[6] += 1

        # 육식, 가공식품, 인스턴트식품, 단 음식, 맵고 짠 음식, 밀가루 음식, 기름진 음식, 과일, 채소, 외식 주 끼니, 음주, 흡연, 자다깨는횟수, 입면시간, 기상시 개운함 - 생활습관문진 테이블
        sql_Q3 = "select food_beef, food_processed, food_instant, food_sweet, food_spicy, food_flour, food_old, fruit, vegetable, eat_out, drinking, smoking, breaksleep_count, sleepin_time, wakeup_refresh from tb_lifestyle where question_sq = " + str(question_sq)
        cur.execute(sql_Q3)
        res3 = cur.fetchall()

        if res3[0][0] == 1: # 육식 = 1 청일수, 청이장, 청삼혈
            medi_score[0] += 1
            medi_score[1] += 1
            medi_score[2] += 1
        if res3[0][1] == 1: # 가공식품 = 1 청일수, 청이장, 청삼혈
            medi_score[0] += 1
            medi_score[1] += 1
            medi_score[2] += 1
        if res3[0][2] == 1: # 인스턴트식품 = 1 청일수, 청이장, 청삼혈
            medi_score[0] += 1
            medi_score[1] += 1
            medi_score[2] += 1
        if res3[0][3] == 1: # 단 음식 = 1 청일수, 청이장, 청삼혈
            medi_score[0] += 1
            medi_score[1] += 1
            medi_score[2] += 1
        if res3[0][4] == 1: # 맵고 짠 음식 = 1 청일수, 청이장, 청삼혈
            medi_score[0] += 1
            medi_score[1] += 1
            medi_score[2] += 1
        if res3[0][5] == 1: # 밀가루 음식 = 1 청일수, 청이장, 청삼혈
            medi_score[0] += 1
            medi_score[1] += 1
            medi_score[2] += 1
        if res3[0][6] == 1: # 기름진 음식 = 1 청일수, 청이장, 청삼혈
            medi_score[0] += 1
            medi_score[1] += 1
            medi_score[2] += 1
        if res3[0][7] == 0: # 과일 = 0 청일수, 청이장, 청삼혈
            medi_score[0] += 1
            medi_score[1] += 1
            medi_score[2] += 1
        if res3[0][8] == 0: # 채소 = 0 청일수
            medi_score[0] += 1
        if res3[0][9] >= 3: # 외식 주끼니 >= 3 청일수
            medi_score[0] += 1
        if res3[0][10] >= 3: # 음주 >= 3 청일수, 청이장, 청삼혈
            medi_score[0] += 1
            medi_score[1] += 1
            medi_score[2] += 1
        if res3[0][11] >= 1: # 흡연 >= 1 청일수, 청이장, 청삼혈
            medi_score[0] += 1
            medi_score[1] += 1
            medi_score[2] += 1
        if res3[0][12] >= 2: # 자다깨는횟수 >= 2 청사심
            medi_score[3] += 1
        if res3[0][13] >= 30: # 입면시간 >= 30 청사심
            medi_score[3] += 1
        if res3[0][14] > 1: # 기상시 개운함 = 2 청팔보
            medi_score[7] += 1

        # 식욕, 소화, 대변, 소변, 수면, 스트레스, 부종, 갈증, 소화력_식체, 소화력_가스헛배, 소화력_속더부룩함, 소화력_트림, 소화력_신물, 소화력_명치답답함, 소화력_메스꺼움, 소화력_속쓰림 - 건강척도 테이블
        sql_Q4 = "select appetite, digestion, foo, fee, sleep, stress, tumepy, thrist, digestion_stomach, digestion_gas, digestion_full, digestion_burp, digestion_acid_reflux, digestion_heaviness, digestion_sickness, digestion_sour_stomach from tb_healthlevel where question_sq = " + str(question_sq)
        cur.execute(sql_Q4)
        res4 = cur.fetchall()

        if res4[0][0] < 3: # 식욕 < 3 청칠위
            medi_score[6] += 1
        if res4[0][1] < 3: # 소화 < 3 청칠위
            medi_score[6] += 1
        if res4[0][2] < 3: # 대변 < 3 청이장
            medi_score[1] += 1
        if res4[0][3] < 3: # 소변 < 3 청일수
            medi_score[0] += 1
        if res4[0][4] < 3: # 수면 < 3 청사심
            medi_score[3] += 1
        if res4[0][5] < 3: # 스트레스 < 3 청사심
            medi_score[3] += 1
        if res4[0][6] < 3: # 부종 < 3 청일수
            medi_score[0] += 1
        if res4[0][7] < 3: # 갈증 < 3 청일수
            medi_score[0] += 1
        if res4[0][8] == 1: # 식체 = 1 청칠위
            medi_score[6] += 1
        if res4[0][9] == 1: # 가스/헛배 = 1 청칠위
            medi_score[6] += 1
        if res4[0][10] == 1: # 속더부룩함 = 1 청칠위
            medi_score[6] += 1
        if res4[0][11] == 1: # 트림 = 1 청칠위
            medi_score[6] += 1
        if res4[0][12] == 1: # 신물 = 1 청칠위
            medi_score[6] += 1
        if res4[0][13] == 1: # 명치답답함 = 1 청칠위
            medi_score[6] += 1
        if res4[0][14] == 1: # 메스꺼움 = 1 청칠위
            medi_score[6] += 1
        if res4[0][15] == 1: # 속쓰림 = 1 청칠위
            medi_score[6] += 1

        # 주소증, 과거력, 기타 병력 - 병력 테이블
        sql_Q5 = "select chief_complain, pmhx, pmhx_etc from tb_history where question_sq = '" + str(question_sq) + "'"
        cur.execute(sql_Q5)
        res5 = cur.fetchall()

        if res5[0][1] != '' and res5[0][1] != '기타' and res5[0][1] != '해당없음': # 과거력 청일수,청이장,청삼혈,청오식,청육행 != null or 기타, 청칠위 = 위암, 청구력 = 암 or 피부질환 or 자가면역질환, 청시원 = 치매
            medi_score[0] += 1
            medi_score[1] += 1
            medi_score[2] += 1
            medi_score[4] += 1
            medi_score[5] += 1
        if '위암' in res5[0][1]:
            medi_score[6] += 1
        if '암' in res5[0][1] or '피부질환' in res5[0][1] or '자가면역질환' in res5[0][1]:
            medi_score[8] += 1
        if '치매' in res5[0][1]:
            medi_score[9] += 1

        res = list(res1[0] + res2[0] + res3[0] + res4[0] + res5[0])
        
        temp = [res + medi_score]
        res = FM.model_output(temp)

        medicine = ['청일수', '청이장', '청삼혈', '청사심', '청오식', '청육행', '청칠위', '청팔보', '청구력', '청시원']
        recommend = [medicine[i] for i in range(len(res)) if res[i] == 1]
        expert = [medicine[i] for i in range(len(medi_score)) if medi_score[i] != 0]
        
        recommend_count = "select count(*) from tb_medicine_recommend where question_sq = " + str(question_sq)
        cur.execute(recommend_count)
        count = cur.fetchall()[0]

        if count[0] == 0:
            insert = "insert into tb_medicine_recommend(medi_one, medi_two, medi_three, medi_four, medi_five, medi_six, medi_seven, medi_eight, medi_nine, medi_ten) values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            cur.execute(insert, (res[0], res[1], res[2], res[3], res[4], res[5], res[6], res[7], res[8], res[9]))
            conn.commit()

        # 정상 체중(정상 BMI)
        if int(res1[0][0]) > 35:
            normal_weight = round((res1[0][1] ** 2 * 21) / 10000, 1)
        else:
            normal_weight = round((res1[0][1] ** 2 * 20) / 10000, 1)

        # 증가 체중 계산
        if res1[0][2] < res1[0][4]:
            add_weight = res1[0][4] - res1[0][3]
        else: 
            add_weight = res1[0][2] - res1[0][3]

        # 보정 체중 계산
        if int(res1[0][0]) < 30:
            corrected_weight = 0
        elif int(res1[0][0]) < 35:
            corrected_weight = round(add_weight / 4, 1)
        elif int(res1[0][0]) < 40:
            corrected_weight = round(add_weight / 3, 1)
        else:
            corrected_weight = round(add_weight / 2, 1)

        # 건강한 체중(적정 체중)
        healthy_weight = corrected_weight + res1[0][3] # 보정 체중 + 20대 초중반 체중

        prescription_etc = "select count(*) from tb_prescription_etc where prescription_etc_sq = " + str(question_sq)
        cur.execute(prescription_etc)
        prescription = cur.fetchall()[0]

        if prescription[0] == 0:
            insert_weight = "insert into tb_prescription_etc(prescription_etc_sq, normal_weight, healthy_weight) values(%s, %s, %s)"
            cur.execute(insert_weight, (question_sq, normal_weight, healthy_weight))
            conn.commit()

        # 처방 추천, 전문가 처방, 정상 BMI(정상 체중), 건강한 체중
        data = {'recommend':recommend, 'expert':expert, 'normal_weight':normal_weight, 'healthy_weight':healthy_weight}

        response = json.dumps(data, ensure_ascii=False).encode('utf-8')

        return Response(response, content_type='application/json; charset=utf-8')
