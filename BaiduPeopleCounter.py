# encoding:utf-8
import requests
import base64
import timeit
import cv2
import numpy as np
import image_process as IP
import S3_service as S3
'''
人流量统计
'''

def BaiduImageProcessing(dirDir):

    request_url = "https://aip.baidubce.com/rest/2.0/image-classify/v1/body_attr"
    request_url_num = "https://aip.baidubce.com/rest/2.0/image-classify/v1/body_num"
    # 二进制方式打开图片文件
    f = open(dirDir, 'rb')
    img = base64.b64encode(f.read())

    typ = "gender,age,bag,smoke,face_mask,carrying_item"
    access_token = '24.ddcfced251cc6d32aa4ab615c7760067.2592000.1588622521.282335-19264077'
    headers = {'content-type': 'application/x-www-form-urlencoded'}

    params_num = {"image":img, "show":"true"}
    request_url_num = request_url_num + "?access_token=" + access_token
    response_num = requests.post(request_url_num, data=params_num, headers=headers)
    img_out = None
    ret_num = None
    if response_num:
        ret_num = response_num.json()
        img_out = IP.cv_from_64(ret_num["image"])
        print("Detected People: "+str(ret_num["person_num"]))

    params = {"image":img, "type":typ}
    request_url = request_url + "?access_token=" + access_token
    response = requests.post(request_url, data=params, headers=headers)
    ret = None
    if response:
        ret = response.json()
        print("Detailed Detected People: "+str(ret["person_num"]))
        print()
        count = 0
        for people in ret["person_info"]:
            count += 1
            print("person: "+str(count))
            attrs = people["attributes"]
            for attr in attrs:
                print(attr+": "+attrs[attr]['name'])
            print()
    return img_out,ret,ret_num

def people_counting(img, image = True):
    request_url_num = "https://aip.baidubce.com/rest/2.0/image-classify/v1/body_num"
    access_token = '24.ddcfced251cc6d32aa4ab615c7760067.2592000.1588622521.282335-19264077'
    headers = {'content-type': 'application/x-www-form-urlencoded'}

    if image == True:
        params_num = {"image": img, "show": "true"}
    else:
        params_num = {"image": img}
    request_url_num = request_url_num + "?access_token=" + access_token
    response_num = requests.post(request_url_num, data=params_num, headers=headers)
    img_out = None
    count = 0
    if response_num:
        ret = response_num.json()
        count = ret["person_num"]
        if image == True:
            img_out = IP.cv_from_64(ret["image"])
    return count, img_out

def people_details(dirDir, dir_short):

    if S3.file_setpublic('a3user',dir_short):
        request_url = "https://aip.baidubce.com/rest/2.0/image-classify/v1/body_attr"
        f = S3.get_image('a3user',dir_short)
        img = base64.b64encode(f.read())
        typ = "gender,age,bag,smoke,face_mask,carrying_item"
        access_token = '24.ddcfced251cc6d32aa4ab615c7760067.2592000.1588622521.282335-19264077'
        headers = {'content-type': 'application/x-www-form-urlencoded'}
        params = {"image": img, "type": typ}
        request_url = request_url + "?access_token=" + access_token
        response = requests.post(request_url, data=params, headers=headers)
        if response:
            ret = response.json()
            if S3.file_setprivate('a3user',dir_short):
                print(ret)
                return ret