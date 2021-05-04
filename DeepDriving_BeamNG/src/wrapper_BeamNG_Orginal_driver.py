# This file uses BeamNGpy which is an official library providing a Python interface to BeamNG.research © Copyright 2018, BeamNG GmbH.
# https://github.com/BeamNG/BeamNGpy

import cv2
import time
import math
import numpy as np

from beamngpy import BeamNGpy, Scenario,Road, Vehicle, setup_logging
from beamngpy.sensors import Camera, GForces, Electrics, Damage
from docutils.nodes import transition


from shapely import geometry
from shapely.geometry import Point
import sys, os
sys.path.append(r'C:\Users\hamza\deepdriving')
import speed_dreams as sd


def preprocess(image, brightness):

    # Elaborate Frame from BeamNG
    pil_image = image.convert('RGB')
    open_cv_image = np.array(pil_image)

    # Convert RGB to BGR. This is important
    open_cv_image = open_cv_image[:, :, ::-1].copy()

    # decrease_brightness and resize
    hsv = cv2.cvtColor(cv2.resize(open_cv_image, (280, 210)), cv2.COLOR_BGR2HSV)
    hsv[..., 2] = hsv[..., 2] * brightness
    preprocessed = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

    # Check that we are passing to the network values between 0 and 1
    return preprocessed


# def translate_steering(original_steering_value):
#     # Using a quadratic function might be too much
#     # newValue = -1.0 * (0.4 * pow(original_steering_value, 2) + 0.6 * original_steering_value + 0)
#     # This seems to over shoot. Maybe it's just a matter of speed and not amount of steering
#     newValue = -1.0 * original_steering_value
#     linear_factor = 0.6
#     # Dump the controller to compensate oscillations in gentle curve
#     if abs(original_steering_value) < 1:
#         newValue = linear_factor * newValue

#     # print("Steering", original_steering_value, " -> ", newValue)
#     return newValue




# steering_gain = translate_steering()
acc_gain = 1  # 0.4
brake_gain = 0
# BeamNG images are too bright for DeepDrive
brightness = 0.4



fov =50
# MAX_SPEED = 70
MAX_FPS = 60
# Increase the controller frequency to 20Hz
SIMULATION_STEP = 6

# Setup the SHM with DeepDrive
# Create shared memory object
Memory = sd.CSharedMemory(TargetResolution=[280, 210])
# Enable Pause-Mode
Memory.setSyncMode(True)

scenario = Scenario('asfault', 'indicatorsT3')

# Adding vehicels in the scenario :
original_vehicle1 = (1048.5682373046875, -319.7727966308594, 0.20004777610301971)
vehicle1 = Vehicle('ego_vehicle', model='hopper', licence='Main01')

original_vehicle2 = (862.418, -293.463, 0.2012)    #(862.418, -293.463, 0.2012)
vehicle2 = Vehicle('green_vehicle', model='van', licence='Main02', colour='Green')

original_vehicle3 = (862.418, -293.463, 0.2012)    #(862.418, -293.463, 0.2012)
vehicle3 = Vehicle('yellow_vehicle', model='van', licence='Main03', colour='Yellow')

scenario.add_vehicle(vehicle1, pos=original_vehicle1, rot=(0, 0, 90))

scenario.add_vehicle(vehicle2, pos=original_vehicle2, rot=(0, 0, 100))

scenario.add_vehicle(vehicle3, pos=original_vehicle3, rot=(0, 0, 100))



electrics = Electrics()
vehicle1.attach_sensor('electrics', electrics)
cam_pos = (0, 1.8, 0.7)
cam_dir = (0, 1, 0.2 )
cam = Camera(cam_pos, cam_dir, 60, (280, 210), near_far=(0.5, 300), colour=True)
vehicle1.attach_sensor('cam', cam)

