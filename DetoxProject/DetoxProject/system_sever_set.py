
class flask_server():
    # 분류모델
    survey_server_type = 'http://221.150.59.202:5005/detox_type'
    # 회귀모델
    survey_server_score = 'http://221.150.59.202:5005/detox_score'

    # 혀 영역 추출
    tongue_server_segment = 'http://221.150.59.202:5000/Tongue_Project/Segment_Tongue'
    # tongue_server_segment = 'http://127.0.0.1:5000/Tongue_Project/Segment_Tongue'
    # 혀 분석
    tongue_server_predict = 'http://221.150.59.202:5000/Tongue_Project/Predict_Tongue'
    # tongue_server_predict = 'http://127.0.0.1:5000/Tongue_Project/Predict_Tongue'

    # 처방 추천 모델
    prescription_server = 'http://221.150.59.202:5015/Medicine_api/Medicine_recommend'
    # prescription_server = 'http://127.0.0.1:5015/Medicine_api/Medicine_recommend'

class db_server():
    dbname = "aidb"
    dbuser = "kca"
    dbpassword = "kca21!@#"
    # host = "221.150.59.211"
    host = "221.150.59.202"

    # dbname = "survey_test"
    # dbuser = "postgres"
    # dbpassword = "adminadmin"
    # host = "localhost"