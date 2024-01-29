from flask import Flask, jsonify, request, render_template
import random
import json
import pandas as pd
from work_model import resultModel

print("hello flask")
app = Flask(__name__)

# 해독지수 detox_score
@app.route('/detox_score', methods=['GET','POST'])
def detox_score():
    ## -----------------------데이터 받기-------------------##
    data = request.json
    data = json.loads(data)
    data_column = data['survey_title'] 
    data_value = data['survey_data']

    survey_data_df = pd.DataFrame(columns=data_column)
    survey_data_df.loc[0] = data_value

    healthlevel_col = ['appetite', 'digestion', 'foo', 'fee', 'sleep', 'stress', 'sweat', 'coldhand', 'hand_numb', 'headache', 
                        'whirl', 'tumepy', 'thrist', 'shoulder_pain', 'chest', 'heart_pain', 'anxious', 'fatigue', 'menstruation_pain', 'menstruation_period']
    
    ## ------------------score 전문가 진단 ---------------------------##
    healthlevel_df = survey_data_df.iloc[0][healthlevel_col]
    healthlevel_fval = list(map(float,healthlevel_df))

    score_result_1 = []
    score_result_2 = []
    result_final = []

    # 해독 상수 적용 전 계산 (기본:6-n, 특수case 처리)
    for i,col in enumerate(healthlevel_col):
        if col == 'sweat':
            score_result_1.append(abs(3.0-healthlevel_fval[i]))
        elif col == 'menstruation_period':
            score_result_1.append(4.0-healthlevel_fval[i])
        else:
            score_result_1.append(6.0-healthlevel_fval[i])
    
    for i,col in enumerate(healthlevel_col):
        score_value = 0.0
        score_value = score_result_1[i]

        if col == 'digestion':
            score_value += float(survey_data_df.iloc[0]['digestion_total'])/2.0

        elif col == 'foo':
            poo_count = float(survey_data_df.iloc[0]['poo_count']) 
            poo_smell = int(survey_data_df.iloc[0]['poo_smell']) 
            poo_feel = int(survey_data_df.iloc[0]['poo_feel'])
            poo_color = int(survey_data_df.iloc[0]['poo_color'])
            poo_shape = int(survey_data_df.iloc[0]['poo_shape'])
            diarrhea_shape = int(survey_data_df.iloc[0]['diarrhea_shape'])

            if poo_count > 2 or poo_count <= 0.5:
                score_value += 1.0
            if poo_smell >= 1:
                score_value += 1.0
            if poo_color > 2:
                score_value += 1.0
            if diarrhea_shape > 4.0:
                score_value += diarrhea_shape/5.5
            if poo_shape == 1:
                score_value += 1.0
            elif poo_shape == 2:
                score_value += 0.5
            score_value += poo_feel/2.0

        elif col == 'fee':
            pee_count = float(survey_data_df.iloc[0]['pee_count'])
            pee_night_count = float(survey_data_df.iloc[0]['pee_night_count'])

            if pee_count < 4.0 or pee_count > 7.0:
                score_value += 1.0
            if pee_night_count >= 0.75:
                score_value += 1.0

        elif col == 'sleep':
            breaksleep_count = float(survey_data_df.iloc[0]['breaksleep_count'])
            sleepin_time = float(survey_data_df.iloc[0]['sleepin_time'])

            if breaksleep_count > 4:
                score_value += 1.5
            else:
                score_value += breaksleep_count/3.0
            
            if sleepin_time >= 120.0:
                score_value += 3.0
            elif sleepin_time >= 30 and sleepin_time <= 119:
                score_value += sleepin_time/40.0

        elif col == 'thrist':
            score_value += float(survey_data_df.iloc[0]['mouth_thirsty'])

        elif col == 'fatigue':
            score_value += float(survey_data_df.iloc[0]['wakeup_refresh'])
        
        elif survey_data_df.iloc[0]['user_gender'] == '0' and (col == 'menstruation_pain' or col == 'menstruation_period'):
            score_value = 0.0  
        score_result_2.append(score_value)

    # 해독 상수 적용 계산
    static_val = [5.20, 8.50, 10.32, 7.60, 9.72, 5.35, 3.10, 5.56, 5.31, 5.54, 5.49, 5.28, 6.20, 5.73, 5.46, 5.27, 5.61, 7.82, 5.53, 3.95]
    for i in range(len(static_val)):
        result_final.append(round(score_result_2[i]/static_val[i],2))

    score_result_df = pd.DataFrame(columns=healthlevel_col)
    score_result_df.loc[0] = result_final

    # 종합점수 계산(남/녀 조건)
    if survey_data_df.iloc[0]['user_gender'] == '0':
        result_total_score = round(sum(score_result_2) / 113.06,2)
    else:
        result_total_score = round(sum(score_result_2) / 122.54,2)


    ## -------------------score AI 진단--------------------------##
    xgbmodel = resultModel()
    predictions = xgbmodel.regression_model_input(survey_data_df)
    ai_score_result = list(map(str,predictions))

    score_data = {"score_col":list(score_result_df.columns),
                  "expert_score_data":list(map(str,score_result_df.iloc[0].values)),
                  "expert_total_score":str(result_total_score),
                  "ai_score_data":ai_score_result[:-1],
                  "ai_total_score":ai_score_result[-1]}

    return score_data


