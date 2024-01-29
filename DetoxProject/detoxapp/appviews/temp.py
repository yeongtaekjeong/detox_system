from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from pathlib import Path

from sqlalchemy import create_engine, text
from sqlalchemy import Table, MetaData, insert
from urllib.parse import quote

import numpy as np
import hashlib
import cv2
import re
import os

# Image Save Path
BASE_DIR = Path(__file__).resolve().parent.parent
IMAGE_DIR = Path('static/decodingapp/image/tongue_images')

# DB Info
id = "kca"
pwd = "kca21!@#"
engine = create_engine(f"postgresql://{id}:{quote(pwd)}@221.150.59.202:5432/aidb")


# Views
def main(request):
    return render(request, 'decodingapp/main.html', {})


def tongue_define(request):
    return render(request, 'decodingapp/tongue/tongue_define.html', {})


def tongue_ai(request):
    return render(request, 'decodingapp/tongue/tongue_ai.html', {})


# Tab change
@csrf_exempt
def tongue_change(request):
    tabno = 0
    if request.method == 'POST':
        tabno = request.POST.get('no')
        tabval = {"tabno": tabno}

        return JsonResponse(tabval)
    else:
        return render(request, 'decodingapp/tongue/tongue_ai.html', {})


# Image Upload
@csrf_exempt
def upload_tongue(request):
    if request.method == 'POST':
        file = request.FILES['File']
        basic_response = {"img_dupl": False}

        # segmented_tongue
        if 'file_name' in request.POST.keys():
            file_name = request.POST.get('file_name')
            save_path = (BASE_DIR / IMAGE_DIR / file_name)
            file_path = os.path.dirname(str(save_path))
            basic_response["img_path"] = file_name
            # if not dupl, save to db
            img_seq = int(request.POST.get('img_seq'))
            if check_dupl_seg_image(engine, img_seq):
                insert_segmented_tongue_info(file_name, file_path, img_seq)

        # origin_tongue
        else:
            save_path = (BASE_DIR / IMAGE_DIR / file.name)
            # check dupl image
            read_file = file.read()
            img_array = np.frombuffer(read_file, np.uint8)
            img_hash = get_hash(img_array)

            # if dupl, return file name
            img_index = check_dupl_image(engine, img_hash)
            if img_index:
                basic_response["img_dupl"] = True
                basic_response["img_path"] = file.name
                basic_response["cur_seq"] = img_index
                return JsonResponse(basic_response)

            # if new img, save to db
            basic_response["cur_seq"] = get_sequence(engine)
            insert_origin_tongue_info(save_path, img_hash, img_array)

        # save image file
        with open(save_path, 'wb+') as img:
            for chunk in file.chunks():
                img.write(chunk)
        return JsonResponse(basic_response)


############ Setting #############
# 원본 이미지 중복체크
def check_dupl_image(engine, img_hash):
    with engine.connect() as conn:
        result = conn.execute(text("SELECT img_hash FROM tb_orgn_tongue"))
        for idx, data in enumerate(result.all()):
            if img_hash == data[0]:
                return idx + 1
        else:
            return False


# 분할 이미지 중복체크
def check_dupl_seg_image(engine, img_seq):
    with engine.connect() as conn:
        result = conn.execute(text("SELECT orgn_img_num FROM tb_segmented_tongue"))
        for data in result.all():
            if img_seq == data[0]:
                return False
        else:
            return True


def get_hash(byte_data):
    return hashlib.sha256(byte_data).hexdigest()


def get_stmt(table_name, data, option=False):
    table = Table(table_name, MetaData(), autoload_with=engine)
    columns = table.columns.keys()
    if option == 'info':
        columns = list(np.array(columns)[[1, 4, 5, 10, 6, 8, 11, 14, 13, 16, 17, -1]])
        data = [data[:6] + [data[6]] * 2 + [data[7]] * 2 + [data[-2]] + [data[-1]]]
    elif option == 'seg':
        columns = columns[1:]
    else:
        columns = columns[1:-1]

    dict_data = [dict(zip(columns, one_data)) for one_data in data]
    stmt = insert(table).values(dict_data)
    return stmt


def insert_data(stmt, engine):
    stmt.compile()
    with engine.connect() as conn:
        conn.execute(stmt)
        conn.commit()


def get_sequence(engine):
    sequence = 1
    with engine.connect() as conn:
        result = conn.execute(text("SELECT MAX(orgn_img_num) FROM tb_orgn_tongue")).fetchone()[0]
        if result:
            sequence = result + 1
    print(sequence)
    return sequence


###################################### Insert Data #######################################
# Origin
def insert_origin_tongue_info(save_path, img_hash, img_array):
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

    data = [[file_name, file_extns, file_path, img_hash, img_width, img_height, date_taken]]
    stmt = get_stmt('tb_orgn_tongue', data)
    insert_data(stmt, engine)


# Segmented
def insert_segmented_tongue_info(file_name, file_path, img_seq):
    file_name = file_name[:-4]
    data = [[file_name, file_path, img_seq]]
    stmt = get_stmt('tb_segmented_tongue', data, 'seg')
    insert_data(stmt, engine)
###########################################################################################

# Predict
@csrf_exempt
def predict_to_db(request):
    if request.method == 'POST':
        pred_list = request.POST.getlist('predict_list[]')
        img_seq = request.POST.get('img_seq')
        insert_predict_info(pred_list, img_seq)
        return JsonResponse({"remove_500": 500})
    else:
        return render(request, 'decodingapp/tongue/tongue_ai.html', {})


# Predict
def insert_predict_info(pred_list, img_seq):
    data = list(map(int, pred_list)) + [img_seq]
    stmt = get_stmt('tb_tongue_predict', data, 'info')
    insert_data(stmt, engine)


# Result
@csrf_exempt
def result_to_db(request):
    if request.method == 'POST':
        true_list = request.POST.getlist('true_list[]')
        img_seq = request.POST.get('img_seq')
        insert_label_info(true_list, img_seq)
        return JsonResponse({"remove_500": 500})
    else:
        return render(request, 'decodingapp/tongue/tongue_ai.html', {})


# True
def insert_label_info(true_list, img_seq):
    data = list(map(int, true_list)) + [img_seq]
    stmt = get_stmt('tb_tongue_label', data, 'info')
    insert_data(stmt, engine)