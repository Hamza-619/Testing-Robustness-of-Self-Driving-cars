import ctypes

RECORD_MAX_IMAGE_HEIGHT=1440
RECORD_MAX_IMAGE_WIDTH=2560
RECORD_IMAGE_CHANNELS=3
MAX_TRACK_NAME_LENGTH=256
RECORD_MEMORY_NAME="DeepDrivingMemory"

class Sync_t(ctypes.Structure):
  _fields_ = [
    ('IsPauseOn', ctypes.c_uint8),
    ('IsWritten', ctypes.c_uint8),
    ('WriteNumber', ctypes.c_uint64),
  ]

  def __str__(self):
    String = ""
    String += "IsPauseOn={}\n".format(self.IsPauseOn)
    String += "IsWritten={}\n".format(self.IsWritten)
    String += "WriteNumber={}\n".format(self.WriteNumber)
    return String


class Image_t(ctypes.Structure):
  _fields_ = [
    ('ImageWidth', ctypes.c_uint32),
    ('ImageHeight', ctypes.c_uint32),
    ('Data', ctypes.c_uint8 * (RECORD_MAX_IMAGE_HEIGHT*RECORD_MAX_IMAGE_WIDTH*RECORD_IMAGE_CHANNELS))
  ]

  def __str__(self):
    String = ""
    String += "ImageWidth={}\n".format(self.ImageWidth)
    String += "ImageHeight={}\n".format(self.ImageHeight)
    return String


class Labels_t(ctypes.Structure):
  _fields_ = [
    ('Angle', ctypes.c_float),
    ('Fast', ctypes.c_float),
    ('LL', ctypes.c_float),
    ('ML', ctypes.c_float),
    ('MR', ctypes.c_float),
    ('RR', ctypes.c_float),
    ('DistLL', ctypes.c_float),
    ('DistMM', ctypes.c_float),
    ('DistRR', ctypes.c_float),
    ('L', ctypes.c_float),
    ('M', ctypes.c_float),
    ('R', ctypes.c_float),
    ('DistL', ctypes.c_float),
    ('DistR', ctypes.c_float),
  ]

  def __str__(self):
    String = ""
    String += "Angle={}\n".format(self.Angle)
    String += "Fast={}\n".format(self.Fast)
    String += "LL={}\n".format(self.LL)
    String += "ML={}\n".format(self.ML)
    String += "MR={}\n".format(self.MR)
    String += "RR={}\n".format(self.RR)
    String += "DistLL={}\n".format(self.DistLL)
    String += "DistMM={}\n".format(self.DistMM)
    String += "DistRR={}\n".format(self.DistRR)
    String += "L={}\n".format(self.L)
    String += "M={}\n".format(self.M)
    String += "R={}\n".format(self.R)
    String += "DistL={}\n".format(self.DistL)
    String += "DistR={}\n".format(self.DistR)
    return String


class Game_t(ctypes.Structure):
  _fields_ = [
    ('Speed', ctypes.c_float),
    ('Lanes', ctypes.c_uint8),
    ('TrackNameArray', ctypes.c_char * MAX_TRACK_NAME_LENGTH),
    ('UniqueTrackID', ctypes.c_uint64),
    ('UniqueRaceID', ctypes.c_uint64),
  ]

  @property
  def TrackName(self):
    return self.TrackNameArray.decode("ascii")

  def __str__(self):
    String = ""
    String += "Speed={}\n".format(self.Speed)
    String += "Lanes={}\n".format(self.Lanes)
    String += "TrackName={}\n".format(self.TrackName)
    String += "UniqueTrackID={}\n".format(self.UniqueTrackID)
    String += "UniqueRaceID={}\n".format(self.UniqueRaceID)
    return String


class Control_t(ctypes.Structure):
  _fields_ = [
    ('IsControlling', ctypes.c_uint8),
    ('Steering', ctypes.c_float),
    ('Accelerating', ctypes.c_float),
    ('Breaking', ctypes.c_float),
  ]

  def __str__(self):
    String = ""
    String += "IsControlling={}\n".format(self.IsControlling)
    String += "Steering={}\n".format(self.Steering)
    String += "Accelerating={}\n".format(self.Accelerating)
    String += "Breaking={}\n".format(self.Breaking)
    return String


class Data_t(ctypes.Structure):
  _fields_ = [
    ('Sync', Sync_t),
    ('Image', Image_t),
    ('Labels', Labels_t),
    ('Game', Game_t),
    ('Control', Control_t),
  ]

  def __str__(self):
    String = ""
    String += addStringPrefix("Sync.", str(self.Sync))
    String += addStringPrefix("Image.", str(self.Image))
    String += addStringPrefix("Labels.", str(self.Labels))
    String += addStringPrefix("Game.", str(self.Game))
    String += addStringPrefix("Control.", str(self.Control))
    return String


def addStringPrefix(Prefix, String):
  import re

  IsLastNewLine = False

  if String[-1] == '\n':
    String = String[:-1]
    IsLastNewLine = True

  EndOfLine = re.compile("\n")
  NewString = Prefix + EndOfLine.sub("\n"+Prefix, String)

  if IsLastNewLine:
    NewString += "\n"

  return NewString