road = Road('road_rubber_sticky', rid='main_road', texture_length=16)
road.nodes = [
(1050.0,-323.18966165522687,0.01,7.999999999999996),
(954.4249840125182,-293.7717025317153,0.01,8.000000000000062),
(945.3077798322204,-291.3954300619591,0.01,8.000000000000012),
(936.0181635743155,-289.8228167284825,0.01,8.000000000000018),
(926.6268348277497,-289.0658310683232,0.01,8.0),
(917.2052672749237,-289.13023419943534,0.01,8.000000000000032),
(907.8251647338126,-290.01553597510355,0.01,8.00000000000001),
(898.557915448615,-291.71499871425516,0.01,7.999999999999959),
(884.1421943383076,-294.35860741960215,0.01,7.999999999999995),
(869.5509237188014,-295.7357435150861,0.01,7.9999999999999805),
(854.895151969961,-295.8359261634828,0.01,8.000000000000004),
(840.286418364192,-294.658392914346,0.01,8.000000000000004),
(825.8359041852287,-292.2121055067158,0.01,8.000000000000012),
(811.6535865714322,-288.51568166487283,0.01,7.999999999999975),
(797.8474015233609,-283.5972534062153,0.01,8.000000000000039),
(784.5224224456331,-277.4942529396198,0.01,8.000000000000027),
(771.7800604748727,-270.25312778372955,0.01,8.000000000000021),
(759.7172926797257,-261.9289872732918,0.01,7.9999999999999725),
(748.4259240068113,-252.5851831438444,0.01,8.000000000000004),
(737.9918885896456,-242.29282738675565,0.01,8.00000000000003),
(728.4945957379957,-231.13025104403135,0.01,7.999999999999948),
(720.006325585085,-219.1824080617875,0.01,8.000000000000036),
(712.5916789921349,-206.54022873942375,0.01,7.999999999999959),
(706.3070858968036,-193.29992769513996,0.01,8.0),
(701.2003758472878,-179.56227161459543,0.01,7.999999999999917),
(697.31041399058,-165.43181235558666,0.01,8.000000000000064),
(694.666805285233,-151.01609124527928,0.01,8.000000000000004),
(693.289669189749,-136.42482062577312,0.01,8.000000000000032),
(693.1894865413524,-121.76904887693271,0.01,7.999999999999888),
(693.1131569044787,-110.60274659210194,0.01,8.000000000000032),
(692.0639103555386,-99.48558802485915,0.01,8.000000000000005),
(690.0497322943219,-88.50218146462495,0.01,8.000000000000068),
(687.0859518320683,-77.73611726728494,0.01,8.000000000000012),
(683.1951251276753,-67.26933168210815,0.01,7.999999999999983),
(678.4068637217085,-57.18148326741573,0.01,8.000000000000059),
(672.7576091746989,-47.54934664085289,0.01,7.9999999999999325),
(666.2903557248623,-38.44622817819089,0.01,8.000000000000037),
(659.0543230759862,-29.941408107543808,0.01,8.00000000000003),
(651.1045818057646,-22.099613245000015,0.01,8.000000000000004),
(642.5016342454489,-14.980524384468652,0.01,7.9999999999999964),
(633.310954020575,-8.638322090801779,0.01,7.999999999999986),
(623.6024877571385,-3.121274352980649,0.01,8.000000000000028),
(613.4501227455364,1.5286307644254435,0.01,7.999999999999988),
(602.9311246136725,5.276004675783568,0.01,8.000000000000021),
(592.1255492888752,8.092327602902003,0.01,8.000000000000027),
(581.1156337239507,9.956165627763141,0.01,8.000000000000018),
(569.9851700243172,10.853333817581643,0.01,8.000000000000032),
(558.8188677394864,10.777004180707962,0.01,8.000000000000032),
(547.7017091722437,9.727757631767815,0.01,8.000000000000037),
(536.7183026120094,7.713579570551076,0.01,8.000000000000043),
(525.9522384146694,4.749799108297523,0.01,8.000000000000043),
(515.4854528294927,0.8589724039044881,0.01,7.999999999999984),
(505.39760441480024,-3.9292890020621627,0.01,7.999999999999995)
]


road.improved_spline = 0
road.over_object = 1
road.break_angle = 180

# We create Divider for the scenario.

