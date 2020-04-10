import base64
import cv2
import numpy as np
import BaiduPeopleCounter as BD
import random
import S3_service as S3

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

def cv_from_file(f):
    img_array = np.frombuffer(f.read(), np.uint8)
    img_out = cv2.imdecode(img_array, cv2.COLOR_BGR2RGB)
    return img_out

def image_labeling(image_dir_s, response_person, finish_dir_s):
    if S3.file_setpublic('a3video',image_dir_s):
        f = S3.get_image('a3video', image_dir_s)
        image = cv_from_file(f)
        for people in response_person:
            location = people['location']
            (x,y) = (location['left'],location['top'])
            (w,h) = (location['width'],location['height'])
            COLORS = (random.randint(0,255), random.randint(0,255), random.randint(0,255))
            cv2.rectangle(image, (x, y), (x + w, y + h), COLORS, 2)
            text = str(people['person_id'])
            cv2.putText(image, text, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX,
                        0.5, COLORS, 2)
        #cv2.imwrite(image_dir,image)
        S3.upload_cvimage(image, finish_dir_s, file_directory="")
    if S3.file_setpublic('a3video', finish_dir_s):
        return