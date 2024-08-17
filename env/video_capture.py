import cv2, queue, threading, time


# bufferless VideoCapture
class VideoCapture:
  def __init__(self, camera_id=0, flip_method=2, width=128, height=128):
    self.stream = cv2.VideoCapture(
      self.__gstreamer_pipeline(
        camera_id=camera_id,
        flip_method=flip_method,
        capture_width=width,
        capture_height=height,
        display_width=width,
        display_height=height
      ),
      cv2.CAP_GSTREAMER
    )

  def __gstreamer_pipeline(
    self,
    camera_id,
    capture_width=1920,
    capture_height=1080,
    display_width=1920,
    display_height=1080,
    framerate=30,
    flip_method=0,
  ):
    pipeline = (
      "nvarguscamerasrc sensor-id=%d ! "
      "video/x-raw(memory:NVMM), "
      "width=(int)%d, height=(int)%d, "
      "format=(string)NV12, framerate=(fraction)%d/1 ! "
      "nvvidconv flip-method=%d ! "
      "video/x-raw, width=(int)%d, height=(int)%d, format=(string)BGRx ! "
      "videoconvert ! "
      "video/x-raw, format=(string)BGR ! appsink max-buffers=1 drop=True"
      % (
        camera_id,
        capture_width,
        capture_height,
        framerate,
        flip_method,
        display_width,
        display_height,
      )
    )
    return pipeline

  def read(self):
    _, frame = self.stream.read()
    return frame

  