road2 = Road('BlankWhite', rid='divider_1_1', texture_length=16)
road2.nodes = [
(1050.0,-323.18966165522687,0.01,0.3),
(954.4249840125182,-293.7717025317153,0.01,0.3),
(945.3077798322204,-291.3954300619591,0.01,0.3),
(936.0181635743155,-289.8228167284825,0.01,0.3),
(926.6268348277497,-289.0658310683232,0.01,0.3),
(917.2052672749237,-289.13023419943534,0.01,0.3),
(907.8251647338126,-290.01553597510355,0.01,0.3),
(898.557915448615,-291.71499871425516,0.01,0.3),
(884.1421943383076,-294.35860741960215,0.01,0.3),
(869.5509237188014,-295.7357435150861,0.01,0.3),
(854.895151969961,-295.8359261634828,0.01,0.3),
(840.286418364192,-294.658392914346,0.01,0.3),
(825.8359041852287,-292.2121055067158,0.01,0.3),
(811.6535865714322,-288.51568166487283,0.01,0.3),
(797.8474015233609,-283.5972534062153,0.01,0.3),
(784.5224224456331,-277.4942529396198,0.01,0.3),
(771.7800604748727,-270.25312778372955,0.01,0.3),
(759.7172926797257,-261.9289872732918,0.01,0.3),
(748.4259240068113,-252.5851831438444,0.01,0.3),
(737.9918885896456,-242.29282738675565,0.01,0.3),
(728.4945957379957,-231.13025104403135,0.01,0.3),
(720.006325585085,-219.1824080617875,0.01,0.3),
(712.5916789921349,-206.54022873942375,0.01,0.3),
(706.3070858968036,-193.29992769513996,0.01,0.3),
(701.2003758472878,-179.56227161459543,0.01,0.3),
(697.31041399058,-165.43181235558666,0.01,0.3),
(694.666805285233,-151.01609124527928,0.01,0.3),
(693.289669189749,-136.42482062577312,0.01,0.3),
(693.1894865413524,-121.76904887693271,0.01,0.3),
(693.1131569044787,-110.60274659210194,0.01,0.3),
(692.0639103555386,-99.48558802485915,0.01,0.3),
(690.0497322943219,-88.50218146462495,0.01,0.3),
(687.0859518320683,-77.73611726728494,0.01,0.3),
(683.1951251276753,-67.26933168210815,0.01,0.3),
(678.4068637217085,-57.18148326741573,0.01,0.3),
(672.7576091746989,-47.54934664085289,0.01,0.3),
(666.2903557248623,-38.44622817819089,0.01,0.3),
(659.0543230759862,-29.941408107543808,0.01,0.3),
(651.1045818057646,-22.099613245000015,0.01,0.3),
(642.5016342454489,-14.980524384468652,0.01,0.3),
(633.310954020575,-8.638322090801779,0.01,0.3),
(623.6024877571385,-3.121274352980649,0.01,0.3),
(613.4501227455364,1.5286307644254435,0.01,0.3),
(602.9311246136725,5.276004675783568,0.01,0.3),
(592.1255492888752,8.092327602902003,0.01,0.3),
(581.1156337239507,9.956165627763141,0.01,0.3),
(569.9851700243172,10.853333817581643,0.01,0.3),
(558.8188677394864,10.777004180707962,0.01,0.3),
(547.7017091722437,9.727757631767815,0.01,0.3),
(536.7183026120094,7.713579570551076,0.01,0.3),
(525.9522384146694,4.749799108297523,0.01,0.3),
(515.4854528294927,0.8589724039044881,0.01,0.3),
(505.39760441480024,-3.9292890020621627,0.01,0.3),





    ]


road2.drivability = -1
road2.improved_spline = 0
road2.over_object = 1
road2.break_angle = 180
road2.render_priority = 9


# Creation of Left side Boundary for the scenario.

