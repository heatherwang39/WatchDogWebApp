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
    return render_template("main.html")
    
@webapp.route('/uploader', methods = ['GET', 'POST'])
def video_uploader():
    if request.method == 'POST':
       global user_id
       user_id = str(request.form['UserID'])
       print(user_id)
       filename = str(int(time.time()))+'.mp4'
       url = 'http://0.0.0.0:5000/Video_upload_action'
       #url = 'https://ax7l11065f.execute-api.us-east-1.amazonaws.com/dev/Video_upload_action'
       fields = {'success_action_redirect': url}
       response = S3.create_presigned_post('a3video', filename, fields={'success_action_redirect':url}, conditions=[fields])
       print(response)
       return render_template("video_upload.html",response = response, url = url)

@webapp.route('/Video_upload_action', methods = ['GET', 'POST'])
def upload_file():
   if request.method == 'GET':
      global filename, video_period,fps
      filename = request.args.get('key')
      timestamp = int(filename.split('.')[0])
      time_d = datetime.datetime.fromtimestamp(timestamp)
      bucket_name = 'a3video'
      video_period,fps = vp.video_info(bucket_name,filename)
      format_period = str(datetime.timedelta(seconds=video_period))
      init_interval = max(int(video_period/10),1)
      return render_template("video_config.html", tim = time_d, Video_length = format_period, init_interval = str(init_interval), video_period = str(video_period))

@webapp.route('/Video_config_confirm', methods = ['GET', 'POST'])
def confirm_config():
   if request.method == 'POST':
      global filename, real_filename, video_period, interval, start_time, plotx, ploty, image_count, start_flag
      start_flag = False
      start = request.form['start-time']
      Date = (start.split('T')[0]).split('-')
      tim = (start.split('T')[1]).split(':')
      start_t = datetime.datetime(year=int(Date[0]),month=int(Date[1]),day=int(Date[2]),hour=int(tim[0]),minute=int(tim[1])).timestamp()
      start_time = int(start_t)
      start = datetime.datetime.fromtimestamp(start_time)
      interval = float(request.form['interval'])
      processing_time = (video_period/interval)*15
      format_processing_time = str(datetime.timedelta(seconds=processing_time))
      return render_template("config_confirm.html", start_time = start, time = format_processing_time)

@webapp.route('/Video_processing_start', methods = ['GET', 'POST'])
def video_processing_start():
   if request.method == 'GET':
      global filename, filedir, real_filename, video_period, interval, start_time, plotx, ploty, image_count, start_flag, fps
      if start_flag == False:
         vp.video_number_processing(filename, 'a3video', interval=interval, options=1, begin_timestamp=start_time)
         start_flag = True
      start_time, counters_int,finish_counters, finish_details = ds.get_start_count_finish('temp',filename.split('.')[0])
      time_line = {}
      time_count = {}
      notice_count = {}
      count = 0
      counters_int_new = [str(index) for index in counters_int]
      for key in sorted(finish_counters.keys()):
         count += 1
         frame_time = int(start_time) + int(int(key) / fps)
         time_line[str(key)] = (str(datetime.datetime.fromtimestamp(int(frame_time))))
         time_count[str(key)] = finish_counters[key]

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
      if count != len(counters_int_new):
         finish = False
      else:
         finish = True
      return render_template("video_output.html", len = count, time_line = time_line, time_count = time_count, finish = finish, counts = counters_int_new, notice_count = notice_count)

@webapp.route('/Video_detail', methods = ['GET', 'POST'])
def video_details():
   if request.method == 'POST':
      global filename
      image_count = int(request.form['image_name'])
      timestamp = filename.split('.')[0]
      image_addr_s = 'temp/'+timestamp + "/%d_unprocessed.jpg" % image_count
      image_addr = "https://a3video.s3.amazonaws.com/"+ image_addr_s
      finish_addr_s = 'temp/' + timestamp + "/%d_processed.jpg" % image_count
      finish_addr = "https://a3video.s3.amazonaws.com/" + finish_addr_s
      start_time, counters_int, finish_counters, finish_details = ds.get_start_count_finish('temp', filename.split('.')[0])
      processed_response = finish_details[str(image_count)]
      ip.image_labeling(image_addr_s,processed_response['person_info'], finish_addr_s)
      return render_template("video_detail.html", processed_address = finish_addr, person_num = processed_response['person_num'], person_list=processed_response['person_info'])

