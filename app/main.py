import copy

from flask import render_template, request
from app import webapp
import time
import video_processing as vp
from datetime import timedelta
import BaiduPeopleCounter as PC
import ciso8601
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
    return render_template("video_upload.html")


@webapp.route('/Video_upload_action', methods = ['GET', 'POST'])
def upload_file():
   if request.method == 'POST':
      global filename, filedir, real_filename, video_period
      f = request.files['file']
      print(type(f))
      filename = str(int(time.time()))
      real_filename = f.filename
      f.seek(0)
      filedir = "app/static/"+filename+".mp4"
      f.save(filedir)
      #S3.upload_file(f, filename=filename+".mp4")
      video_period = vp.video_info(filedir)
      format_period = str(timedelta(seconds=video_period))
      return render_template("video_config.html", filename = real_filename, Video_length = format_period)

@webapp.route('/Video_config_confirm', methods = ['GET', 'POST'])
def confirm_config():
   if request.method == 'POST':
      global filename, filedir, real_filename, video_period, interval, start_time
      start = request.form['start-time']
      start_t = ciso8601.parse_datetime(start)
      start_time = int(time.mktime(start_t.timetuple()))
      interval = float(request.form['interval'])
      processing_time = (video_period/interval)*15
      format_processing_time = str(timedelta(seconds=processing_time))
      return render_template("config_confirm.html", start_time = start, time = format_processing_time)

@webapp.route('/Video_processing_start', methods = ['GET', 'POST'])
def video_processing_start():
   if request.method == 'POST':
      global filename, filedir, real_filename, video_period, interval, start_time, plotx, ploty, image_count
      plotx, ploty, image_count = vp.video_number_processing(filename, filedir, interval=interval, options=1, begin_timestamp=start_time)
      return render_template("video_output.html", len = len(plotx), plotx = plotx, ploty = ploty, image_count = image_count)

@webapp.route('/Video_detail', methods = ['GET', 'POST'])
def video_details():
   if request.method == 'POST':
      global filename
      image_count = int(request.form['image_name'])
      image_addr = "app/static/"+filename+"/frame%d.jpg" % image_count
      Processed_image_addr = "static/"+filename+"_processed/frame%d.jpg" % image_count
      response = PC.people_details(image_addr)
      processed_response = RP.detail_processing(response)
      ip.image_labeling("app/"+Processed_image_addr,processed_response['person_info'])
      return render_template("video_detail.html", processed_address = Processed_image_addr, person_num = processed_response['person_num'], person_list=processed_response['person_info'])