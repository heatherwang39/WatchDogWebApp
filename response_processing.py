def detail_processing(dic):
    out_dic = {}
    out_dic['person_num'] = dic['person_num']
    out_dic['person_info'] = []
    count = 0
    if dic['person_num'] != 0:
        for person in dic["person_info"]:
            count = count + 1
            person_attr = person["attributes"]
            person_attr_out = {}
            person_attr_out['person_id'] = count
            person_attr_out['carrying_item'] = carrying_item_tran(person_attr['carrying_item']['name'])
            person_attr_out['gender'] = gender_tran(person_attr['gender']['name'])
            person_attr_out['age'] = age_tran(person_attr['age']['name'])
            person_attr_out['bag'] = bag_tran(person_attr['bag']['name'])
            person_attr_out['smoke'] = smoke_tran(person_attr['smoke']['name'])
            person_attr_out['face_mask'] = face_mask_tran(person_attr['face_mask']['name'])
            person_location = person["location"]
            person_attr_out['location'] = {'height':int(person_location['height']), 'width':int(person_location['width']),'top':int(person_location['top']),'left':int(person_location['left'])}
            out_dic['person_info'].append(person_attr_out)
    return out_dic


def carrying_item_tran(chn):
    if chn == '无手提物':
        return 'No'
    elif chn == '有手提物':
        return 'yes'
    else:
        return 'Not sure'

def gender_tran(chn):
    if chn == '男性':
        return 'Male'
    else:
        return 'Female'

def age_tran(chn):
    if chn == '幼儿':
        return 'Child'
    elif chn == '青少年':
        return 'Teenager'
    elif chn == '青年':
        return 'Youth'
    elif chn == '中年':
        return 'Middle age'
    else:
        return 'old age'

def bag_tran(chn):
    if chn == '无背包':
        return 'No bags'
    elif chn == '单肩包':
        return 'Sling Bag'
    elif chn == '双肩包':
        return 'backpack'
    else:
        return 'Not sure'

def smoke_tran(chn):
    if chn == '吸烟':
        return 'Smoking'
    elif chn == '未吸烟':
        return 'Not Smoking'
    else:
        return 'Not Sure'

def face_mask_tran(chn):
    if chn == '戴口罩':
        return 'Wearing'
    elif chn == '无口罩':
        return 'Not Wearing'
    else:
        return 'Not Sure'
