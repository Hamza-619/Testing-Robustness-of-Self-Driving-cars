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
import deep_learning as dl
import cv2
import sys
import os
import numpy as np
import PIL
from PIL import Image

def compute_mean(workingDir):
    # Access all PNG files in directory
    allfiles = os.listdir(workingDir)
    imlist = [filename for filename in allfiles if filename.endswith('.jpg')]

    # Assuming all images are the same size, get dimensions of first image
    # w, h = Image.open(imlist[0]).size
    h = 210
    w = 280
    N = len(imlist)

    # Create a numpy array of floats to store the average (assume RGB images)
    arr = np.zeros((h, w, 3), np.float32)

    # Build up average pixel intensities, casting each image as an array of floats
    for im in imlist:
    # for filename in sorted([os.path.join(dir, file) for file in os.listdir(dir)]):

        # Resize and covert the images before computing the mean
        # hsv = cv2.cvtColor(cv2.resize(img, (280, 210)), cv2.COLOR_BGR2HSV)
        imgFile = os.path.join(dir, im)
        # TODO THis assumes that the input files are proportionally scaled to 280,210...
        print(imgFile)
        # Int values
        image = Image.open(imgFile).resize((280,210),Image.ANTIALIAS).convert('RGB')
        print("Image size", image.size)
        # Convert to Float
        imarr = np.array(image, dtype=np.float32)
        # Normalize 0 - 1
        imarr = imarr / 255
        arr = arr + imarr / N

    # Round values in array and cast as 8-bit integer
    # arr = np.array(np.round(arr), dtype=np.uint8)

    # Generate, save and preview final image
    #out = Image.fromarray(arr, mode="RGB")
    #out.save("Average.png")
    #out.show()
    # meanImage = Image.fromarray(arr, mode="RGB")
    # meanImage.show()

    return np.array(arr, dtype=np.float32)


# Basic parsing of arguments
# print("This is the name of the script: ", sys.argv[0])
# print("Number of arguments: ", len(sys.argv))
# print("The arguments are: ", str(sys.argv))

# We take images and data from the following folder
# dir = sys.argv[1]
dir = r"C:\All_images"

MeanReader = dl.data.CMeanReader()

# first create an empty the mean file
# NewMean = np.zeros((210, 280, 3), dtype=np.float32)

# store any image in this file
# ... in this case I just change some pixels
# NewMean[:, 0:94,   :] = (0.0, 0.57, 0.27)
# NewMean[:, 94:187, :] = (1.0, 1.0, 1.0)
# NewMean[:, 187:,   :] = (0.80, 0.12, 0.21)

# in the same way, you can create a variance-image
# but in the current deep-driving net, this is not used
# so I just let it be zero!
NewVar = np.zeros((210, 280, 3), dtype=np.float32)

# create also a "mean-pixel" and "variance-pixel" value
# since those values are also not used, they can be zero again
MeanPixel = np.zeros((3), dtype=np.float32)
VarPixel  = np.zeros((3), dtype=np.float32)

# Read all the image files in the directory and create the MeanImage
NewMean = compute_mean(dir)

# Show will show also 0 - 1 values !
# visible = np.array(np.round(NewMean), dtype=np.uint8)
# cv2.imshow("MeanImage", visible)
# cv2.waitKey(0)

# now store everything
MeanReader.store("beamngyo_imageMean_main.tfrecord", NewMean, NewVar, MeanPixel, VarPixel)
