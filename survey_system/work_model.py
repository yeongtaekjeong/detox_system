from xgboost import XGBClassifier, XGBRegressor

class resultModel():
    def classify_model_input(self, modeltest):
        data = modeltest.astype('float')
        xgb_model = XGBClassifier()
        xgb_model.load_model("./classify_model/xgb_model_v2.model")
        predicts = xgb_model.predict(data)

        return predicts
    
    def regression_model_input(self, surveydf):
        user_col =['user_gender']
        digestion_level_col = ['digestion_stomach', 'digestion_gas', 'digestion_full', 'digestion_burp', 'digestion_acid_reflux', 
                    'digestion_heaviness', 'digestion_sickness', 'digestion_sour_stomach', 'digestion_total']
        healthlevel_col = ['appetite', 'digestion', 'foo', 'fee', 'sleep', 'stress', 'sweat', 'coldhand', 'hand_numb', 'headache', 'whirl', 'tumepy', 
                'thrist', 'shoulder_pain', 'chest', 'heart_pain', 'anxious', 'fatigue', 'menstruation_pain', 'menstruation_period','healthy_total_score']
        digestion_col = ['poo_count','poo_smell','poo_feel','poo_color','poo_shape','diarrhea_shape','pee_count','pee_night_count',
                    'water_amount','mouth_thirsty','mouth_dry','mouth_chew','food_night','foot_excess','food_unbalance']
        lifestyle_col = ['breaksleep_count','sleepin_time','wakeup_refresh']

        score_all_use_col = user_col+digestion_level_col+healthlevel_col+digestion_col+lifestyle_col
        
        modeltest_data = surveydf[score_all_use_col]
        modeltest_data = modeltest_data.astype('float')

        ai_score_result = []

        for colnm in healthlevel_col:
            xgb_model = XGBRegressor()
            modelnm = "xgb_model_reg_"+colnm+".model"
            xgb_model.load_model("./regression_model/"+modelnm)
            predicts = xgb_model.predict(modeltest_data)
            ai_score_result.append(round(predicts[0],2))

        return ai_score_result




