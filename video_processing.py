import cv2
import image_process as IP
import BaiduPeopleCounter as BP
from datetime import datetime, timedelta
import S3_service as S3
import time
import boto3
import dynamodb_service as ds
import matplotlib.pyplot as plt
import os
"""
processing a video file given a filename and a interval in seconds

int options: 
  0: no process, only save interval images
  1: get the number of people in the video
  2: get detailed information of people in the video

begin_timestamp (optional):
  start time of the video
"""

def video_info(bucket_name,keyname):
    if S3.file_setpublic(bucket_name,keyname):
        vim = cv2.VideoCapture('https://'+bucket_name+'.s3.amazonaws.com/'+keyname)
        fps = vim.get(cv2.CAP_PROP_FPS)
        period = vim.get(cv2.CAP_PROP_FRAME_COUNT) / fps
    if S3.file_setprivate(bucket_name,keyname):
        return period,fps

def video_number_processing(file_name,bucket_name, interval, options, begin_timestamp=-1):
    file_dir = 'https://'+bucket_name+'.s3.amazonaws.com/'+file_name
    image_addr = []
    if S3.file_setpublic(bucket_name,file_name):
        vidcap = cv2.VideoCapture(file_dir)
        count = 0
        fps = vidcap.get(cv2.CAP_PROP_FPS)
        period = vidcap.get(cv2.CAP_PROP_FRAME_COUNT) / fps
        print("Video started at " + str(datetime.fromtimestamp(int(begin_timestamp))))
        interval_frames = interval * fps
        timestamp = file_name.split('.')[0]
        samples = [int(index * interval_frames) for index in range(int(period / interval))]
        ds.put_user_video('temp', file_name.split('.')[0], samples, {},{}, begin_timestamp)
        while True:
          success, image = vidcap.read()
          if not success:
            break
          if count % interval_frames == 0:
            image_addr.append(count)
            S3.upload_cvimage(image, "%d_unprocessed.jpg" % count, file_directory='temp'+"/"+timestamp + "/")
          count += 1
    if S3.file_setprivate(bucket_name,file_name):
        return

def video_processing(file_name, interval, options, end_timestamp = -1):

  vidcap = cv2.VideoCapture(file_name)
  count = 0
  fps = vidcap.get(cv2.CAP_PROP_FPS)
  period = vidcap.get(cv2.CAP_PROP_FRAME_COUNT)/fps
  begin_timestamp = end_timestamp-period
  print("Video started at "+str(datetime.fromtimestamp(int(begin_timestamp))))
  interval_frames = interval * fps
  plotx = []
  ploty = []
  while True:
    success, image = vidcap.read()
    if not success:
      break
    if count%interval_frames == 0:
      cv2.imwrite("temp/frame%d.jpg" % count, image)  # save frame as JPEG file
      if options == 1:
        img_64 = IP.cv_to_64(image)
        people_num = BP.people_counting(img_64)[0]
        frame_time = begin_timestamp+count/fps
        print("At "+ str(datetime.fromtimestamp(int(frame_time))) + ", there are "+ str(people_num)+" people")
        plotx.append(str(datetime.fromtimestamp(int(frame_time)).time()))
        ploty.append(int(people_num))
      elif options == 2:
        img_64 = IP.cv_to_64(image)
        people_num, img_out = BP.people_counting(img_64, image=True)
        frame_time = begin_timestamp+count/fps
        print("At "+ str(datetime.fromtimestamp(int(frame_time))) + ", there are "+ str(people_num)+" people")
        cv2.imwrite("temp/frame%d_processed.jpg" % count, img_out)
        detail_num, dic_people = BP.people_details(img_64)
        print("Able to analysis "+str(detail_num)+" people in detail")
        inner_count = 0
        for people in dic_people:
            inner_count += 1
            print("\tperson: " + str(inner_count))
            attrs = people["attributes"]
            for attr in attrs:
                print("\t \t"+attr + ": " + attrs[attr]['name'])
            print()
    count += 1
  plt.title(label=file_name + " on " +str(datetime.fromtimestamp(int(begin_timestamp)).date()))
  plt.plot(plotx, ploty)
  plt.axis((min(plotx), max(plotx), 0, max(ploty)*1.25))
  plt.savefig("processed_plot.png")