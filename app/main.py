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
import cv2
import datetime

@webapp.route('/')
def main():
    return render_template("main.html")
    
@webapp.route('/uploader')
def video_uploader():
    filename = str(int(time.time()))+'.mp4'
    url = 'http://0.0.0.0:5000/Video_upload_action'
    #url = 'https://ax7l11065f.execute-api.us-east-1.amazonaws.com/dev/Video_upload_action'
    fields = {'success_action_redirect': url}
    response = S3.create_presigned_post('a3user', filename, fields={'success_action_redirect':url}, conditions=[fields])
    print(response)
    return render_template("video_upload.html",response = response, url = url)


@webapp.route('/Video_upload_action', methods = ['GET', 'POST'])
def upload_file():
   if request.method == 'GET':
      global filename, video_period
      filename = request.args.get('key')
      timestamp = int(filename.split('.')[0])
      time_d = datetime.datetime.fromtimestamp(timestamp)
      bucket_name = 'a3user'
      video_period = vp.video_info(bucket_name,filename)
      format_period = str(datetime.timedelta(seconds=video_period))
      init_interval = max(int(video_period/10),1)
      return render_template("video_config.html", tim = time_d, Video_length = format_period, init_interval = str(init_interval), video_period = str(video_period))

@webapp.route('/Video_config_confirm', methods = ['GET', 'POST'])
def confirm_config():
   if request.method == 'POST':
      global filename, real_filename, video_period, interval, start_time
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
   if request.method == 'POST':
      global filename, filedir, real_filename, video_period, interval, start_time, plotx, ploty, image_count
      plotx, ploty, image_count = vp.video_number_processing(filename, 'a3user', interval=interval, options=1, begin_timestamp=start_time)
      return render_template("video_output.html", len = len(plotx), plotx = plotx, ploty = ploty, image_count = image_count)

@webapp.route('/Video_detail', methods = ['GET', 'POST'])
def video_details():
   if request.method == 'POST':
      global filename
      image_count = int(request.form['image_name'])
      timestamp = filename.split('.')[0]
      image_addr_s = timestamp + "/frame%d.jpg" % image_count
      image_addr = "https://a3user.s3.amazonaws.com/"+ image_addr_s
      Processed_image_addr_short = timestamp + "_processed/frame%d.jpg" % image_count
      Processed_image_addr = "https://a3user.s3.amazonaws.com/"+ Processed_image_addr_short
      response = PC.people_details(image_addr, image_addr_s)
      processed_response = RP.detail_processing(response)
      ip.image_labeling(Processed_image_addr,processed_response['person_info'], Processed_image_addr_short)
      return render_template("video_detail.html", processed_address = Processed_image_addr, person_num = processed_response['person_num'], person_list=processed_response['person_info'])


