import video_processing as VP
import os
import time
from datetime import datetime

# dt = datetime(2020, 4, 4, 12, 30, 49)
# dtstamp = dt.timestamp()
# print(time.ctime(dtstamp))
# dtstamp = dt.timestamp() + 400
# print(time.ctime(dtstamp))
start = time.time()
statinfo = os.path.getctime("project.mp4")
VP.video_processing('project.mp4', 40, 1, end_timestamp=statinfo)
end = time.time()
period = int(end - start)
print("execution time: "+str(period)+" seconds")