road3 = Road('strap', rid='boundary_1_l1', texture_length=16)
road3.nodes = [
(1048.9115355124302,-326.72593724676375,0.01,0.3),
(953.323928755878,-297.3044014419012,0.01,0.3),
(944.5443988044801,-295.0161390636174,0.01,0.3),
(935.5732530241694,-293.4962808797398,0.01,0.3),
(926.5037807931288,-292.76409308889004,0.01,0.3),
(917.4050062713336,-292.8251480822636,0.01,0.3),
(908.3461766268849,-293.67898119449484,0.01,0.3),
(899.3962350232478,-295.3190942400412,0.01,0.3),
(884.6501658996772,-298.0232833962012,0.01,0.3),
(869.7375647383498,-299.43074693192403,0.01,0.3),
(854.7590419968316,-299.53313581345355,0.01,0.3),
(839.8285932774662,-298.3296707995771,0.01,0.3),
(825.0598483102592,-295.82951098572244,0.01,0.3),
(810.5652061620216,-292.0516840977104,0.01,0.3),
(796.4549798116083,-287.0249416792737,0.01,0.3),
(782.8365566015312,-280.78754027544596,0.01,0.3),
(769.8135809554484,-273.38695027715625,0.01,0.3),
(757.4851655815157,-264.879494642891,0.01,0.3),
(745.9451371648282,-255.32992024696836,0.01,0.3),
(735.2813222896962,-244.81090511673167,0.01,0.3),
(725.5748790263071,-233.40250530887687,0.01,0.3),
(716.8996792688073,-221.19154563452378,0.01,0.3),
(709.3217465255783,-208.27095886997017,0.01,0.3),
(702.8987534404785,-194.7390784821608,0.01,0.3),
(697.6795828691943,-180.69889025161928,0.01,0.3),
(693.7039558511937,-166.2572484884741,0.01,0.3),
(691.002129308634,-151.52406280664957,0.01,0.3),
(689.5946657729111,-136.61146164532133,0.01,0.3),
(689.4921873573719,-121.61984092694169,0.01,0.3),
(689.4182430216505,-110.80248558851187,0.01,0.3),
(688.4004651361473,-100.00659991793142,0.01,0.3),
(686.4456367685357,-89.3405010392577,0.01,0.3),
(683.568635343051,-78.885364405324,0.01,0.3),
(679.791356577722,-68.72075991889866,0.01,0.3),
(675.1425478447361,-58.92404635767939,0.01,0.3),
(669.657589385579,-49.56978262728441,0.01,0.3),
(663.3782250460329,-40.729160322960944,0.01,0.3),
(656.3522445803059,-32.469461918558544,0.01,0.3),
(648.6331199421453,-24.85354870627701,0.01,0.3),
(640.2795983309821,-17.9393823842759,0.01,0.3),
(631.3552550902717,-11.77958393315343,0.01,0.3),
(621.9280098607418,-6.421033138510644,0.01,0.3),
(612.0696096709152,-1.904511807476182,0.01,0.3),
(601.8550828989012,1.7356066054706056,0.01,0.3),
(591.3621682611349,4.471618601243636,0.01,0.3),
(580.6707231738047,6.282701476505859,0.01,0.3),
(569.8621159896963,7.155071797014778,0.01,0.3),
(559.0186067358964,7.0820902978797005,0.01,0.3),
(548.2227210653159,6.064312412376524,0.01,0.3),
(537.5566221866422,4.1094840447649785,0.01,0.3),
(527.1014855527084,1.2324826192802605,0.01,0.3),
(516.936881066283,-2.544796146048768,0.01,0.3),
(507.1401675050639,-7.1936048790345986,0.01,0.3),
(495.17268047233347,-12.874048709036112,0.01,0.3),




]



road3.drivability = -1
road3.improved_spline = 0
road3.over_object = 1
road3.break_angle = 180
road3.render_priority = 9

road4 = Road('strap', rid='boundary_1_r1', texture_length=16)
road4.nodes = [
(1051.0884644875698,-319.65338606369,0.01,0.3),
(955.5260392691583,-290.2390036215294,0.01,0.3),
(946.0838357071899,-287.7780245829524,0.01,0.3),
(936.4759886610412,-286.1515388432514,0.01,0.3),
(926.762944800879,-285.3686214183524,0.01,0.3),
(917.0186262553754,-285.43523078259733,0.01,0.3),
(907.3171931724429,-286.3508599985045,0.01,0.3),
(897.7195958739821,-288.11090318846914,0.01,0.3),
(883.6471062186821,-290.6915688294031,0.01,0.3),
(869.3773230309554,-292.0395093410404,0.01,0.3),
(855.0443599199521,-292.13862697950225,0.01,0.3),
(840.7572993894263,-290.98816739971096,0.01,0.3),
(826.6248745967787,-288.5968862937354,0.01,0.3),
(812.7546418280723,-284.98298275468693,0.01,0.3),
(799.252161929753,-280.1739607706323,0.01,0.3),
(786.2201969268668,-274.2064199026371,0.01,0.3),
(773.7579279420017,-267.1257767400065,0.01,0.3),
(761.9602003670561,-258.98591925261724,0.01,0.3),
(750.916802032538,-249.84879667092878,0.01,0.3),
(740.7117798679592,-239.78394801493312,0.01,0.3),
(731.4228002539531,-228.8679728602243,0.01,0.3),
(723.1205579342218,-217.18394836897562,0.01,0.3),
(715.868237985849,-204.82079702257226,0.01,0.3),
(709.7210349427125,-191.87260986783542,0.01,0.3),
(704.7257327317533,-178.43793042734166,0.01,0.3),
(700.9203486190427,-164.61900472371445,0.01,0.3),
(698.3338438754321,-150.52100312565386,0.01,0.3),
(696.9859033637947,-136.2512199379272,0.01,0.3),
(696.8867857253329,-121.91825682692374,0.01,0.3),
(696.8081603213167,-110.4161055725537,0.01,0.3),
(695.7285863321375,-98.97761646348887,0.01,0.3),
(693.6561904337082,-87.67674533173755,0.01,0.3),
(690.6067448101618,-76.59949863026111,0.01,0.3),
(686.6034575840005,-65.83018089508728,0.01,0.3),
(681.6767961882653,-55.45075313686933,0.01,0.3),
(675.8642554909765,-45.54020906811656,0.01,0.3),
(669.2100724365503,-36.17397391334455,0.01,0.3),
(661.7648893759363,-27.423330377568536,0.01,0.3),
(653.5853686477477,-19.354876141875973,0.01,0.3),
(644.7337613436588,-12.030017014869339,0.01,0.3),
(635.2774335399993,-5.504499597375101,0.01,0.3),
(625.2883536012405,0.1720129828454515,0.01,0.3),
(614.8425444572891,4.956319037483773,0.01,0.3),
(604.019505023083,8.812007108621215,0.01,0.3),
(592.9016051638451,11.709733081908597,0.01,0.3),
(581.5734588106767,13.62744351299422,0.01,0.3),
(570.1212799974465,14.550543467552414,0.01,0.3),
(558.6322267199381,14.472007597545916,0.01,0.3),
(547.1937376108735,13.392433608366808,0.01,0.3),
(535.8928664791215,11.320037709937322,0.01,0.3),
(524.8156197776462,8.270592086391233,0.01,0.3),
(514.0463020424713,4.267304860229461,0.01,0.3),
(503.65504132453657,-0.6649731250897255,0.01,0.3),
(492.3062118580076,-6.051767206802257,0.01,0.3),




]




