from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt

from detoxapp.DBConnection.db_sqlalchemy import dbSqlAlchemy
from sqlalchemy.sql import text
import pandas as pd
import time
import requests
import json
import base64

from pathlib import Path
from sqlalchemy import create_engine, text
from sqlalchemy import Table, MetaData, insert
import numpy as np
import hashlib
import re
import os
import cv2

from DetoxProject.system_sever_set import flask_server

predict_meta_all = {
'설질': {0: '담홍설', 1: '담백설', 2:'홍설', 3: '강설', 4:' 자설'},
'설태': {0: '무태', 1: '박백태', 2: '백태', 3: '황태', 4: '회태', 5: '흑태'},
'설열': {1: '유', 0: '무'},
'어반': {1: '유', 0: '무'},
'치흔': {1: '유', 0: '무'},
}
predict_meta_large_intenstines = {
'대장_설태': {0: '무태', 1: '박백태', 2: '백태', 3: '황태', 4: '회태', 5: '흑태'},
'대장_설반': {1: '유', 0: '무'},
}
predict_meta_stomach = {
'위장_설태': {0: '무태', 1: '박백태', 2: '백태', 3: '황태', 4: '회태', 5: '흑태'},
'위장_설열': {1: '유', 0: '무'},
}
predict_meta_heart = {
'심장_설열': {1: '유', 0: '무'},
}
predict_meta_lung = {
'폐 _설태': {0: '무태', 1: '박백태', 2: '백태', 3: '황태', 4: '회태', 5: '흑태'},
'폐 _설열': {1: '유', 0: '무'},
'폐 _설반': {1: '유', 0: '무'},
}
predict_meta_tongue_tip = {
'설첨_홍색': {1: '유', 0: '무'},
'설첨_설반': {1: '유', 0: '무'},
}
predict_meta_area = [predict_meta_large_intenstines, predict_meta_stomach, predict_meta_heart, predict_meta_lung, predict_meta_tongue_tip]

#DB 인서트
def get_stmt(table_name, data, engine, option= False):
    table = Table(table_name, MetaData(), autoload_with=engine)
    columns = table.columns.keys()
    if option == 'info':
        columns = columns[1:]
        data = [data[:10] + data[10:13]*2 + data[13:]]
    elif option == 'seg':
        columns = columns[1:]
    else:
        columns = columns[1:]

    dict_data = [dict(zip(columns, one_data)) for one_data in data]
    stmt = insert(table).values(dict_data)

    return stmt

#Hash값 추출
def get_hash(byte_data):
    return hashlib.sha256(byte_data).hexdigest()

#데이터 INSERT
def insert_data(stmt, engine):
    stmt.compile()
    with engine.connect() as conn:
        conn.execute(stmt)
        conn.commit()

#SQ값 가져오기
def get_sequence(engine):
    sequence = 1
    with engine.connect() as conn:
        result = conn.execute(text("SELECT MAX(orgn_img_num) FROM tb_orgn_tongue")).fetchone()[0]
        if result:
            sequence = result+1
    return sequence

#SQ값 가져오기(seg)
def get_sequence_seg(engine):
    sequence = 1
    with engine.connect() as conn:
        result = conn.execute(text("SELECT MAX(segmented_img_num) FROM tb_segmented_tongue")).fetchone()[0]
        if result:
            sequence = result+1
    return sequence

###################################### Setting #######################################
# 원본 이미지 중복체크
def check_dupl_image(engine, img_hash, question_sq):
    with engine.connect() as conn:
        result = conn.execute(text(f"SELECT img_hash, orgn_img_num FROM tb_orgn_tongue WHERE question_sq={question_sq}"))
        for data in result.all():
            if img_hash == data[0]:
                return data[1]

        return False
# 분할 이미지 중복체크
def check_dupl_seg_image(engine, img_seq):
    with engine.connect() as conn:
        result = conn.execute(text(f"SELECT orgn_img_num, segmented_img_num FROM tb_segmented_tongue WHERE orgn_img_num={img_seq}"))
        for data in result.all():
            if img_seq == data[0]:
                return data[1]

        return False
##########################################################################################

