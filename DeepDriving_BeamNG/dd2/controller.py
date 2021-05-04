import math
from collections import deque

def clamp(the_value, min_value, max_value):
    return max(min(the_value, max_value), min_value)

def calcLinScale(Value, MinValue, MinReturn, MaxValue, MaxReturn):
    Value = clamp(Value, MinValue, MaxValue)
    Gain = (Value - MinValue) / (MaxValue - MinValue)
    return MinReturn + (MaxReturn - MinReturn) * Gain

def reshape_steering(original_steering_value):
    return calcLinScale(original_steering_value, -1.0, -1.0, 1.0, 1.0)


class DrivingController:
    """ This class implements the original controller but in Pyton instead of C"""

    mMaxSpeed = 21
    mMinSpeed = 3
    mMaxCurvySpeed = 14
    mLanes = 1
    mSafetyDistance = 10

    slow_down = None
    pre_dist_L = None
    pre_dist_R = None
    left_clear = None
    left_timer = None
    right_clear = None
    right_timer = None
    timer_set = None
    lane_change = None
    steer_trend = None
    steering_record = None
    coe_steer = None
    center_line = None
    pre_ML = None
    pre_MR = None
    steering_head = None
    desired_speed = None

    def __init__(self):
        self.slow_down = 0
        self.pre_dist_L = 60
        self.pre_dist_R = 60
        self.eft_clear = 0
        self.left_timer = 0
        self.right_clear = 0
        self.right_timer = 0
        self.timer_set = 150
        self.lane_change = 0
        self.steer_trend = 0
        self.steering_record = deque(maxlen=5)
        self.coe_steer = 1.0
        self.center_line = 0
        self.pre_ML = 0
        self.pre_MR = 0
        self.desired_speed = 0

    def configure(self, lanes, MaxSpeed, MinSpeed, SafetyDistance):
        self.mLanes = lanes
        # Inside the controller everything should be m/s
        self.mMaxSpeed = MaxSpeed / 3.6
        self.mMinSpeed = MinSpeed / 3.6
        self.mSafetyDistance = SafetyDistance

        print("Controller initialized with:")
        print(" Lanes : ", self.mLanes)
        print(" Min Speed : ", self.mMinSpeed)
        print(" Max Speed : ", self.mMaxSpeed)

    def control(self, indicators):
        if self.mLanes == 1:
            # Must drive on the current lane
            return self._controlLane1(indicators)
        elif self.mLanes == 2:
            # Can switch to a different lane (either left or right)
            return self._controlLane2(indicators)
        else:
            # Can switch to both left or right lanes
            return self._controlLane3(indicators)

    def _controlLane1(self, rIndicators):
        """ Control is computed in two step. Step 1 steering, Step 2 speed control"""
        # NEGATIVE HEADING ANGLES INDICATE THE CAR IS GOING TOWARDS LEFT

        target_speed = self.mMaxSpeed
        road_width = 4.0

        if math.fabs(rIndicators.MR + rIndicators.ML) < road_width + 1.0:
            print("Driving inside the lane")
            # TODO This might need to change
            coe_steer = 1.5

            # Positive center_line indicates the EGO CAR IS on the LEFT of the center_line
            center_line = (rIndicators.MR + rIndicators.ML) / 2

            # TODO No idea about this one...
            self.pre_ML = rIndicators.ML
            self.pre_MR = rIndicators.MR

            # rIndicators.M takes the value of min(math.fabs(ML), math.fabs(MR))
            # Increasing 0.8 should make the car react faster
            if math.fabs(rIndicators.M) < 0.8:
                print("Car is to close to edge of the lane, steer more")
               # The lower the coefficient the higher is the response of the car
                coe_steer = 0.2

            # Inside the lane we can adopt a style of driving which combines the heading angle and the distance
            # since every quantity is bounded.
            absolute_steering = (rIndicators.Angle - (center_line / road_width)) / coe_steer

            # We are in the middle of the road, but we need to turn a lot
            if coe_steer > 1 and absolute_steering > 0.1:
                print("In the road, but hard turn")
                absolute_steering = absolute_steering * (2.5 * absolute_steering + 0.75)
        else:
            print("Driving outside the lane")

            # TODO No idea about the past observation...
            # If we are outside the lane try to drive back
            if self.pre_ML == self.pre_MR:
                # Decide whether we are on the right or the left
                self.pre_ML = rIndicators.ML
                self.pre_MR = rIndicators.MR

            if math.fabs(self.pre_ML) > math.fabs(self.pre_MR):
                # We are on the RIGHT side of the off road, we need to go back so go LEFT
                # TODO Check L should be something like - 7.0
                center_line = (rIndicators.L + rIndicators.M) / 2
                targetHeadingAngle = + math.radians(90.0)
            else:
                # We are on the LEFT side of the off road, we need to go back, so go RIGHT
                # TODO Check R something like +7.0
                center_line = (rIndicators.R + rIndicators.M) / 2
                targetHeadingAngle = - math.radians(90.0)

            # We are outside the road, and we need to get back there as soon as possible
            # by driving towards the road (perpendicular). However, since we need to make some progress
            # we interpolate this with the traffic_direction. as we get closer to the road/center line
            # As long as we are far away we need the first term, then the second
            long_distance = 1.0 if math.fabs( center_line ) > 10 else 0.5 if math.fabs( center_line ) > 5.0 else 0.2
            short_distance = 1.0 - long_distance

            absolute_steering = long_distance * (rIndicators.Angle + targetHeadingAngle) + short_distance * rIndicators.Angle

        print("Distance to center", center_line)
        print("Heading Angler", rIndicators.Angle, math.degrees(rIndicators.Angle),
              math.radians(math.degrees(rIndicators.Angle)))

        # Build the control object and fill it with ANGLE
        rControl = dict()

        print("Computed steering command", absolute_steering)

        # Store the intensity of past steering actions before reshaping
        self.steering_record.appendleft(math.fabs(absolute_steering))

        # Linearly scale the steering
        reshaped_steering = reshape_steering(absolute_steering)

        print("Reshaped steering command", reshaped_steering)

        # NOTE THIS ONE !!!
        if reshaped_steering > 0:
            print("Ego car will turn LEFT")
        elif reshaped_steering < 0:
            print("Ego car will turn RIGHT")
        else:
            print("Ego car can go straight")

        # DO NOT EVEN STEER IF THE ANGLE IS TOO SMALL?
        # BEAMNG USES A DIFFERENT CONVERSION FOR STEERING *NEGATIVE MEANS LEFT*
        rControl['steering'] = -1.0 * reshaped_steering

        # Target speed is always max speed because there are no obstacles on the road
        return self._calcAccelerating(rControl, rIndicators, target_speed)

    def _calcAccelerating(self, rControl, rIndicators, TargetSpeedFromController):

        CurrentSpeed = rIndicators.Speed
        FullSpeed = self.mMaxSpeed

        # Throttle GAIN
        Kpa = 0.1
        # Braking GAIN 0.2 - 0.4
        Kpb = 0.4

        # TODO Why steering and to past heading angles ?
        # THE SPEED OF THE CAR SHOULD BE PROPORTIONAL TO THE SHARPNESS OF THE CURVE TO MAKE
        # WE ESTIMATE THE SHARPNESS OF THE CURVE BY LOOKING AT THE PAST STEERING ACTIONS
        # Compute a weighted average insted of the sum to understand how sharp is the turn
        # weights = [10, 5, 5, 2, 1]
        # weighted_average = sum(x * y for x, y in zip(self.steering_record, weights)) / sum(weights[:len(self.steering_record)])
        # CurvySpeed = self.mMaxSpeed - weighted_average * 3.5
        # TODO THIS SHALL BE REVISED A BIT

        cumulative_steering = math.fabs(sum(self.steering_record))
        CurvySpeed = self.mMaxSpeed - cumulative_steering * 12.0 # 4.5

        # This one will be always the one adopted by the contrller

        # Ideally CurvySpeed is closer to target speed if weighet_average goes to zero (i.e., straight line or car aligned with road)
        # Do not default to CURVY SPEED instead combine it with a predictor, Fast, that tells if we can go fast. It's a probability value
        # Fast can be the alignment of the car with the road: the more we are aligned the faster we can go
        # If the car is entering or inside a turn, it MUST slow down

        #
        if math.radians(2.0) < math.fabs(rIndicators.Angle) <= math.radians(4.0):
            reduce_by_headig_angle = 0.2
        elif math.radians(4.0) < math.fabs(rIndicators.Angle) <= math.radians(8.0):
            reduce_by_headig_angle = 0.4
        elif math.radians(8.0) < math.fabs(rIndicators.Angle) < math.radians(15.0):
            reduce_by_headig_angle = 0.6
        elif math.fabs(rIndicators.Angle) > math.radians(15.0):
            reduce_by_headig_angle = 0.8
        else:
            reduce_by_headig_angle = 0.0

        if 0 <= math.fabs(rIndicators.M) < 0.5:
            reduce_by_distance = 0.8
        elif 0.5 <= math.fabs(rIndicators.M) < 0.8:
            reduce_by_distance = 0.6
        elif 0.8 <= math.fabs(rIndicators.M) < 1.2:
            reduce_by_distance = 0.2
        else:
            reduce_by_distance = 0.0

        Fast = 1.0 - reduce_by_headig_angle - reduce_by_distance
        Fast = clamp(Fast, 0.0, 1.0)

        ResultSpeed = min(Fast * FullSpeed + (1 - Fast) * CurvySpeed, TargetSpeedFromController)
        print("P(Fast)=", Fast, FullSpeed, CurvySpeed, TargetSpeedFromController, "-->", ResultSpeed)

        DeltaSpeed = ResultSpeed - CurrentSpeed

        if TargetSpeedFromController > 0.0:
            if DeltaSpeed >= 0:
                rControl['braking'] = 0.0
                rControl['throttle'] = Kpa * DeltaSpeed
            else:
                # // This is basically a PID controller for the speed
                # // This is the "fix", we cannot go less than mMinSpeed
                if CurrentSpeed < self.mMinSpeed:
                    rControl['braking'] = 0.0
                    rControl['throttle'] = Kpa * self.mMinSpeed
                else:
                    # // Brake only if really needed, and brake more if DeltaSpeed
                    # // is Large
                    rControl['throttle'] = 0.0
                    rControl['braking'] = - Kpb * DeltaSpeed
        else:
            print("Emergency Brake.")
            # Perform an emergency break
            rControl['throttle'] = 0.0
            rControl['braking'] = 1.0

        # Ensure the controls are within the range
        acc_gain = 0.5
        brake_gain = 1.0

        rControl['throttle'] = rControl['throttle'] * acc_gain
        rControl['braking'] = rControl['braking'] * brake_gain

        return rControl

    def _controlLane2(self, rIndicators):
        return NotImplementedError

    def _controlLane3(self, rIndicators):
        return NotImplementedError

    #
    #     public Control controlLane2(Indicators rIndicators) {
    #         slow_down = mMaxSpeed
    #
    #         boolean IsFast = isFast(rIndicators.Fast)
    #
    #         if (pre_dist_L < 20 && rIndicators.DistLL < 20) {
    #             // left lane is occupied or not
    #             left_clear = 0
    #             left_timer = 0
    #         } else
    #             left_timer++
    #
    #         if (pre_dist_R < 20 && rIndicators.DistRR < 20) {
    #             // right lane is occupied or not
    #             right_clear = 0
    #             right_timer = 0
    #         } else
    #             right_timer++
    #
    #         pre_dist_L = rIndicators.DistLL
    #         pre_dist_R = rIndicators.DistRR
    #
    #         if (left_timer > timer_set) {
    #             // left lane is clear
    #             left_timer = timer_set
    #             left_clear = 1
    #         }
    #
    #         if (right_timer > timer_set) {
    #             // right lane is clear
    #             right_timer = timer_set
    #             right_clear = 1
    #         }
    #
    #         if (lane_change == 0 && rIndicators.DistMM < 25) {
    #             // if current lane is occupied
    #
    #             steer_trend = steering_record[0] + steering_record[1] + steering_record[2] + steering_record[3]
    #                     + steering_record[4]
    #             // am I turning or not
    #
    #             if (rIndicators.LL > -8 && left_clear == 1 && steer_trend >= 0 && IsFast) {
    #                 // move to left lane
    #                 lane_change = -2
    #                 coe_steer = 2
    #                 right_clear = 0
    #                 right_timer = 0
    #                 left_clear = 0
    #                 left_timer = 0
    #                 // timer_set=30
    #             }
    #
    #             else if (rIndicators.RR < 8 && right_clear == 1 && steer_trend <= 0 && IsFast) {
    #                 // move to right lane
    #                 lane_change = 2
    #                 coe_steer = 2
    #                 left_clear = 0
    #                 left_timer = 0
    #                 right_clear = 0
    #                 right_timer = 0
    #                 // timer_set=30
    #             }
    #         }
    #
    #         ///////////////////////////////////////////////// prefer to stay in the
    #         ///////////////////////////////////////////////// right lane
    #         else if (lane_change == 0 && rIndicators.DistMM >= 25) {
    #
    #             steer_trend = steering_record[0] + steering_record[1] + steering_record[2] + steering_record[3]
    #                     + steering_record[4] // am I turning or not
    #
    #             if (rIndicators.LL < -8 && right_clear == 1 && steer_trend <= 0 && steer_trend > -0.2 && IsFast) {
    #                 // in left lane, move to right lane lane_change = 2
    #                 coe_steer = 2
    #                 right_clear = 0
    #                 right_timer = 0
    #             }
    #         }
    #         ///////////////////////////////////////////////// END prefer to stay in
    #         ///////////////////////////////////////////////// the right lane
    #
    #         if (rIndicators.DistMM < 25) {
    #             double v_max = mMaxSpeed
    #             double c = 2.772
    #             double d = -0.693
    #             // optimal vilocity car-following model
    #             slow_down = v_max * (1 - Math.exp(-c / v_max * (rIndicators.DistMM) - d))
    #             if (slow_down < 0)
    #                 slow_down = 0
    #         }
    #
    #         if (rIndicators.DistMM < mSafetyDistance) {
    #             slow_down = 0
    #         }
    #
    #         ///////////////////////////////////////////////// implement lane
    #         ///////////////////////////////////////////////// changing or
    #         ///////////////////////////////////////////////// car-following
    #         if (lane_change == 0) {
    #             if (-rIndicators.ML + rIndicators.MR < 5.5) {
    #
    #                 center_line = (rIndicators.ML + rIndicators.MR) / 2
    #                 coe_steer = calcLinScale(Math.abs(center_line), 0.25, 1.5, 0.75, 0.5)
    #
    #                 pre_ML = rIndicators.ML
    #                 pre_MR = rIndicators.MR
    #                 if ((rIndicators.M < 1) && (rIndicators.M > -1))
    #                     coe_steer = 0.4
    #             } else {
    #                 if (-pre_ML > pre_MR)
    #                     center_line = (rIndicators.L + rIndicators.M) / 2
    #                 else
    #                     center_line = (rIndicators.R + rIndicators.M) / 2
    #                 coe_steer = 0.3
    #             }
    #         }
    #
    #         else if (lane_change == -2) {
    #             if (-rIndicators.ML + rIndicators.MR < 5.5) {
    #                 center_line = (rIndicators.LL + rIndicators.ML) / 2
    #                 if (rIndicators.L > -5 && (rIndicators.M < 1.5) && (rIndicators.M > -1.5)) {
    #                     if (-rIndicators.L > 3) {
    #                         center_line = (center_line + (rIndicators.L + rIndicators.M) / 2) / 2
    #                     } else {
    #                         coe_steer = 1
    #                         if (rIndicators.M < 1.25) {
    #                             lane_change = 0
    #                         }
    #                     }
    #                 }
    #             } else {
    #                 center_line = (rIndicators.L + rIndicators.M) / 2
    #                 coe_steer = 1
    #                 lane_change = -1
    #             }
    #         }
    #
    #         else if (lane_change == -1) {
    #             if (rIndicators.L > -5 && rIndicators.M < 1.5) {
    #                 center_line = (rIndicators.L + rIndicators.M) / 2
    #                 if (-rIndicators.ML + rIndicators.MR < 5.5)
    #                     center_line = (center_line + (rIndicators.ML + rIndicators.MR) / 2) / 2
    #             } else {
    #                 center_line = (rIndicators.ML + rIndicators.MR) / 2
    #                 lane_change = 0
    #             }
    #         }
    #
    #         else if (lane_change == 2) {
    #             if (-rIndicators.ML + rIndicators.MR < 5.5) {
    #                 center_line = (rIndicators.RR + rIndicators.MR) / 2
    #                 if (rIndicators.R < 5 && (rIndicators.M < 1.5) && (rIndicators.M > -1.5)) {
    #                     if (rIndicators.R > 3) {
    #                         center_line = (center_line + (rIndicators.R + rIndicators.M) / 2) / 2
    #                     } else {
    #                         coe_steer = 1
    #                         if (rIndicators.M > -1.25) {
    #                             lane_change = 0
    #                         }
    #                     }
    #                 }
    #             } else {
    #                 center_line = (rIndicators.R + rIndicators.M) / 2
    #                 coe_steer = 1
    #                 lane_change = 1
    #             }
    #         }
    #
    #         else if (lane_change == 1) {
    #             if (rIndicators.R < 5 && rIndicators.M < 1.5) {
    #                 center_line = (rIndicators.R + rIndicators.M) / 2
    #                 if (-rIndicators.ML + rIndicators.MR < 5.5)
    #                     center_line = (center_line + (rIndicators.ML + rIndicators.MR) / 2) / 2
    #             } else {
    #                 center_line = (rIndicators.ML + rIndicators.MR) / 2
    #                 lane_change = 0
    #             }
    #         }
    #         ///////////////////////////////////////////////// END implement lane
    #         ///////////////////////////////////////////////// changing or
    #         ///////////////////////////////////////////////// car-following
    #
    #         double road_width = 2 * 4.0
    #
    #         Control rControl = new Control()
    #         rControl['steering'] = (rIndicators.Angle - center_line / road_width) / coe_steer
    #
    #         // reshape the steering control curve
    #         if (lane_change == 0 && coe_steer > 1 && rControl['steering'] > 0.1)
    #             rControl['steering'] = rControl['steering'] * (2.5 * rControl['steering'] + 0.75)
    #
    #         // update previous steering record
    #         steering_record[steering_head] = rControl['steering']
    #         steering_head++
    #         if (steering_head == 5)
    #             steering_head = 0
    #
    #         return calcAccelerating(rControl, rIndicators.Fast, rIndicators.Speed, slow_down)
    #     }
    #
    #     public Control controlLane3(Indicators rIndicators) {
    #         slow_down = mMaxSpeed
    #         boolean IsFast = isFast(rIndicators.Fast)
    #
    #         if (pre_dist_L < 20 && rIndicators.DistLL < 20) { // left lane is
    #                                                           // occupied or not
    #             left_clear = 0
    #             left_timer = 0
    #         } else
    #             left_timer++
    #
    #         if (pre_dist_R < 20 && rIndicators.DistRR < 20) { // right lane is
    #                                                           // occupied or not
    #             right_clear = 0
    #             right_timer = 0
    #         } else
    #             right_timer++
    #
    #         pre_dist_L = rIndicators.DistLL
    #         pre_dist_R = rIndicators.DistRR
    #
    #         if (left_timer > timer_set) { // left lane is clear
    #             left_timer = timer_set
    #             left_clear = 1
    #         }
    #
    #         if (right_timer > timer_set) { // right lane is clear
    #             right_timer = timer_set
    #             right_clear = 1
    #         }
    #
    #         if (lane_change == 0 && rIndicators.DistMM < 25) {
    #             // if current lane is occupied
    #
    #             steer_trend = steering_record[0] + steering_record[1] + steering_record[2] + steering_record[3]
    #                     + steering_record[4] // am I turning or not
    #
    #             if (rIndicators.LL > -8 && left_clear == 1 && steer_trend >= 0 && steer_trend < 0.2 && IsFast) { // move
    #                                                                                                              // to
    #                                                                                                              // left
    #                                                                                                              // lane
    #                 lane_change = -2
    #                 coe_steer = 2
    #                 right_clear = 0
    #                 right_timer = 0
    #                 left_clear = 0
    #                 left_timer = 0
    #                 // timer_set = 60
    #             }
    #
    #             else if (rIndicators.RR < 8 && right_clear == 1 && steer_trend <= 0 && steer_trend > -0.2 && IsFast) { // move
    #                                                                                                                    // to
    #                                                                                                                    // right
    #                                                                                                                    // lane
    #                 lane_change = 2
    #                 coe_steer = 2
    #                 left_clear = 0
    #                 left_timer = 0
    #                 right_clear = 0
    #                 right_timer = 0
    #                 // timer_set = 60
    #             }
    #         }
    #
    #         ///////////////////////////////////////////////// prefer to stay in the
    #         ///////////////////////////////////////////////// central lane
    #         else if (lane_change == 0 && rIndicators.DistMM >= 25) {
    #
    #             steer_trend = steering_record[0] + steering_record[1] + steering_record[2] + steering_record[3]
    #                     + steering_record[4] // am I turning or not
    #
    #             if (rIndicators.RR > 8 && left_clear == 1 && steer_trend >= 0 && steer_trend < 0.2 && IsFast) { // in
    #                                                                                                             // right
    #                                                                                                             // lane,
    #                                                                                                             // move
    #                                                                                                             // to
    #                                                                                                             // central
    #                                                                                                             // lane
    #                 lane_change = -2
    #                 coe_steer = 2
    #                 left_clear = 0
    #                 left_timer = 0
    #             }
    #
    #             else if (rIndicators.LL < -8 && right_clear == 1 && steer_trend <= 0 && steer_trend > -0.2 && IsFast) { // in
    #                                                                                                                     // left
    #                                                                                                                     // lane,
    #                                                                                                                     // move
    #                                                                                                                     // to
    #                                                                                                                     // central
    #                                                                                                                     // lane
    #                 lane_change = 2
    #                 coe_steer = 2
    #                 right_clear = 0
    #                 right_timer = 0
    #             }
    #         }
    #         ///////////////////////////////////////////////// END prefer to stay in
    #         ///////////////////////////////////////////////// the central lane
    #
    #         if (rIndicators.DistMM < 25) {
    #             double v_max = mMaxSpeed
    #             double c = 2.772
    #             double d = -0.693
    #             slow_down = v_max * (1 - Math.exp(-c / v_max * (rIndicators.DistMM) - d)) // optimal
    #                                                                                        // vilocity
    #                                                                                        // car-following
    #                                                                                        // model
    #             if (slow_down < 0)
    #                 slow_down = 0
    #         }
    #
    #         if (rIndicators.DistMM < mSafetyDistance) {
    #             slow_down = 0
    #         }
    #
    #         ///////////////////////////////////////////////// implement lane
    #         ///////////////////////////////////////////////// changing or
    #         ///////////////////////////////////////////////// car-following
    #         if (lane_change == 0) {
    #             if (-rIndicators.ML + rIndicators.MR < 5.5) {
    #                 center_line = (rIndicators.ML + rIndicators.MR) / 2
    #                 coe_steer = calcLinScale(Math.abs(center_line), 0.25, 1.5, 0.75, 0.5)
    #
    #                 pre_ML = rIndicators.ML
    #                 pre_MR = rIndicators.MR
    #                 if ((rIndicators.M < 1) && (rIndicators.M > -1))
    #                     coe_steer = 0.4
    #             } else {
    #                 if (-pre_ML > pre_MR)
    #                     center_line = (rIndicators.L + rIndicators.M) / 2
    #                 else
    #                     center_line = (rIndicators.R + rIndicators.M) / 2
    #                 coe_steer = 0.3
    #             }
    #         }
    #
    #         else if (lane_change == -2) {
    #             if (-rIndicators.ML + rIndicators.MR < 5.5) {
    #                 center_line = (rIndicators.LL + rIndicators.ML) / 2
    #                 if (rIndicators.L > -5 && (rIndicators.M < 1.5) && (rIndicators.M > -1.5)) {
    #                     if (-rIndicators.L > 3) {
    #                         center_line = (center_line + (rIndicators.L + rIndicators.M) / 2) / 2
    #                     } else {
    #                         coe_steer = 1
    #                         if (rIndicators.M < 1.25) {
    #                             lane_change = 0
    #                         }
    #                     }
    #                 }
    #             } else {
    #                 center_line = (rIndicators.L + rIndicators.M) / 2
    #                 coe_steer = 1
    #                 lane_change = -1
    #             }
    #         }
    #
    #         else if (lane_change == -1) {
    #             if (rIndicators.L > -5 && rIndicators.M < 1.5) {
    #                 center_line = (rIndicators.L + rIndicators.M) / 2
    #                 if (-rIndicators.ML + rIndicators.MR < 5.5)
    #                     center_line = (center_line + (rIndicators.ML + rIndicators.MR) / 2) / 2
    #             } else {
    #                 center_line = (rIndicators.ML + rIndicators.MR) / 2
    #                 lane_change = 0
    #             }
    #         }
    #
    #         else if (lane_change == 2) {
    #             if (-rIndicators.ML + rIndicators.MR < 5.5) {
    #                 center_line = (rIndicators.RR + rIndicators.MR) / 2
    #                 if (rIndicators.R < 5 && (rIndicators.M < 1.5) && (rIndicators.M > -1.5)) {
    #                     if (rIndicators.R > 3) {
    #                         center_line = (center_line + (rIndicators.R + rIndicators.M) / 2) / 2
    #                     } else {
    #                         coe_steer = 1
    #                         if (rIndicators.M > -1.25) {
    #                             lane_change = 0
    #                         }
    #                     }
    #                 }
    #             } else {
    #                 center_line = (rIndicators.R + rIndicators.M) / 2
    #                 coe_steer = 1
    #                 lane_change = 1
    #             }
    #         }
    #
    #         else if (lane_change == 1) {
    #             if (rIndicators.R < 5 && rIndicators.M < 1.5) {
    #                 center_line = (rIndicators.R + rIndicators.M) / 2
    #                 if (-rIndicators.ML + rIndicators.MR < 5.5)
    #                     center_line = (center_line + (rIndicators.ML + rIndicators.MR) / 2) / 2
    #             } else {
    #                 center_line = (rIndicators.ML + rIndicators.MR) / 2
    #                 lane_change = 0
    #             }
    #         }
    #         ///////////////////////////////////////////////// END implement lane
    #         ///////////////////////////////////////////////// changing or
    #         ///////////////////////////////////////////////// car-following
    #
    #         Control rControl = new Control()
    #
    #         double road_width = 3 * 4.0
    #
    #         rControl['steering'] = (rIndicators.Angle - center_line / road_width) / coe_steer
    #
    #         if (lane_change == 0 && coe_steer > 1 && rControl['steering'] > 0.1) // reshape
    #                                                                           // the
    #                                                                           // steering
    #                                                                           // control
    #                                                                           // curve
    #             rControl['steering'] = rControl['steering'] * (2.5 * rControl['steering'] + 0.75)
    #
    #         steering_record[steering_head] = rControl['steering'] // update previous
    #                                                             // steering record
    #         steering_head++
    #         if (steering_head == 5)
    #             steering_head = 0
    #
    #         return calcAccelerating(rControl, rIndicators.Fast, rIndicators.Speed, slow_down)
    #     }
    #
    #     public static double clamp(double Value, double Max, double Min) {
    #         return Math.max(Min, Math.min(Max, Value))
    #     }
    #
    #     // Problem: The original implementation gets stuck if the speed is zero and
    #     // the
    #     // car is "turning"
    #     // Solution: define a minimum speed if current speed and result speed are
    #     // both
    #     // <= 0.0
    #     // This version fixes the behavior by enforcing a minimum speed
    #