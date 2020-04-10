import copy

from flask import render_template, request, url_for
from app import webapp
import time
import video_processing as vp
import datetime
import BaiduPeopleCounter as PC
import response_processing as RP
import image_process as ip
import S3_service as S3
import dynamodb_service as ds
import cv2
import threading
import datetime


@webapp.route('/')
def main():
    # temp for user login
    return render_template("main.html")


"""
The main page for video uploading and history checking
"""


@webapp.route('/uploader', methods=['GET', 'POST'])
def video_uploader():
    if request.method == 'POST':
        global user_id

        # Get user_id
        user_email = str(request.form['email'])
        user_id = ds.get_userID(user_email)

        # Get all previous videos belongs to that user
        video_list = ds.query_user_videos(user_id)
        format_list = []

        # format previous video list into time
        for video in video_list:
            format_time = datetime.datetime.fromtimestamp(int(video))
            format_list.append(format_time)

        # set a storage address for the new image
        filename = user_id + "/" + str(int(time.time())) + '.mp4'

        # redirect address for local
        #url = 'http://0.0.0.0:5000/Video_upload_action'
        # redirect address for lambda
        url = 'https://ax7l11065f.execute-api.us-east-1.amazonaws.com/dev/Video_upload_action'

        # set redirect address for S3
        fields = {'success_action_redirect': url}

        # Get a presigned post info
        response = S3.create_presigned_post('a3video', filename, fields={'success_action_redirect': url},
                                            conditions=[fields])

        return render_template("video_upload.html", response=response, url=url, format_list = format_list, video_list = video_list, len = len(video_list))


"""
The page for user to config the video analyzer
"""


