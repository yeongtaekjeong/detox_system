from flask import request, Response
from flask_restx import Resource, Namespace, fields

import json
import os
import io
import base64

import torch
import cv2
import numpy as np

from PIL import Image, ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True

from ultralytics import YOLO


############################# Name Space ###########################
Todo = Namespace('predict_api', description= 'Predict API')

predict_tongue = Todo.model('Predict_Tongue',
                {   'image_path': fields.String(required=True,
                            description= """Image Path""",),
                    'save_path': fields.String(required=True,
                            description= """Save Path""",)
                })

segment_tongue = Todo.model('Segmen_Tongue',
                {   'image_path': fields.String(required=True,
                            description= """Image Paths""",),
                    'save_path': fields.String(required=True,
                            description= """Save Paths""",)
                })

############################# CNN Model ###########################
class CNN(torch.nn.Module):
    # B: Batch_size, X: Image_size, C: Channel_size
    def __init__(self, input_size, middle_outputs, final_outputs):
        super(CNN, self).__init__()
        self.keep_prob = 0.5

        # L1 ImgIn shape = (B, 3, X, X)
        #    Conv       -> (B, 32, X, X)
        #    Pool       -> (B, 32, X/2, X/2)
        self.layer1 = torch.nn.Sequential(
            torch.nn.Conv2d(3, 32, kernel_size= 3, stride= 1, padding= 1),
            torch.nn.ReLU(),
            torch.nn.MaxPool2d(kernel_size= 2, stride= 2))

        # L2 ImgIn shape = (B, 32, X/2, X/2)
        #    Conv       -> (B, 64, X/2, X/2)
        #    Pool       -> (B, 64, X/4, X/4)
        self.layer2 = torch.nn.Sequential(
            torch.nn.Conv2d(32, 64, kernel_size= 3, stride= 1, padding= 1),
            torch.nn.ReLU(),
            torch.nn.MaxPool2d(kernel_size= 2, stride= 2))

        # L3 ImgIn shape = (B, 64, X/4, X/4)
        #    Conv       -> (B, 128, X/4, X/4)
        #    Pool       -> (B, 128, X/8, X/8)
        self.layer3 = torch.nn.Sequential(
            torch.nn.Conv2d(64, 128, kernel_size= 3, stride= 1, padding= 1),
            torch.nn.ReLU(),
            torch.nn.MaxPool2d(kernel_size= 2, stride= 2))
        
        # L4 FC x/8 * x/8 * 128 -> middle_outputs
        self.fc1 = torch.nn.Linear(input_size//8 * input_size//8 * 128, middle_outputs, bias= True)
        torch.nn.init.kaiming_uniform_(self.fc1.weight)
        self.layer4 = torch.nn.Sequential(
            self.fc1,
            torch.nn.ReLU(),
            torch.nn.Dropout(p= 1-self.keep_prob))
        
        # L5 Final FC middle_outputs -> final_outputs
        self.fc2 = torch.nn.Linear(middle_outputs, final_outputs, bias= True)
        torch.nn.init.kaiming_uniform_(self.fc2.weight)

    def forward(self, x):
        out = self.layer1(x)
        out = self.layer2(out)
        out = self.layer3(out)
        out = out.view(out.size(0), -1) # Flatten them for FC
        out = self.layer4(out)
        out = self.fc2(out)
        return out

############################# Varible ###########################
tongue_color = {0: '담홍설', 1: '담백설', 2:'홍설', 3: '강설', 4:' 자설'}
tongue_coating = {0: '무태', 1: '박백태', 2: '백태', 3: '황태', 4: '회태', 5: '흑태'}
is_or_not = {1: '유', 0: '무'}

model_list = {0: ['설질(색)', 5, 32, 425], 3: ['어반', 2, 64, 75], 4: ['치흔', 2, 128, 250], 
            5: ['대장_설태', 6, 32, 625], 6: ['대장_설반', 2, 48, 425], 7: ['위장_설태', 6, 64, 250],
            8: ['위장_설열', 2, 64, 125], 9: ['심장_설열', 2, 32, 75],
            10: ['폐_설태', 6, 32, 625], 11: ['폐_설열', 2, 128, 75], 12: ['폐_설반', 2, 32, 625], 
            13: ['설첨_홍', 2, 32, 75], 14: ['설첨_설반', 2, 32, 125]}

############################# Load Model ###########################
for model_num, model_file_name in zip(dict(sorted(model_list.items(), key= lambda x: x[0])), 
                                    sorted(os.listdir('./models/best_models/'), key= lambda x: int(x.split('_')[0][5:]))):
    device = torch.device('cpu')
    model_info = model_list[model_num]
    # img_size, middle_output_size, number of class
    globals()[f'model_pred_{model_num}'] = CNN(model_info[2], model_info[3], model_info[1]).to(device)
    globals()[f'model_pred_{model_num}'].load_state_dict(torch.load(f'./models/best_models/{model_file_name}', map_location= device))

def _predict_image(img, pred_model, model_num):
    img_size = model_list[model_num][2]
    img_array = np.array(img)

    img = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
    img = cv2.resize(img, (img_size, img_size))

    background = np.where((img[:, :, 0] <= 30) & (img[:, :, 1] <= 30) & (img[:, :, 2] <= 30))
    img[background] = 0

    img_tensor = torch.from_numpy(img)
    img_tensor = img_tensor.permute(2, 0, 1)
    img_tensor = img_tensor.to(dtype= torch.float32)

    X_single_data = img_tensor
    X_single_data = X_single_data.reshape((1,) + X_single_data.shape)

    pred_model.eval()
    with torch.no_grad():
        single_prediction = pred_model(X_single_data)
        prediction = torch.argmax(single_prediction, 1).item()

    return prediction

def _get_crack_coating(coatings):
    for coating in range(5, -1, -1):
        if coating in coatings:
            return coating

def get_label_info(img):
    label_info = dict()
    label_info["predict_list"] = [0] * (len(model_list) + 2)
    for model_num in model_list:
        predict = _predict_image(img, globals()[f'model_pred_{model_num}'], model_num)
        label_info["predict_list"][model_num] = predict

    coatings = [label_info["predict_list"][7], label_info["predict_list"][10]]
    label_info["predict_list"][1] = _get_crack_coating(coatings)

    crakcs = [label_info["predict_list"][8], label_info["predict_list"][9], label_info["predict_list"][11]]
    label_info["predict_list"][2] = int(any(crakcs))

    return label_info

############################# YOLOv8x-seg ###########################

weights = './models/bestl_2658.pt'
model_seg = YOLO(weights)

def segment_tongue(img):
    img = img.resize((640, 640))

    result = model_seg(img)[0]
    mask = result.masks.numpy()
    masks = mask.data.astype(bool)

    point_locas = np.where(masks == True)[1:]
    x, y, dx, dy = min(point_locas[0]), min(point_locas[1]), max(point_locas[0]), max(point_locas[1])

    img = result.orig_img
    for m in masks:
        new = np.zeros_like(img, dtype= np.uint8)
        new[m] = img[m]
    new = new[x:dx, y:dy, :]
    new = new[:, :, ::-1]
    img = cv2.resize(new, (512, 512))
    img = Image.fromarray(img.astype('uint8'))

    return img

############################ POST #################################
@Todo.route('/Predict_Tongue')
class searchPost1(Resource):
    @Todo.expect(predict_tongue)
    def post(self):
        img_file = request.files['File']
        img = Image.open(img_file)
        seg_image = segment_tongue(img)

        label_info = get_label_info(seg_image)
        response = json.dumps(label_info, ensure_ascii= False).encode('utf-8')
        return Response(response, content_type='application/json; charset=utf-8')

@Todo.route('/Segment_Tongue')
class searchPost2(Resource):
    @Todo.expect(segment_tongue)
    def post(self):
        img_file = request.files['File']
        img = Image.open(img_file)
        seg_image = segment_tongue(img)

        file_object = io.BytesIO()
        seg_image.save(file_object, 'JPEG')
        file_object.seek(0)

        img_data = base64.b64encode(file_object.getvalue()).decode()
        return f'data:image/jpeg;base64,{img_data}'