###################################### Insert Data #######################################
# Origin
def insert_origin_tongue_info(engine, save_path, img_hash, img_array, question_sq):
    # file infos
    save_path = str(save_path)
    file_path, file_extns = os.path.splitext(save_path)
    # name, extens, path
    file_name = os.path.basename(file_path)
    file_extns = file_extns[1:]
    file_path = os.path.dirname(file_path)

    # img_shape
    img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
    img_width, img_height, _ = img.shape

    # img taken
    date_taken = re.findall('[0-9]{4}-[0-9]{2}-[0-9]{2}', file_name)[:1]
    if not date_taken:
        date_taken = re.findall('[0-9]{4}-?[0-9]{2}-?[0-9]{2}', file_name)[:1]

    if date_taken:
        date_taken = date_taken[0]
        if len(date_taken) == 8:
            date_taken = f"{date_taken[:4]}-{date_taken[4:6]}-{date_taken[6:8]}"
    else:
        date_taken = None

    data = [[file_name, file_extns, file_path, img_hash, img_width, img_height, date_taken, question_sq]]
    stmt = get_stmt('tb_orgn_tongue', data, engine)

    insert_data(stmt, engine)


# Segmented
def insert_segmented_tongue_info(engine, file_name, file_path, img_seq):
    file_name = file_name[:-4]
    data = [[file_name, file_path, img_seq]]
    stmt = get_stmt('tb_segmented_tongue', data, engine, 'seg')
    insert_data(stmt, engine)
##########################################################################################

#######################################################################################################################
# 1. MethodName : tongue_detail
# 2. Comment    : 설진 화면 진입
# 3. 작성자      : 전준영
# 4. 작성일      : 2023. 08. 22.
#######################################################################################################################
def tongue_detail(request):
    if request.method == 'GET':
        question_sq = request.GET.get("question_sq")
        # try:
        engine, session = dbSqlAlchemy.get_engine()
        sql = f"""
select a.user_sq, a.user_name, b.question_sq, b.user_gender, b.user_birth
from tb_user a, tb_question b
where a.user_sq = b.user_sq
and b.question_sq = {question_sq};
        """
        user_result = pd.read_sql_query(text(sql), engine)

        sql = f"""
select a.*, b.*, c.*
from tb_orgn_tongue a, tb_segmented_tongue b, tb_tongue_predict c
where a.question_sq = {question_sq}
and a.orgn_img_num = b.orgn_img_num
and b.segmented_img_num = c.segmented_img_num
        """
        tongue_result = pd.read_sql_query(text(sql), engine)

        if len(tongue_result) == 0:
            tongue_result = {}
        else:
            tongue_result = tongue_result.to_dict('records')[0]

    context = {'predict_meta_all': predict_meta_all,
               'predict_meta_area':predict_meta_area,
               'user_info': user_result.to_dict('records')[0],
               'tungue_info': tongue_result}
    return render(request, 'detoxapp/tongue/tongue_detail.html',context=context)


#######################################################################################################################
# 1. MethodName : upload_tongue
# 2. Comment    : 사진 저장 (단계1/2)
# 3. 작성자      : 전준영
# 4. 작성일      : 2023. 08. 21.
#######################################################################################################################
@csrf_exempt
def upload_tongue(request):
    basic_response = {
        'su': False,
        'img_dupl': False,
        'img_path': None,
        'cur_seq': None
    }

    #DB CONNECTION - 실패시 바로 return
    try:
        engine, session = dbSqlAlchemy.get_engine()
    except Exception as e:
        print(e)
        return JsonResponse(basic_response)

    if request.method == 'POST':
        file = request.FILES['File']
        question_sq = request.POST.get('question_sq')
        BASE_DIR = Path(__file__).resolve().parent.parent
        IMAGE_DIR = Path('static/detoxapp/image/tongue_images')
        save_path = (BASE_DIR / IMAGE_DIR / file.name)

        # segmented_tongue
        if 'file_name' in request.POST.keys():
            file_name = request.POST.get('file_name')
            save_path = (BASE_DIR / IMAGE_DIR / file_name)
            file_path = os.path.dirname(str(save_path))
            # if not dupl, save to db
            img_seq = int(request.POST.get('img_seq'))
            seg_index = check_dupl_seg_image(engine, img_seq)
            if not seg_index:
                insert_segmented_tongue_info(engine, file_name, file_path, img_seq)
            basic_response["img_path"] = file_name

        else:
            # check dupl image
            read_file = file.read()
            img_array = np.frombuffer(read_file, np.uint8)
            img_hash = get_hash(img_array)

            # if dupl, return file name
            img_index = check_dupl_image(engine, img_hash, question_sq)
            if img_index:
                basic_response["su"] = True
                basic_response["img_dupl"] = True
                basic_response["img_path"] = file.name
                basic_response["cur_seq"] = img_index
                return JsonResponse(basic_response)

            # if new img, save to db
            basic_response["cur_seq"] = get_sequence(engine)
            insert_origin_tongue_info(engine, save_path, img_hash, img_array, question_sq)
        with open(save_path, 'wb+') as img:
            for chunk in file.chunks():
                img.write(chunk)

        basic_response["su"] = True

        return JsonResponse(basic_response)