# 해독유형 detox_type
@app.route('/detox_type', methods=['GET','POST'])
def detox_type():
    if request.method == "POST":
        data = request.json
        data = json.loads(data)
        data_column = data['survey_title'] 
        data_value = data['survey_data']

        survey_data_df = pd.DataFrame(columns=data_column)
        survey_data_df.loc[0] = data_value

        ## -------------------type 전문가 진단--------------------------##
        expert_use_col = ['user_birth','weight','weight_20age','weight_high','weight_low','indigestion_before','indegestion_after','digestion','digestion_total']
        type_expert_df = survey_data_df[expert_use_col]
        type_expert_df = type_expert_df.astype('float')

        weight_add = 0
        weight_scaling = 0

        if type_expert_df.iloc[0]['weight_high'] > type_expert_df.iloc[0]['weight']:
            weight_add = type_expert_df.iloc[0]['weight_high'] - type_expert_df.iloc[0]['weight_low']
        else:
            weight_add = type_expert_df.iloc[0]['weight'] - type_expert_df.iloc[0]['weight_low']

        if type_expert_df.iloc[0]['user_birth'] < 30:
            weight_scaling = 0
        elif type_expert_df.iloc[0]['user_birth'] >= 30 and type_expert_df.iloc[0]['user_birth'] < 35:
            weight_scaling = round(weight_add/4.0,1)
        elif type_expert_df.iloc[0]['user_birth'] >= 35 and type_expert_df.iloc[0]['user_birth'] < 40:
            weight_scaling = round(weight_add/3.0,1)
        else:
            weight_scaling = round(weight_add/2.0,1)

        weight_standard = type_expert_df.iloc[0]['weight_20age'] + weight_scaling
        digestion_score = round((6-type_expert_df.iloc[0]['digestion']+(type_expert_df.iloc[0]['digestion_total']/2.0))/8.5,2)

        weight_consider = {'excess':0,'digestion_ability':0,'inborn_digestion':0,'acquired_digestion':0}

        if type_expert_df.iloc[0]['weight'] > weight_standard:
            weight_consider['excess'] = 1

        if digestion_score > 0.47:
            weight_consider['digestion_ability'] = 1
        
        weight_consider['inborn_digestion'] = int(type_expert_df.iloc[0]['indigestion_before'])
        weight_consider['acquired_digestion'] = int(type_expert_df.iloc[0]['indegestion_after'])

        expert_detox_type = 0
        #1유형
        if sum(weight_consider.values()) == 0:
            expert_detox_type = 1
        #2유형
        if weight_consider['excess'] == 1 and sum(weight_consider.values()) == 1:
            expert_detox_type = 2
        #3유형
        if weight_consider['inborn_digestion'] == 1 or weight_consider['acquired_digestion'] == 1:
            expert_detox_type = 3
        #4유형
        if weight_consider['excess'] == 1 and (weight_consider['inborn_digestion'] == 1 or weight_consider['acquired_digestion'] == 1):
            expert_detox_type = 4
        #5,6유형
        if int(type_expert_df.iloc[0]['user_birth']) < 30:
            if weight_consider['excess'] == 0 and weight_consider['inborn_digestion'] == 1:
                expert_detox_type = 5
            elif weight_consider['excess'] == 1 and weight_consider['inborn_digestion'] == 1:
                expert_detox_type = 6

        elif int(type_expert_df.iloc[0]['user_birth']) >= 30:
            if weight_consider['excess'] == 0 and (weight_consider['digestion_ability'] == 1 and weight_consider['inborn_digestion'] == 1):
                expert_detox_type = 5
            elif weight_consider['excess'] == 1 and (weight_consider['digestion_ability'] == 1 and weight_consider['inborn_digestion'] == 1):
                expert_detox_type = 6
        
        ## -------------------type AI 진단--------------------------##
        col_digestion_score = ['digestion_stomach', 'digestion_gas', 'digestion_full', 'digestion_burp', 'digestion_acid_reflux', 
                         'digestion_heaviness', 'digestion_sickness', 'digestion_sour_stomach', 'digestion_total']
        col_question = ['user_birth','weight','weight_20age','weight_high','indigestion_before','indegestion_after']
        col_healthlevel = ['appetite', 'digestion', 'foo', 'fee', 'sleep', 'stress', 'sweat', 'coldhand', 'hand_numb', 'headache', 'whirl', 'tumepy', 
                        'thrist', 'shoulder_pain', 'chest', 'heart_pain', 'anxious', 'fatigue', 'menstruation_pain', 'menstruation_period','healthy_total_score']
        detoxtype_col = col_digestion_score+col_question+col_healthlevel
        type_ai_df = survey_data_df[detoxtype_col]

        xgbmodel = resultModel()
        predictions = xgbmodel.classify_model_input(type_ai_df)
        ai_detox_type = int(predictions[0]+1)
    
        result = {"expert_detox_type":expert_detox_type,"ai_detox_type":ai_detox_type}
        return result
    
    else:    
        result = {"data":''}
        return result

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5005, debug=True)