road4.drivability = -1
road4.improved_spline = 0
road4.over_object = 1
road4.break_angle = 180
road4.render_priority = 9



# Adding Main Road in the sceanrio
scenario.add_road(road4)

# Adding Divider in the sceanrio
scenario.add_road(road3)

# Adding Left Boundary in the sceanrio
scenario.add_road(road2)

# Adding Rigt Boundary in the sceanrio
scenario.add_road(road)

#Delete from here!!

positions = list()
directions = list()
distance = list()


Memory.Data.Game.UniqueRaceID = int(time.time())
print("Setting Race ID at ", Memory.Data.Game.UniqueRaceID)

# Setting Max_Speed for the Vehicle.
# TODO What's this? Maybe some hacky way to pass a parameter which is not supposed to be there...

#Memory.Data.Game.UniqueTrackID = int(MAX_SPEED)
# Speed is KM/H
print("Setting speed at ", Memory.Data.Game.UniqueTrackID)
# Default for AsFault
Memory.Data.Game.Lanes = 1
# By default the AI is in charge
#Memory.Data.Control.IsControlling = 1

deep_drive_engaged = True
#STATE = "GRACE"
print ("I am here lalala before wait on reading ")


STATE = "NORMAL"

Memory.waitOnRead()
# if Memory.Data.Control.Breaking == 3.0 or Memory.Data.Control.Breaking == 2.0:
#     print("\n\n\nState not reset ! ", Memory.Data.Control.Breaking)
#     Memory.Data.Control.Breaking = 0.0
#     # Pass the computation to DeepDrive
#     # Not sure this will have any effect
#     Memory.indicateWrite()

#     Memory.waitOnRead()
#     if Memory.Data.Control.Breaking == 3.0 or Memory.Data.Control.Breaking == 2.0:
#         print("\n\n\nState not reset Again! ", Memory.Data.Control.Breaking)
#         Memory.Data.Control.Breaking = 0.0
#         # Pass the computation to DeepDrive
#         Memory.indicateWrite()


# Connect to running beamng
beamng = BeamNGpy('localhost', 61126, home='C:/Beamng/trunk')
scenario.make(beamng)
beamng = beamng.open()
beamng.load_scenario(scenario)
beamng.start_scenario()
beamng.set_deterministic()  # Set simulator to be deterministic
beamng.set_steps_per_second(MAX_FPS)



road_geometry = beamng.get_road_edges('main_road')
boundary_geo_left = beamng.get_road_edges('boundary_1_l1')
boundary_geo_right = beamng.get_road_edges('boundary_1_r1')


# Creating variable to only collect middle edges for the main road.

node_ar =[]
for edge_ar in road_geometry:
    edge_rr = edge_ar['middle']
    node_ar.append(edge_rr)
    
    
# Creating variable to only collect right edges for the left boundary.