@webapp.route('/Video_upload_action', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'GET':
        # Get all the global objects
        global filename, video_period, fps, user_id, filedir

        # Get the file_dir of the uploaded file
        filedir = request.args.get('key')

        # get the filename
        filename = filedir.split('/')[1]

        # Get the timestamp of uploading, which is the filename
        timestamp = int(filename.split('.')[0])

        # format the timestamp
        time_d = datetime.datetime.fromtimestamp(timestamp)

        # Get the info of the uploaded video
        bucket_name = 'a3video'
        video_period, fps = vp.video_info(bucket_name, filedir)
        format_period = str(datetime.timedelta(seconds=video_period))
        init_interval = max(int(video_period / 10), 1)

        # render the website
        return render_template("video_config.html", tim=time_d, Video_length=format_period,
                               init_interval=str(init_interval), video_period=str(video_period))


"""
The page for user to confirm the configuration of the video analyzer
"""


@webapp.route('/Video_config_confirm', methods=['GET', 'POST'])
def confirm_config():
    if request.method == 'POST':
        # Get global variables
        global filename, real_filename, video_period, interval, start_time, plotx, ploty, image_count, start_flag, user_id

        # Set start_flag to False to show that the video hasn't been processed yet
        start_flag = False

        # Get the start time of the video in date_time
        start = request.form['start-time']
        date = (start.split('T')[0]).split('-')
        tim = (start.split('T')[1]).split(':')
        start_t = datetime.datetime(year=int(date[0]), month=int(date[1]), day=int(date[2]), hour=int(tim[0]),
                                    minute=int(tim[1])).timestamp()
        start_time = int(start_t)
        start = datetime.datetime.fromtimestamp(start_time)

        # Get the setting of the interval length
        interval = float(request.form['interval'])

        # Calculate the estimation of the processing time
        processing_time = (video_period / interval) * 15
        format_processing_time = str(datetime.timedelta(seconds=processing_time))

        # Render the confirmation page
        return render_template("config_confirm.html", start_time=start, time=format_processing_time)


"""
Start the video analyzer and get the result from the Dynamodb
Notice: The video_number_processing will sample frames from the video according to the interval length in user's setup.
The analyzer will be triggered by file creation in S3 ended with "_unprocessed.jpg". The analyzer is a lambda function
The result of the analyzer will be written to the Dynamodb
"""


@webapp.route('/Video_processing_start', methods=['GET', 'POST'])
def video_processing_start():
    # http get
    if request.method == 'GET':

        # Set up global variables
        global filename, filedir, real_filename, video_period, interval, start_time, plotx, ploty, image_count, start_flag, fps, user_id

        # if the video hasn't been sampled yet
        if start_flag == False:
            # sample the video and save frames
            vp.video_number_processing(filedir, user_id, 'a3video', interval=interval, options=1, begin_timestamp=start_time)
            # set start_flag to be true
            start_flag = True

        # get the processed info of the video
        start_time, counters_int, finish_counters, finish_details = ds.get_start_count_finish(user_id,
                                                                                              filename.split('.')[0])

        # init parameters
        time_line = {}
        time_count = {}
        notice_count = {}
        count = 0

        # put all the samples frames index to strings
        counters_int_new = [str(index) for index in counters_int]

        # Get the people counts for each sample frame
        for key in sorted(finish_counters.keys()):
            count += 1
            frame_time = int(start_time) + int(int(key) / fps)
            time_line[str(key)] = (str(datetime.datetime.fromtimestamp(int(frame_time))))
            time_count[str(key)] = finish_counters[key]

        # Get the detail information for each sample frame
        for key in sorted(finish_details.keys()):
            notice = ""
            details = finish_details[key]
            if int(details['person_num']) != 0:
                Not_Wearing = False
                Smoke = False
                for person in details['person_info']:
                    if person['face_mask'] == 'Not Wearing':
                        Not_Wearing = True
                    if person['smoke'] == 'Smoking':
                        Smoke = True
                if Not_Wearing == True:
                    notice = notice + "Not Wearing Face Mask"
                if Smoke == True:
                    if notice == "":
                        notice = notice + "Smoking"
                    else:
                        notice = notice + ", Smoking"
            if notice == "":
                notice = "Everything is fine"
            notice_count[str(key)] = notice

        # if the completed information number doesn't equal to the required information number
        if count != len(counters_int_new):
            finish = False
        else:
            finish = True

        # Render the information page for the video
        return render_template("video_output.html", len=count, time_line=time_line, time_count=time_count,
                               finish=finish, counts=counters_int_new, notice_count=notice_count)


"""
From history
"""
@webapp.route('/Video_processing_history', methods=['GET', 'POST'])
def video_processing_history():
    # http get
    if request.method == 'POST':
        # Set up global variables
        global filename, filedir, real_filename, video_period, interval, start_time, plotx, ploty, image_count, start_flag, fps, user_id

        filename = request.form['filename']

        # get the processed info of the video
        start_time, counters_int, finish_counters, finish_details = ds.get_start_count_finish(user_id, filename)

        # video address
        vid_adr = user_id+"/"+filename+".mp4"
        period, fps = vp.video_info('a3video',vid_adr)

        # init parameters
        time_line = {}
        time_count = {}
        notice_count = {}
        count = 0

        # put all the samples frames index to strings
        counters_int_new = [str(index) for index in counters_int]

        # Get the people counts for each sample frame
        for key in sorted(finish_counters.keys()):
            count += 1
            frame_time = int(start_time) + int(int(key) / fps)
            time_line[str(key)] = (str(datetime.datetime.fromtimestamp(int(frame_time))))
            time_count[str(key)] = finish_counters[key]

        # Get the detail information for each sample frame
        for key in sorted(finish_details.keys()):
            notice = ""
            details = finish_details[key]
            if int(details['person_num']) != 0:
                Not_Wearing = False
                Smoke = False
                for person in details['person_info']:
                    if person['face_mask'] == 'Not Wearing':
                        Not_Wearing = True
                    if person['smoke'] == 'Smoking':
                        Smoke = True
                if Not_Wearing == True:
                    notice = notice + "Not Wearing Face Mask"
                if Smoke == True:
                    if notice == "":
                        notice = notice + "Smoking"
                    else:
                        notice = notice + ", Smoking"
            if notice == "":
                notice = "Everything is fine"
            notice_count[str(key)] = notice

        # if the completed information number doesn't equal to the required information number
        if count != len(counters_int_new):
            finish = False
        else:
            finish = True

        # Render the information page for the video
        return render_template("video_output.html", len=count, time_line=time_line, time_count=time_count,
                               finish=finish, counts=counters_int_new, notice_count=notice_count)


"""
Detail information for a single frame
"""


@webapp.route('/Video_detail', methods=['GET', 'POST'])
def video_details():
    if request.method == 'POST':
        global filename, user_id

        # Get the clicked image index
        image_count = int(request.form['image_name'])

        # the timestamp of the video
        timestamp = filename.split('.')[0]

        # the address of the unprocessed frame
        image_addr_s = user_id + '/' + timestamp + "/%d_unprocessed.jpg" % image_count

        # the address of the future processed frame
        finish_addr_s = user_id + '/' + timestamp + "/%d_processed.jpg" % image_count
        finish_addr = "https://a3video.s3.amazonaws.com/" + finish_addr_s

        # Get the detail information of that frame
        start_time, counters_int, finish_counters, finish_details = ds.get_start_count_finish(user_id,
                                                                                              filename.split('.')[0])
        processed_response = finish_details[str(image_count)]

        # Label the target on the frame
        ip.image_labeling(image_addr_s, processed_response['person_info'], finish_addr_s)

        # Render the detailed frames
        return render_template("video_detail.html", processed_address=finish_addr,
                               person_num=processed_response['person_num'],
                               person_list=processed_response['person_info'])
