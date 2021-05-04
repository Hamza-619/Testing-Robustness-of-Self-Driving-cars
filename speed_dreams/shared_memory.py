import mmap
import ctypes
import numpy as np
import cv2
import math
import os
import datetime
import time

# TODO Investigate why the memory is SO slow !

from .data_types import Data_t, RECORD_MEMORY_NAME, RECORD_IMAGE_CHANNELS, RECORD_MAX_IMAGE_HEIGHT, RECORD_MAX_IMAGE_WIDTH

class CSharedMemory():
  TARGET_IMAGE_CHANNELS = RECORD_IMAGE_CHANNELS
  memory_location= None

  def __init__(self, TargetResolution = [640, 480], memory_location=RECORD_MEMORY_NAME):
    """
    Creates a Shared-Memory class.

    Keyword arguments:
       TargetResolution: The needed resolution of the image (default 640x480 px)
    """
    self._IsPauseOn = False
    self._TargetResolution = TargetResolution

    Size = ctypes.sizeof(Data_t)
    self._SharedMemoryFile = None

    self.memory_location = memory_location
    print("SHM Location is ", memory_location)

    if os.name == "nt":
        self._SharedMemory = mmap.mmap(-1, Size, memory_location)

    else:
        Filename = os.path.join("/", "dev", "shm", memory_location)
        self._SharedMemoryFile = open(Filename, "w+b")
        self._SharedMemoryFile.write(b"\0"*Size)
        self._SharedMemoryFile.flush()
        self._SharedMemory = mmap.mmap(self._SharedMemoryFile.fileno(), Size)

    self._Data = Data_t.from_buffer(self._SharedMemory)
    self._Image = np.empty(shape=TargetResolution + [self.TARGET_IMAGE_CHANNELS])
    self._RawImage = np.empty(shape=TargetResolution + [self.TARGET_IMAGE_CHANNELS])


  def __del__(self):
    self.Data.Sync.IsPauseOn = 0
    self.Data.Control.IsControlling = 0

    if self._SharedMemoryFile is not None:
      self._SharedMemoryFile.close()


  def setSyncMode(self, IsPauseOn = True):
    """
    Enables or disables the pause mode (Speed-Dreams waits with
    new data until old data have been read).

    Keyword arguments:
      IsPauseOn: Indicates, if pause mode should be enabled or disabled.
    """
    self._IsPauseOn = IsPauseOn

  frameNumber = 0
  def store_to_file(self, Image):
    if self.frameNumber % 1 == 0:
      cv2.imwrite(os.path.join('original', str(self.frameNumber) + ".png"), Image)
      print("Stored images", self.frameNumber)
    self.frameNumber = self.frameNumber + 1

  def read(self):
    """
    Checks if new data is available and read an image from the memory if possible.

    :return: Returns True if data can be read.
    """
    if self.Data.Sync.IsWritten == 1:

      if self._IsPauseOn:
        self.Data.Sync.IsPauseOn = 1
      else:
        self.Data.Sync.IsPauseOn = 0

      Width       = self.Data.Image.ImageWidth
      Height      = self.Data.Image.ImageHeight

      # Image = np.fromstring(self.Data.Image.Data, np.uint8, Width * Height * self.TARGET_IMAGE_CHANNELS)
      Image = np.frombuffer(self.Data.Image.Data, np.uint8, Width * Height * self.TARGET_IMAGE_CHANNELS)
      Image = Image.reshape(Height, Width, self.TARGET_IMAGE_CHANNELS)

      AspectRatio = Width / Height
      TargetWidth = int(self._TargetResolution[1] * AspectRatio)

      if TargetWidth >= self._TargetResolution[0]:
        if Width != TargetWidth or Height != self._TargetResolution[1]:
          Image = cv2.resize(Image, (TargetWidth, self._TargetResolution[1]))

        if TargetWidth != self._TargetResolution[0]:
          XStart = int(TargetWidth/2 - self._TargetResolution[0]/2)
          XStop  = int(TargetWidth/2 + self._TargetResolution[0]/2)
          Image = Image[:, XStart:XStop]

      else:
        TargetHeight = int(self._TargetResolution[0]/AspectRatio)

        if Width != self._TargetResolution[0] or Height != TargetHeight:
          Image = cv2.resize(Image, (self._TargetResolution[1], TargetHeight))

          if TargetHeight != self._TargetResolution[1]:
            YStart = int(TargetHeight/2 - self._TargetResolution[1]/2)
            YStop  = int(TargetHeight/2 + self._TargetResolution[1]/2)
            Image = Image[YStart:YStop, :]

      # Shall we convert this to 0 - 1 ?
      self._RawImage = Image
      self._Image = cv2.flip(Image, 0)

      # This one does not flip the image, but it rotate and crop !!
      # self._Image = np.array(cv2.flip(Image, 0)/255, dtype=np.float32)
      # self._Image = cv2.flip(Image, 0)


      # This one is flipped upside/down
      # print("Image from memory reshaped as WxH with Mean", Width, Height, np.mean((self._Image), axis=(0, 1)))
      # self.store_to_file(self._Image)

      return True

    return False


  _mWriteNumber = 0
  def indicateWrite(self):
    self._mWriteNumber = self._mWriteNumber+1
    self.Data.Sync.WriteNumber = self._mWriteNumber
    self.Data.Sync.IsWritten = 1

  def waitOnRead(self):
    # print('Wait on Read ', self.Data.Sync.IsWritten, self.Data.Sync.IsPauseOn)
    while self.Data.Sync.IsWritten and self.Data.Sync.IsPauseOn:
      time.sleep(0.001)

  def indicateReady(self):
    """
    Indicates to Speed-Dreams, that the reader is ready.
    """
    self.Data.Sync.IsWritten = 0

  def write(self, Width, Height, ImageData, Speed, angle, min_dist, fast,min_dist_left, min_dist_right, ego_min_dis_right, ego_min_dis_left, vehicle_dis_in_current, vehicle_dis_in_left):
    """
    Enable to check if a new image can be written to memory.d
    :return: True if a new image can and was written
    """
    # write_begin = datetime.datetime.now()

    self.Data.Game.Speed = Speed
    self.Data.Labels.Angle = angle
    self.Data.Labels.M = min_dist
    self.Data.Labels.Fast = fast
    self.Data.Labels.LL = min_dist_left
    self.Data.Labels.RR = min_dist_right
    self.Data.Labels.L = ego_min_dis_left
    self.Data.Labels.R = ego_min_dis_right
    self.Data.Labels.ML = min_dist_left
    self.Data.Labels.ML = min_dist_left
    self.Data.Labels.DistLL = vehicle_dis_in_left
    self.Data.Labels.DistRR = vehicle_dis_in_current
    self.Data.Labels.DistMM = vehicle_dis_in_current



    # TODO Not sure if needed
    AspectRatio = Width / Height
    TargetWidth = int(self._TargetResolution[1] * AspectRatio)

    if TargetWidth >= self._TargetResolution[0]:
      if Width != TargetWidth or Height != self._TargetResolution[1]:
        ImageData = cv2.resize(ImageData, (TargetWidth, self._TargetResolution[1]))

      if TargetWidth != self._TargetResolution[0]:
        XStart = int(TargetWidth / 2 - self._TargetResolution[0] / 2)
        XStop = int(TargetWidth / 2 + self._TargetResolution[0] / 2)
        ImageData = ImageData[:, XStart:XStop]

    else:
      TargetHeight = int(self._TargetResolution[0] / AspectRatio)

      if Width != self._TargetResolution[0] or Height != TargetHeight:
        ImageData = cv2.resize(ImageData, (self._TargetResolution[1], TargetHeight))

        if TargetHeight != self._TargetResolution[1]:
          YStart = int(TargetHeight / 2 - self._TargetResolution[1] / 2)
          YStop = int(TargetHeight / 2 + self._TargetResolution[1] / 2)
          ImageData = ImageData[YStart:YStop, :]
    ImageData = cv2.flip(ImageData, 0)
    # Update Parameters

    Height, Width = ImageData.shape[:2]
    # print("Type is ", np.array(ImageData).dtype)

    # Set the SHM
    self.Data.Image.ImageWidth = Width
    self.Data.Image.ImageHeight = Height

    # Reshape ImageData to 1 D array
    ImageData = ImageData.flatten()


    # print("Target Image data", Width, Height)

    start_time = datetime.datetime.now()
    self.Data.Image.Data = (ctypes.c_uint8 * (RECORD_MAX_IMAGE_HEIGHT * RECORD_MAX_IMAGE_WIDTH * RECORD_IMAGE_CHANNELS))(*np.array(ImageData))

    # elapsed = datetime.datetime.now() - start_time
    # print("Setting Image data  ",  int(elapsed.total_seconds() * 1000) )
    #
    # Notify we wrote a new data - Maybe we can also share the frame number
    #self.Data.Sync.IsWritten = 1
    # elapsed = datetime.datetime.now() - write_begin
    # print("Write to memory took ",  int(elapsed.total_seconds() * 1000))

    if self._IsPauseOn:
      self.Data.Sync.IsPauseOn = 1
    else:
      self.Data.Sync.IsPauseOn = 0

  @property
  def Data(self):
    return self._Data


  @property
  def Image(self):
    return self._Image


  @property
  def RawImage(self):
    return self._RawImage


  @property
  def ImageWidth(self):
    return self._TargetResolution[0]

  @property
  def ImageHeight(self):
    return self._TargetResolution[1]
