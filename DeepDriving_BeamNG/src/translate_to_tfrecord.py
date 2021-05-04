# The MIT license:
#
# Copyright 2017 Andre Netzeband
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
# documentation files (the "Software"), to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and
# to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of
# the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO
# THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# Note: The DeepDriving project on this repository is derived from the DeepDriving project devloped by the princeton
# university (http://deepdriving.cs.princeton.edu/). The above license only applies to the parts of the code, which
# were not a derivative of the original DeepDriving project. For the derived parts, the original license and
# copyright is still valid. Keep this in mind, when using code from this project.


import sys, os
sys.path.append(r'C:\Users\hamza\deepdriving\python\modules')
import deep_driving
import dd.data_reader as dddr
import dd
import time
from csv import DictReader
import os
import cv2
import dd2

class Cursor:
    def __init__(self, Indicators, Lanes, Image, FrameNumber):
        self.Labels = Indicators
        self.Lanes = Lanes
        self.Image = Image
        self.Key = FrameNumber


class Translator:

    def __init__(self, input_folder, output_path):
      # Store the translated data here
      self._OutputDB = deep_driving.db.COutputDB(output_path)
      self.input_folder = input_folder


    def translateSingle(self, Cursor):
        self._Indicators = dd2.Indicators_t()
        self._Indicators = deep_driving.legacy.translateLabels(self._Indicators, Cursor.Labels)

        Data = {
          # Image data
          'Image' :      Cursor.Image,
          'FrameNumber': Cursor.Key,

          # Additional data
          'Speed':       Cursor.Labels.Speed,
          'Lanes':       Cursor.Lanes,

          'RaceID':      1,
          'TrackName': "asfault",
          'TrackID': 1,

          # Original Labels
          'Angle':       self._Indicators.Angle,
          'Fast':        self._Indicators.Fast,
          'LL':          self._Indicators.LL,
          'ML':          self._Indicators.ML,
          'MR':          self._Indicators.MR,
          'RR':          self._Indicators.RR,
          'DistLL':      self._Indicators.DistLL,
          'DistMM':      self._Indicators.DistMM,
          'DistRR':      self._Indicators.DistRR,
          'L':           self._Indicators.L,
          'M':           self._Indicators.M,
          'R':           self._Indicators.R,
          'DistL':       self._Indicators.DistL,
          'DistR':       self._Indicators.DistR,
        }
        self._OutputDB.store(Data)

    def get_cursor(self, csv_dict_reader):
        for indicators_dict in csv_dict_reader:
            labels = dd2.Indicators_t.fromDict(indicators_dict)
            image = cv2.imread(indicators_dict['Image'])
            lanes = 1
            frame_number = int(indicators_dict['FrameNumber'])

            cursor = Cursor(labels, lanes, image, frame_number)
            yield cursor

    # TODO Create a generator which yields the curson object for each line/file that is found in the CSV
    def translate(self):

        csv_file = os.path.join(self.input_folder, 'ValidationNew.csv')
        with open(csv_file, newline='') as csvfile:
            reader = DictReader(csvfile)

            for cursor in self.get_cursor(reader):
                self.translateSingle(cursor)


if __name__ == '__main__':
    translator = Translator(r'C:\Data_main\Validation', r'C:\Data_main\Validation')
    translator.translate()

# if __name__ == '__main__':
#   CApplication("translate").run(CTranslateWindow)