node_ar_left =[]
for edge_ar_left in boundary_geo_left:
    edge_left = edge_ar_left['right']
    node_ar_left.append(edge_left)
    
# Creating variable to only collect left edges for the right boundary.

node_ar_right =[]
for edge_ar_right in boundary_geo_right:
    edge_right = edge_ar_right['left']
    node_ar_right.append(edge_right)


def node_dist(x1, y1, x2, y2, x3, y3): # x3 and y3 are the points.
    px = x2-x1
    py = y2-y1

    norm = px*px + py*py

    u =  ((x3 - x1) * px + (y3 - y1) * py) / float(norm)

    if u > 1:
        u = 1
    elif u < 0:
        u = 0

    x = x1 + u * px
    y = y1 + u * py

    dx = x - x3
    dy = y - y3
    
    dist = (dx*dx + dy*dy)**.5

    return dist


# Collecting first person view from the ego vehicle's attached camera.
def plot_overhead(ax):
    view = bng.poll_sensors(vehicle1)['cam']['colour']
    view = view.convert('RGB')
    ax.imshow(np.asarray(view))
    ax.set_aspect('auto','datalim')

    
# Code for collecting car angle with respect to direction of the road.
def unit_vector(vector):
        return vector / np.linalg.norm(vector)

def angle_between(v1, v2):
        v1_u = unit_vector(v1)
        v2_u = unit_vector(v2)
        return np.arccos(np.clip(np.dot(v1_u, v2_u), -1.0, 1.0))
        
def compute_angle_road(newposition_Vehicle1, direction_car, closest_node, node_ar):
    vec_1 = geometry.Point(node_ar[closest_node][0], node_ar[closest_node][1])
    vec_2 = geometry.Point(node_ar[closest_node+1][0],node_ar[closest_node+1][1])
    magnitude = vec_1.distance(vec_2)
    vector_u = geometry.Point((vec_2.x - vec_1.x) / magnitude, (vec_2.y - vec_1.y) / magnitude)
    radiants = angle_between(np.array([vector_u.x, vector_u.y]), np.array([direction_car.x, direction_car.y]))
    degree_car = (radiants*180)/3.14
    return degree_car

vehicle_distance1 = -1
vehicle_distance2 = -1
vehicle_distance3 = -1

vehicle_dis_in_left = 0

vehicle_dis_in_left = 0


# With 60hz temporal resolution
    # Connect to the existing vehicle (identified by the ID set in the vehicle instance)
    #bng.connect_vehicle(vehicle)
    # Put simulator in pause awaiting further inputs
