
from flask import render_template, request
from app import webapp
import time
import video_processing as vp
from datetime import timedelta
import ciso8601
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
      filename = str(int(time.time()))
      real_filename = f.filename
      filedir = "app/static/"+filename+".mp4"
      f.save(filedir)
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
      processing_time = (video_period/interval)*30
      format_processing_time = str(timedelta(seconds=processing_time))
      return render_template("config_confirm.html", start_time = start, time = format_processing_time)

@webapp.route('/Video_processing_start', methods = ['GET', 'POST'])
def video_processing_start():
   if request.method == 'POST':
      global filename, filedir, real_filename, video_period, interval, start_time
      plotx, ploty = vp.video_number_processing(filename, filedir, interval=interval, options=1, begin_timestamp=start_time)
      return render_template("video_output.html", len = len(plotx), plotx = plotx, ploty = ploty)
