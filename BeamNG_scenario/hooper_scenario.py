# Define all the imports

import time
import matplotlib
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from shapely import geometry
import sys
from matplotlib.pyplot import imshow
from time import sleep
import os
import math
import csv
import itertools as it
import random

from beamngpy import BeamNGpy, Vehicle, Scenario, Road, setup_logging
from beamngpy.sensors import Electrics
from beamngpy.sensors import Camera


positions = list()
directions = list()
distance = list()
speed = {9, 10, 11, 13, 14, 16, 17, 19, 20, 22, 23} 

# Creation main road for the scenario.
#def simu(speed):
for car_speed in speed:
    my_dict={'hopper_transmission' : ['hopper_transmission_4A', 'hopper_transmission_6M_race','hopper_transmission_5M'],
     'tire_R_15x7_alt':['tire_R_225_75_15_standard','tire_R_28_8_15_offroad','tire_R_205_75_15_standard'],
     'brakepad_F':['brakepad_F_semi_race','brakepad_F_race','brakepad_F_premium']}
    allNames = sorted(my_dict)
    combinations = it.product(*(my_dict[Name] for Name in allNames))
    #print(list(combinations))

    for x in list(combinations):
        # Calling BeamngPY
        bng = BeamNGpy('localhost', 64324, home='C:/Beamng/trunk')

        # Create a scenario in asfault map with scenario name 'indicatorsT1'.
        scenario = Scenario('asfault', 'euroT1')

        # Properties for list of vehicles.

        original_vehicle1 = (803.1582641601562, -283.4632263183594, 0.20022384822368622)
        vehicle1 = Vehicle('ego_vehicle', model='hopper', licence='Main01', color = 'White')

        original_vehicle2 = (530.0204467773438, 8.33481502532959, 0.1997339278459549)
        vehicle2 = Vehicle('green_vehicle', model='van', licence='Main02', colour='Yellow')



        # Add vehicles to our scenario at this position and rotation.

        scenario.add_vehicle(vehicle1, pos=original_vehicle1, rot=(0, 0, 90))

        scenario.add_vehicle(vehicle2, pos=original_vehicle2, rot=(0, 0, 100))
        road = Road('road_rubber_sticky', rid='main_road', texture_length=16)
        road.nodes = [
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
         ]


        road.improved_spline = 0
        road.over_object = 1
        road.break_angle = 180



        # We create Divider for the scenario.

        road2 = Road('BlankWhite', rid='divider_1_1', texture_length=16)
        road2.nodes = [
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
        ]


        road2.drivability = -1
        road2.improved_spline = 0
        road2.over_object = 1
        road2.break_angle = 180
        road2.render_priority = 9




        # Creation of Left side Boundary for the scenario.

        road3 = Road('strap', rid='boundary_1_l1', texture_length=16)
        road3.nodes = [
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
        ]



        road3.drivability = -1
        road3.improved_spline = 0
        road3.over_object = 1
        road3.break_angle = 180
        road3.render_priority = 9



        # Creation of Right side Boundary for the scenario.

        road4 = Road('strap', rid='boundary_1_r1', texture_length=16)
        road4.nodes = [
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

        scenario.make(bng)
        bng.open()
        bng.load_scenario(scenario)
        bng.start_scenario()



        config_trans = vehicle1.get_part_config()
        config_trans['parts']['hopper_transmission'] = x[1]
        set_config_trans = vehicle1.set_part_config(config_trans)

        if (x[1] == 'hopper_transmission_4A'):
            trans_mission = 'transmission1'
        elif (x[1] == 'hopper_transmission_6M_race'):
            trans_mission = 'transmission2'
        else:
            trans_mission = 'transmission3'


        config_tire = vehicle1.get_part_config()
        config_tire['parts']['tire_R_15x7_alt'] = x[2]
        set_config_tire = vehicle1.set_part_config(config_tire)

        if (x[2] == 'tire_R_225_75_15_standard'):
            tire_main = 'tire1'
        elif (x[2] == 'tire_R_28_8_15_offroad'):
            tire_main = 'tire2'
        else:
            tire_main = 'tire3'

        config_brake = vehicle1.get_part_config()
        config_brake['parts']['brakepad_F'] = x[0]
        set_config_brake = vehicle1.set_part_config(config_brake)

        if (x[0] == 'brakepad_F_semi_race'):
            brake_main = 'brake1'
        elif (x[0] == 'brakepad_F_race'):
            brake_main = 'brake2'
        else:
            brake_main = 'brake3'

        config = vehicle1.get_part_config()
        print(config)

        vehicle1.ai_set_speed(car_speed, 'set')
        if car_speed == 9:
            car_speed_km = 30
        elif car_speed == 10:
            car_speed_km = 35
        elif car_speed == 11:
            car_speed_km = 40
        elif car_speed == 13:
            car_speed_km = 45
        elif car_speed == 14:
            car_speed_km = 50
        elif car_speed == 16:
            car_speed_km = 55
        elif car_speed == 17:
            car_speed_km = 60
        elif car_speed == 19:
            car_speed_km = 65
        elif car_speed == 20:
            car_speed_km = 70
        elif car_speed == 22:
            car_speed_km = 75
        else:
            car_speed_km = 80
        vehicle1.ai_set_mode('span')
        vehicle1.ai_drive_in_lane(True)

        positions = list()
        directions = list()
        distance = list()



        for index in range(100000):
            time.sleep(0.1)



            #vehicle1 = scenario.get_vehicle('ego_vehicle')
            vehicle1.update_vehicle()  # Synchs the vehicle's "state" variable with the simulator
            sensors = bng.poll_sensors(vehicle1)

            #vehicle2 = scenario.get_vehicle('green_vehicle')
            vehicle2.update_vehicle()
            sensors = bng.poll_sensors(vehicle2)


            ispass = -1

            # Collecting position and direction for the vehicles in the scenario.
            directions.append(vehicle1.state['dir'])
            direction_car = geometry.Point(vehicle1.state['dir'])
            #display(vehicle1.state['dir'])
            newdirection_road = geometry.Point(vehicle1.state['dir'])
            positions.append(vehicle1.state['pos'])
            #display(vehicle1.state['pos'])
            positions.append(vehicle2.state['pos'])
            #display(vehicle2.state['pos'])

            vehiclepos = vehicle1.state['pos']
            vehiclepos2 = vehicle2.state['pos']

            newposition_Vehicle1 = geometry.Point(vehicle1.state['pos'])
            newposition_Vehicle2 = geometry.Point(vehicle2.state['pos'])

            vehicle_distance1 = newposition_Vehicle2.distance(newposition_Vehicle1)
            print('distance', vehicle_distance1)

            if (vehicle_distance1 <= 20 and car_speed_km == 30) or (vehicle_distance1 <= 20 and car_speed_km == 35) or (vehicle_distance1 <= 23 and car_speed_km == 40) :
                vehicle1.ai_set_mode('stopping')
                time.sleep(5)

                if (vehicle_distance1 > 21):  # 18
                    ispass = 1
                    print('pass')
                else:
                    ispass = 0
                    print('fail')

                if (ispass == 1 or ispass == 0):
                    path_dir = os.getcwd()
                    file_name_csv = (path_dir + '\dataset_van.csv')
                    #fileEmpty = os.stat(file_name_csv).st_size == 0
                    v = random.randint(0, 100)
                    #with open(r'C:\Users\hamza\OneDrive\Desktop\Boundary\datset.csv', 'a') as f:
                    with open(file_name_csv, 'a') as f:
                        headers = ['Brake', 'Transmission', 'Tire', 'Speed', 'Car_model', 'Result']
                        writer = csv.DictWriter(f,delimiter=',', lineterminator='\n',fieldnames=headers)
                        fileEmpty = os.stat(file_name_csv).st_size == 0
                        if fileEmpty:
                            writer.writeheader()
                        writer.writerow({ 'Tire': tire_main ,'Brake' : brake_main ,'Transmission' : trans_mission, 'Car_model': 'hopper' , 'Speed': car_speed_km, 'Result' : ispass})
                break
            elif (vehicle_distance1 < 27 and car_speed_km == 45) or (vehicle_distance1 <= 30 and car_speed_km == 50) or (vehicle_distance1 <= 32 and car_speed_km == 55) :
                vehicle1.ai_set_mode('stopping')
                print(vehicle_distance1)
                time.sleep(5)

                if ( vehicle_distance1 > 30 ):
                    ispass = 1
                    print('pass')
                else:
                    ispass = 0
                    print('fail')

                if (ispass == 1 or ispass == 0):
                    path_dir = os.getcwd()
                    file_name_csv = (path_dir + '\dataset_van.csv')
                    v = random.randint(0, 100)
                    #with open(r'C:\Users\hamza\OneDrive\Desktop\Boundary\datset.csv', 'a') as f:
                    with open(file_name_csv, 'a') as f:
                        headers = ['Brake', 'Transmission', 'Tire', 'Speed', 'Car_model', 'Result']
                        writer = csv.DictWriter(f,delimiter=',', lineterminator='\n',fieldnames=headers)
                        fileEmpty = os.stat(file_name_csv).st_size == 0
                        if fileEmpty:
                            writer.writeheader()
                        writer.writerow({ 'Tire': tire_main ,'Brake' : brake_main ,'Transmission' : trans_mission, 'Car_model': 'hopper' , 'Speed': car_speed_km, 'Result' : ispass})
                break
            elif (vehicle_distance1 <= 35 and car_speed_km == 60) or (vehicle_distance1 <= 40 and car_speed_km == 65) or (vehicle_distance1 <= 45 and car_speed_km == 70) :
                vehicle1.ai_set_mode('stopping')
                time.sleep(5)

                if (vehicle_distance1 > 37):
                    ispass = 1
                    print('pass')
                else:
                    ispass = 0
                    print('fail')

                if (ispass == 1 or ispass == 0):
                    path_dir = os.getcwd()
                    file_name_csv = (path_dir + '\dataset_van.csv')
                    v = random.randint(0, 100)
                    #with open(r'C:\Users\hamza\OneDrive\Desktop\Boundary\datset.csv', 'a') as f:
                    with open(file_name_csv, 'a') as f:
                        headers = ['Brake', 'Transmission', 'Tire', 'Speed', 'Car_model', 'Result']
                        writer = csv.DictWriter(f,delimiter=',', lineterminator='\n',fieldnames=headers)
                        fileEmpty = os.stat(file_name_csv).st_size == 0
                        if fileEmpty:
                            writer.writeheader()
                        writer.writerow({ 'Tire': tire_main ,'Brake' : brake_main ,'Transmission' : trans_mission, 'Car_model': 'hopper' , 'Speed': car_speed_km, 'Result' : ispass})
                break
            elif (vehicle_distance1 <= 50 and car_speed_km == 75) or (vehicle_distance1 <= 55 and car_speed_km == 80) :
                vehicle1.ai_set_mode('stopping')
                time.sleep(5)

                if (vehicle_distance1 > 48):
                    ispass = 1
                    print('pass')
                else:
                    ispass = 0
                    print('fail')

                if (ispass == 1 or ispass == 0):
                    path_dir = os.getcwd()
                    file_name_csv = (path_dir + '\dataset_van.csv')
                    v = random.randint(0, 100)
                    #with open(r'C:\Users\hamza\OneDrive\Desktop\Boundary\datset.csv', 'a') as f:
                    with open(file_name_csv, 'a') as f:
                        headers = ['Brake', 'Transmission', 'Tire', 'Speed', 'Car_model', 'Result']
                        writer = csv.DictWriter(f,delimiter=',', lineterminator='\n',fieldnames=headers)
                        fileEmpty = os.stat(file_name_csv).st_size == 0
                        if fileEmpty:
                            writer.writeheader()
                        writer.writerow({ 'Tire': tire_main ,'Brake' : brake_main ,'Transmission' : trans_mission, 'Car_model': 'hopper' , 'Speed': car_speed_km, 'Result' : ispass})
                break

        bng.stop_scenario()
        bng.close()