beamng.pause()
while True:
    beamng.step(SIMULATION_STEP)
    
    time.sleep(0.1)
    vehicle1.update_vehicle()  # Synchs the vehicle's "state" variable with the simulator
    sensors = beamng.poll_sensors(vehicle1)
    vehicle2.update_vehicle()
    sensors = beamng.poll_sensors(vehicle2)
    vehicle3.update_vehicle()
    sensors = beamng.poll_sensors(vehicle3)
    
    directions.append(vehicle1.state['dir'])
    direction_car = geometry.Point(vehicle1.state['dir'])
    #display(vehicle1.state['dir'])
    newdirection_road = geometry.Point(vehicle1.state['dir'])
    positions.append(vehicle1.state['pos'])
    #display(vehicle1.state['pos'])
    positions.append(vehicle2.state['pos'])
    #display(vehicle2.state['pos'])
    positions.append(vehicle3.state['pos'])
    
    vehiclepos = vehicle1.state['pos']
    vehiclepos2 = vehicle2.state['pos']
    vehiclepos3 = vehicle3.state['pos']
    
    newposition_Vehicle1 = geometry.Point(vehicle1.state['pos'])
    newposition_Vehicle2 = geometry.Point(vehicle2.state['pos'])
    newposition_Vehicle3 = geometry.Point(vehicle3.state['pos'])
    
    def on_left(dist_left, dist_right):
        if dist_left < dist_right:
            return True
        else:
            return False
     
    # For Main vehicle (Ego Car)
    i = 0
    min_dist = 100000000
    closest_node = -1
    while i < len(node_ar)-1:
        current = node_dist(node_ar[i][0], node_ar[i][1], node_ar[i+1][0], node_ar[i+1][1],vehiclepos[0],vehiclepos[1])
        if min_dist > current:
            min_dist = current
            closest_node = i
        i += 1
   



    print('1. Car distance from middel lane marking')
    if min_dist >= 1 and min_dist <= 4:
        print(min_dist)
        print('\n')
    
    
    a = 0
    min_dist_left = 100000000
    while a < len(node_ar_left)-1:
        min_dist_left = min(min_dist_left, node_dist(node_ar_left[a][0], node_ar_left[a][1], node_ar_left[a+1][0], node_ar_left[a+1][1], vehiclepos[0], vehiclepos[1]))
        a += 1
   


    print('2. Car distance from left lane marking')
    if min_dist_left < 8 and min_dist_left > 0.5: 
        print(min_dist_left)
        print('\n')
    
    b = 0
    min_dist_right = 100000000
    while b < len(node_ar_right)-1:
        min_dist_right = min(min_dist_right, node_dist(node_ar_right[b][0], node_ar_right[b][1], node_ar_right[b+1][0],node_ar_right[b+1][1], vehiclepos[0], vehiclepos[1]))
        b += 1
    
    
    
    print('3. Car distance from right lane marking')
    if min_dist_right > 0.5 and min_dist_right < 8:
        print(min_dist_right)
        print('\n')
    
    
    
    print('4. Distance between ego vehicle and right lane when ego vehicle on marking')
    ego_min_dis_right = 0
    if min_dist_right < 5.5 and min_dist_right > 3.5:
        ego_min_dis_right = min_dist_right
        print(ego_min_dis_right)
        print('\n')
    
    
    
    print('5. Distance between ego vehicle and left lane when ego vehicle on marking')
    ego_min_dis_left = 0
    if min_dist_left < 5.5 and min_dist_left  > 3.5 :
        ego_min_dis_left = min_dist_left
        print(ego_min_dis_left)
        print('\n')
    
    
    
    
    # For Vehicle2
    
    c = 0
    min_dist_left_v2 = 100000000
    while c < len(node_ar_left)-1:
        min_dist_left_v2 = min(min_dist_left_v2, node_dist(node_ar_left[c][0], node_ar_left[c][1], node_ar_left[c+1][0], node_ar_left[c+1][1], vehiclepos2[0], vehiclepos2[1]))
        c += 1
    #print(min_dist_left_v2)
    print('\n')
    
    d = 0
    min_dist_right_v2 = 100000000
    while d < len(node_ar_right)-1:
        min_dist_right_v2 = min(min_dist_right_v2, node_dist(node_ar_right[d][0], node_ar_right[d][1], node_ar_right[d+1][0],node_ar_right[d+1][1], vehiclepos2[0], vehiclepos2[1]))
        d += 1
    #print(min_dist_right_v2)
    #print('\n')
    
    side = on_left(min_dist_left_v2, min_dist_right_v2)
    
    
        
    
    
    # For Vehicle 3
    
    e = 0
    min_dist_left_v3 = 100000000
    while e < len(node_ar_left)-1:
        min_dist_left_v3 = min(min_dist_left_v3, node_dist(node_ar_left[e][0], node_ar_left[e][1], node_ar_left[e+1][0], node_ar_left[e+1][1], vehiclepos3[0], vehiclepos3[1]))
        e += 1
    #print(min_dist_left_v3)
    print('\n')
    
    f = 0
    min_dist_right_v3 = 100000000
    while f < len(node_ar_right)-1:
        min_dist_right_v3 = min(min_dist_right_v3, node_dist(node_ar_right[f][0], node_ar_right[f][1], node_ar_right[f+1][0],node_ar_right[f+1][1], vehiclepos3[0], vehiclepos3[1]))
        f += 1
    #print(min_dist_right_v3)
    #print('\n')
    
    
    #print('6. Distance between ego vehicle and preceeding vehicle in current lane :')
    
    
    previous_distance1 = vehicle_distance1
    previous_distance2 = vehicle_distance2
    previous_distance3 = vehicle_distance3
    
    previous_distance_all = [previous_distance1, previous_distance2]
    
    vehicle_distance1 = newposition_Vehicle2.distance(newposition_Vehicle1)
    vehicle_distance2 = newposition_Vehicle3.distance(newposition_Vehicle1)
    
    vehicle_distance_all = [vehicle_distance1, vehicle_distance2]
    
    other_veh_dist = [min_dist_right_v2, min_dist_right_v3]
    
    vehicle_dis_in_current = 0
    i = 0
    while i < len(vehicle_distance_all):
        distance_of_vehicle = vehicle_distance_all[i]
        prev_dist = previous_distance_all[i]
        otherdis = other_veh_dist[i]
        i += 1
        if prev_dist != -1 and distance_of_vehicle < prev_dist:
            if distance_of_vehicle <= 100 and otherdis > 0.5 and otherdis < 4:
                vehicle_dis_in_current = distance_of_vehicle
                print(vehicle_dis_in_current)
    
    #print('7. Distance between ego vehicle and preceeding vehicle in left lane')
    
    
    vehicle_dis_in_left = 0
    i = 0
    while i < len(vehicle_distance_all):
        distance_of_vehicle = vehicle_distance_all[i]
        prev_dist = previous_distance_all[i]
        otherdis = other_veh_dist[i]
        i += 1
        if prev_dist != -1 and distance_of_vehicle < prev_dist:
            if distance_of_vehicle <= 100 and otherdis > 4 and otherdis < 8:
                vehicle_dis_in_left = distance_of_vehicle
                print(vehicle_dis_in_left)

    print('8. Angle between car heading and tangent of the road')
    angle = compute_angle_road(newposition_Vehicle1, direction_car, closest_node, node_ar)
    #print(angle)
    #print('\n')
    
    
    

    # Retrieve sensor data and show the camera data.
    sensors = beamng.poll_sensors(vehicle1)
    # print("vehicle.state", vehicle.state)

    # # TODO: Is there a way to query for the speed directly ?
    #speed = math.sqrt(vehicle.state['vel'][0] * vehicle.state['vel'][0] + vehicle.state['vel'][1] * vehicle.state['vel'][1])
    # Speed is M/S ?
    # print("Speed from BeamNG is: ", speed, speed*3.6)

    imageData = preprocess(sensors['cam']['colour'], brightness)
    
    
    
    #Angle = 5
    fast = 1

    Height, Width = imageData.shape[:2]
    Speed = 50
    # print("Image size ", Width, Height)
    # TODO Size of image should be right since the beginning
    Memory.write(Width, Height, imageData, Speed, angle, min_dist,fast,min_dist_left, min_dist_right, ego_min_dis_left, ego_min_dis_right,vehicle_dis_in_current,vehicle_dis_in_left)


    # Pass the computation to DeepDrive
    Memory.indicateWrite()


    # Wait for the control commands to send to the vehicle
    # This includes a sleep and will be unlocked by writing data to it
    Memory.waitOnRead()