#######################################################################################################################
# 1. MethodName : segment_tongue
# 2. Comment    : 혀 영역 추출 (단계2)
# 3. 작성자      : 전준영
# 4. 작성일      : 2023. 08. 21.
#######################################################################################################################
@csrf_exempt
def segment_tongue(request):
    if request.method == 'POST':
        result = json.loads(request.body)
        filename = result['filename']
        BASE_DIR = Path(__file__).resolve().parent.parent
        IMAGE_DIR = Path('static/detoxapp/image/tongue_images')
        save_path = (BASE_DIR / IMAGE_DIR / filename)
        seg_filename = filename.replace('.jpg', '')+'_out.jpg'
        seg_save_path = (BASE_DIR / IMAGE_DIR / seg_filename)

        res = requests.post(flask_server.tongue_server_segment, files={"File": open(save_path, 'rb')})

        data = {"file": res.text, 'save_path': str(seg_save_path), 'seg_filename': seg_filename}
        return JsonResponse(data)

#######################################################################################################################
# 1. MethodName : predict_tongue
# 2. Comment    : AI알고리즘 (단계3)
# 3. 작성자      : 전준영
# 4. 작성일      : 2023. 08. 21.
#######################################################################################################################
@csrf_exempt
def predict_tongue(request):
    basic_response = {
        'su': False,
    }

    # DB CONNECTION - 실패시 바로 return
    try:
        engine, session = dbSqlAlchemy.get_engine()
    except Exception as e:
        print(e)
        return JsonResponse(basic_response)

    if request.method == 'POST':
        result = json.loads(request.body)
        filename = result['filename']
        BASE_DIR = Path(__file__).resolve().parent.parent
        IMAGE_DIR = Path('static/detoxapp/image/tongue_images')
        save_path = (BASE_DIR / IMAGE_DIR / filename)
        res = requests.post(flask_server.tongue_server_predict,
                            files={"File": open(save_path, 'rb')})
        # print(res.json())

        predict_list = res.json()['predict_list']
        img_seq = int(result['img_seq'])
        seg_index = check_dupl_seg_image(engine, img_seq)
        insert_predict_info(engine, predict_list, seg_index)

        basic_response['su'] = True
        basic_response['predict_list'] = predict_list
        return JsonResponse(basic_response)


# Predict
def insert_predict_info(engine, predict_list, seg_index):
    data = list(map(int, predict_list)) + [seg_index]
    stmt = get_stmt('tb_tongue_predict', data, engine, 'info')
    insert_data(stmt, engine)


#######################################################################################################################
# 1. MethodName : label_tongue
# 2. Comment    : 전문가 진단 저장 및 제출
# 3. 작성자      : 전준영
# 4. 작성일      : 2023. 08. 23.
#######################################################################################################################
# Result
@csrf_exempt
def label_tongue(request):
    basic_response = {
        'su': False,
    }
    # DB CONNECTION - 실패시 바로 return
    try:
        engine, session = dbSqlAlchemy.get_engine()
    except Exception as e:
        print(e)
        return JsonResponse(basic_response)

    if request.method == 'POST':
        true_list = request.POST.getlist('true_list[]')
        img_seq = request.POST.get('img_seq')
        insert_label_info(engine, true_list, img_seq)
        basic_response['su'] = True
        return JsonResponse(basic_response)

# True
def insert_label_info(engine, true_list, img_seq):
    data = list(map(int, true_list)) + [img_seq]
    stmt = get_stmt('tb_tongue_label', data, engine, 'info')
    insert_data(stmt, engine)
