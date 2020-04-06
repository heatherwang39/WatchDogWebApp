import base64
import cv2
import numpy as np
import BaiduPeopleCounter as BD

"""
Convert opencv file into byte64 file
"""
def cv_to_64(img_cv):
    retval, buffer = cv2.imencode('.jpg', img_cv)
    img_64 = base64.b64encode(buffer)
    return img_64


"""
Convert byte64 file into opencv file
"""
def cv_from_64(img_64):
    b = bytes(img_64, 'utf-8')
    img_b64decode = base64.b64decode(b)
    img_array = np.frombuffer(img_b64decode, np.uint8)
    img_out = cv2.imdecode(img_array, cv2.COLOR_BGR2RGB)
    return img_out