#         # TODO Assumption. As long as the car is out of the road for too long this value stays up
# #         if Memory.Data.Control.Breaking == 3.0:
# #             if STATE != "DISABLED":
# #                 print("Abnormal situation detected. Disengage DeepDrive and enable BeamNG AI")
#         vehicle.ai_set_mode("manual")
#         vehicle.ai_drive_in_lane(True)
#         vehicle.ai_set_speed(MAX_SPEED)
#         #vehicle.ai_set_waypoint("waypoint_goal")
#         deep_drive_engaged = False
#         STATE = "DISABLED"
# #         elif Memory.Data.Control.Breaking == 2.0:
# #             if STATE != "GRACE":
# #                 print("Grace period. Deep Driving still disengaged")
# #                 vehicle.ai_set_mode("manual")
# #                 vehicle.ai_drive_in_lane(True)
# #                 vehicle.ai_set_speed(MAX_SPEED)
# #                 #vehicle.ai_set_waypoint("waypoint_goal")
# #                 # vehicle.ai_drive_in_lane(True)
# #                 STATE = "GRACE"
# #         else:
# #             if STATE != "NORMAL":
# #                 print("DeepDrive re-enabled")
# #                 # Disable BeamNG AI driver
# #                 # vehicle.ai_set_mode("disabled")
# #                 deep_drive_engaged = True
# #                 STATE = "NORMAL"

    # print("State ", STATE, "Memory ",Memory.Data.Control.Breaking )
#         if STATE == "NORMAL":
#             # vehicle.ai_set_mode("disabled")
#             # print("DeepDrive re-enabled")
#             # Disable BeamNG AI driver
#             vehicle.ai_set_mode("disabled")
        # Get commands from SHM
        # Apply Control - not sure cutting at 3 digit makes a difference
    steering = Memory.Data.Control.Steering
    throttle = Memory.Data.Control.Accelerating
    brake = Memory.Data.Control.Breaking 

    # Apply commands
    vehicle1.control(throttle=throttle, steering=steering, brake=brake)
    #vehicle.set_shift_mode('realistic_automatic')

    print("Suggested Driving Actions: ")
    print(" Steer: ", steering)
    print(" Accel: ", throttle)
    print(" Brake: ", brake)

beamng.close()
