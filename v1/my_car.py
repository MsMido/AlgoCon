import v1.DrivingInterface.drive_controller

from v1.DrivingInterface.drive_controller import DrivingController
import  math

is_accident = False  # 충돌 발생 여부
accident_count = 0  # 정지상태에서 카운트 -> 정지상태 여부 체크
recovery_count = 0  # 후진을 언제까지 할지 판단
set_brake = 0.0
set_throttle = 1
break_count = 0
accident_angle = 0
accident_dist = 0
forward_flag = True
class DrivingClient(DrivingController):
    import math
    _count = 0
    _newMiddle = 0
    _fullBrake = False
    _brakeSpeed = 200
    _position = -100
    _roadWidth = 10

    def __init__(self):
        # =========================================================== #
        #  Area for member variables =============================== #
        # =========================================================== #
        # Editing area starts from here
        #

        self.is_debug = True

        #
        # Editing area ends
        # ==========================================================#
        super().__init__()
    def control_driving(self, car_controls, sensing_info):
        global set_brake
        global set_throttle
        global is_accident
        global accident_count
        global recovery_count
        global break_count
        global accident_angle
        global accident_dist
        global forward_flag
        # =========================================================== #
        # Area for writing code about driving rule ================= #
        # =========================================================== #
        # Editing area starts from here
        #
        # self.is_debug = True
        self._roadWidth = self.half_road_limit

        if not is_accident:
            set_brake = 0.0
            set_throttle = 1
        # 속도가 고속일때만 먼곳 확인 필요/ 조정 예정
        if sensing_info.speed > 200:
            angle_num = int(sensing_info.speed / 20)
        elif sensing_info.speed > 150:
            angle_num = int(sensing_info.speed / 60)
        else:
            angle_num = int(sensing_info.speed / 85)

        # speed에 맞춰 전방의 커브들의 평균을 사용 - speed 고려 부분 추가 필요
        if angle_num > 8:
            angle_num = 8

        ref_angle = (sensing_info.track_forward_angles[angle_num] + sensing_info.track_forward_angles[angle_num + 1]) / 2.5
        # 도로 위치에 따른 보정값 1-6
        if self._position < -99:
            self._position = (sensing_info.to_middle + 6) % 6
        if abs(sensing_info.to_middle)- 1 > self._roadWidth and abs(sensing_info.moving_angle) < 1:
            self._position = (sensing_info.to_middle + 6) % 6
        if len(sensing_info.track_forward_obstacles) > 0:
            fwd_obstacle = sensing_info.track_forward_obstacles[0]
            if abs(fwd_obstacle['to_middle']) < 1:
                self._position = 2
            else:
                self._position = 5
        target_dist = self._roadWidth / 2 - (1.35 * self._position)  # 1.35는 차폭의절반
        self._newMiddle = target_dist + sensing_info.to_middle # 타겟 위치에 맞는 중앙값 보정
        middle_add = ((target_dist + self._newMiddle) / 400) * -1  # 타겟값을 지나갈때 스티어링을 반대로 쳐주는 카운터
        set_steering = (ref_angle - sensing_info.moving_angle) / (sensing_info.speed + 0.1)
        first_steering = set_steering  # 값확인용
        set_steering -= (self._newMiddle / (sensing_info.speed + 0.1))

        second_steering = set_steering  # 값확인용
        set_steering += middle_add/1000  # 최종 스티어링값
        third_steering = set_steering  # 값확인용

        #참조 각 들 추가 및 변경 가능
        angle_short = abs(sensing_info.track_forward_angles[4] - sensing_info.track_forward_angles[0])
        angle_long = abs(sensing_info.track_forward_angles[9] - sensing_info.track_forward_angles[5])
        angle_middle = abs(sensing_info.track_forward_angles[7] - sensing_info.track_forward_angles[3])
        angle_front = abs(sensing_info.track_forward_angles[1] - sensing_info.track_forward_angles[0])
        angle_end = abs(sensing_info.track_forward_angles[9] - sensing_info.track_forward_angles[0])

        brake_angle = int((75 - (sensing_info.speed/4))/10)*10
        if angle_short > 70:
            clean_speed = 140 - (angle_short / 2)
        else:
            clean_speed = 150 - (angle_short / 2)

        fullBrakeSpeed = 140 - (angle_short / 2)
        #중간 brake를 위한 angle값 추가 필요
        if angle_end > brake_angle and angle_long > brake_angle and sensing_info.speed > 160:
            self._fullBrake = True
            if self._brakeSpeed > fullBrakeSpeed:
                self._brakeSpeed = fullBrakeSpeed
        if angle_middle > brake_angle and sensing_info.speed > clean_speed:
            self._fullBrake = True
            self._brakeSpeed = clean_speed
        if sensing_info.speed > clean_speed and angle_short > 9:
            set_brake = 0.2
        if self._fullBrake:
            set_throttle = -1
            set_brake = 1
            if angle_short < brake_angle and angle_end < brake_angle and angle_long < brake_angle:
                self._fullBrake = False
                self._brakeSpeed = 200
            if sensing_info.speed < self._brakeSpeed:
                self._fullBrake = False
                self._brakeSpeed = 200
        if sensing_info.speed > 240:
            set_throttle = 0
        if set_steering > 1:
            set_steering = 1
        if set_steering < -1:
            set_steering = -1


        #급브레이크 판단용 추가 보정 및 로직 추가 필요
        # if angle_short > 30:
        # if sensing_info.speed > 80 :
        # set_throttle -= 0.2
        # #set_brake = 1
        # ##### #
        # 역주행 #
        # ##### #
        # 역주행 하고 있는 경우 핸들 완전 꺾을것
        if sensing_info.moving_forward and forward_flag:
            forward_flag = False
            print("역주행 복구 완료=============================================")
            print("[MyCar] is moving forward: {}".format(sensing_info.moving_forward))
            print("맵 진행률: {}".format(sensing_info.lap_progress))
            print("----------------------------------------------------------")

        if not sensing_info.moving_forward and sensing_info.speed > 5:
            forward_flag = True
            print("역주행====================================================")
            print("[MyCar] is moving forward: {}".format(sensing_info.moving_forward))
            print("[MyCar] moving angle: {}".format(sensing_info.moving_angle))
            print("[MyCar] sensing_info.speed: {}".format(sensing_info.speed))
            print("맵 진행률: {}".format(sensing_info.lap_progress))
            print("----------------------------------------------------------")
            if sensing_info.to_middle > 0:
                set_steering = 1  # 핸들 방향
            else:
                set_steering = -1

        # ################################## #
        # 부딪혔어도 잘 주행하는 경우 카운트 초기화 #
        # ################################## #
        if sensing_info.speed > 70 and accident_count > 0:
            print("accident_count 초기화=====================================")
            print("초기화 전: {}".format(accident_count))
            print("[MyCar] is moving forward: {}".format(sensing_info.moving_forward))
            print("[MyCar] moving angle: {}".format(sensing_info.moving_angle))
            print("맵 진행률: {}".format(sensing_info.lap_progress))
            print("---------------------------------------------------------")
            accident_count = 0

        # ########## #
        # 충돌 시 복구 #
        # ########## #
        # ( 처음 시작 시 제외 ) 차량 속도 체크, 충돌 flag가 충돌이 아니어도 차량 충돌 여부 판단
        # ( 차량 충돌 직후에 장애물로부터 거리가 떨어지면 flag 다시 false되기 때문에 아래와 같은 충돌 체크 필요함. )
        if sensing_info.lap_progress > 0.5 and not is_accident and -5.0 < sensing_info.speed < 1.0:
            accident_count += 1
            print("accident_count 증가=======================================")
            print("[MyCar] sensing_info.speed: {}".format(sensing_info.speed))
            print("accident_count: {}/6".format(accident_count))
            print("맵 진행률: {}".format(sensing_info.lap_progress))
            print("---------------------------------------------------------")
        # 충돌 flag에 대해서는 옆면 충돌, 충돌 후 정상 궤도로 돌아오는 경우 있어 가중치로만 표현
        if sensing_info.collided:
            accident_count += 3
            if len(sensing_info.track_forward_obstacles) > 0:
                if sensing_info.track_forward_obstacles[0]["dist"] < 10:
                    accident_count += 2
            print("충돌 발생!================================================")
            print("accident_count: {}/6".format(accident_count))
            print("차량 속도: {}".format(sensing_info.speed))
            print("[MyCar] track_forward_obstacles: {}".format(sensing_info.track_forward_obstacles))
            print("맵 진행률: {}".format(sensing_info.lap_progress))
            print("---------------------------------------------------------")
        # accident_count 6 이상이면 충돌로 판정
        if accident_count > 5 and not is_accident:
            is_accident = True
            accident_angle = sensing_info.moving_angle
            accident_dist = sensing_info.to_middle
            print("사고 발생!================================================")
            print("현재 차량 각도: {}".format(accident_angle))
            print("현재 차량 중심에서의 거리: {}".format(sensing_info.to_middle))
            print("차량 속도: {}".format(sensing_info.speed))
            print("[MyCar] track_forward_obstacles: {}".format(sensing_info.track_forward_obstacles))
            print("맵 진행률: {}".format(sensing_info.lap_progress))
            print("---------------------------------------------------------")

        # 충돌 판정 시, 충돌로부터 벗어남 (핸들 방향/속도 변경)
        if is_accident and not forward_flag:
            # 핸들 얼마나 꺾을지 값을 통해 조절 가능
            set_steering = 0.6 - (0.066 * recovery_count)
            # 도로와의 정렬값에 따라 핸들 방향 조정  (* 얼마나 중심에서 떨어진지에 대한 수치도 사용하는게 좋을지?)
            # 오른쪽 도로
            if accident_dist > 0:
                if accident_dist < self.half_road_limit / 2:
                    set_steering *= -1
            # 중앙/왼쪽 도로
            else:
                if accident_dist < -self.half_road_limit / 2:
                    set_steering *= -1
            set_brake = 0  # 브레이크

            # print("sensing_info.to_middle: {}".format(sensing_info.to_middle))
            # print("sensing_info.moving_angle: {}".format(sensing_info.moving_angle))
            # print("sensing_info.moving_forward: {}".format(sensing_info.moving_forward))

            # 차 후면이 코스 벽에 닿은 상태에서는 전진하도록 함. 도로 중앙에서의 거리, 차 앵글 확인
            # 정면으로 닿아서 복구 안되는 상태이면 복구 count 확인하여 값을 반대로 바꿔줌.
            if accident_dist > 10 and -50 < accident_angle < 0:
                set_throttle = 1  # 속도
            elif accident_dist < -10 and 0 < accident_angle < 50:
                set_throttle = 1  # 속도
            else:
                set_throttle = -1  # 속도
            # 충돌로부터 복구중이면 1씩 더함
            recovery_count += 1
            # 충돌로부터 복구 하다가 진행방향이 False가 되면 복구 카운트를 다시 줄임( 더 후진/전진하며 회전 하도록 )
            # if sensing_info.moving_forward:
            #     recovery_count -= 1
            #     if sensing_info.moving_angle > 0:
            #         set_steering = 1  # 핸들 방향
            #     else:
            #         set_steering = -1
            print("복구 진행", recovery_count, "=================================================")
            print("사고 판정 시 차량 각도: {}".format(accident_angle))
            print("사고 판정 시 차량 중심에서의 거리: {}".format(accident_dist))
            print("현재 차량 속도: {}".format(sensing_info.speed))
            print("현재 차량 각도: {}".format(sensing_info.moving_angle))
            print("현재 차량 중심에서의 거리: {}".format(sensing_info.to_middle))
            print("세팅 값: set_steering = ", set_steering, "/ set_throttle = ", set_throttle)
            print("[MyCar] track_forward_obstacles: {}".format(sensing_info.track_forward_obstacles))
            print("맵 진행률: {}".format(sensing_info.lap_progress))
            print("---------------------------------------------------------")

        if recovery_count > 9:
            # 벽면에 정면으로 갖다 박고 있을 경우 속도를 반대로 해서 탈출
            set_throttle *= -1  # 속도
            print("복구 불가-반대 방향으로 진행합니다.============================")
            print("set_throttle: {}".format(set_throttle))
            print("set_steering: {}".format(set_steering))
            print("벽이 아닌 장애물 원인인지 확인>")
            print("[MyCar] track_forward_obstacles: {}".format(sensing_info.track_forward_obstacles))
            print("---------------------------------------------------------")
        # 후진 ~회 이상 하면 다시 전진. 복구 시간을 줄이고 싶으면 recovery_count 수를 줄인다.
        # 계속 멈춰있는 상태면 복구된것으로 판정 안함.
        if recovery_count > 8 and not -1.0 < sensing_info.speed < 1.0:
            is_accident = False
            recovery_count = 0
            accident_count = 0
            # 장애물로부터 벗어날 수 있도록 방향 한번 더 꺾어줌
            set_steering *= 1
            set_brake = 0
            # 초기 속도와 맞춰줘야함.
            set_throttle = 1
            print("복구 완료=================================================")
            print("사고 판정 시 차량 각도: {}".format(accident_angle))
            print("사고 판정 시 차량 중심에서의 거리: {}".format(accident_dist))
            print("현재 차량 속도: {}".format(sensing_info.speed))
            print("현재 차량 각도: {}".format(sensing_info.moving_angle))
            print("현재 차량 중심에서의 거리: {}".format(sensing_info.to_middle))
            print("세팅 값: set_steering = ", set_steering, "/ set_throttle = ", set_throttle)
            print("[MyCar] track_forward_obstacles: {}".format(sensing_info.track_forward_obstacles))
            print("[MyCar] distance_to_way_points: {}".format(sensing_info.distance_to_way_points))
            print("맵 진행률: {}".format(sensing_info.lap_progress))
            print("---------------------------------------------------------")
        self._prevToMiddle = sensing_info.to_middle
        self._prevBrake = set_brake
        self._prevSteering = set_steering
        self._prevThrottle = set_throttle
        # if sensing_info.speed > 40 and set_steering > 0 and
        self._count += 1
        if self._count == 5:
            self._count = 0



        car_controls.brake = set_brake
        car_controls.throttle = set_throttle
        car_controls.steering = set_steering

        if self.is_debug :#and self._count == 0:
            print("###############", sensing_info.lap_progress, is_accident, self._position)
            print("angleNum=", angle_num, ", refAngle", ref_angle, ", movingAngle=", sensing_info.moving_angle)
            print("front=", angle_front, ", short=", angle_short, ", middle=", angle_middle, ",long=", angle_long,
                  ", end=", angle_end)
            print("break_angle=", brake_angle, ", clean_speed=",clean_speed)
            print("targetdist=", target_dist, ", to_middle=", sensing_info.to_middle, ", newMiddle=", self._newMiddle)
            print("first=", first_steering, ", second=", second_steering, ", middle_add=", middle_add, ", third=",
                  third_steering)
            print("Steer=",set_steering," ACC=",set_throttle," BR=",set_brake, "BR_SPEED=",self._brakeSpeed)
            print("=========================================================")
            print("[MyCar] to middle: {}".format(sensing_info.to_middle))

            print("[MyCar] collided: {}".format(sensing_info.collided))
            print("[MyCar] car speed: {} km/h".format(sensing_info.speed))

            print("[MyCar] is moving forward: {}".format(sensing_info.moving_forward))
            print("[MyCar] moving angle: {}".format(sensing_info.moving_angle))
            print("[MyCar] lap_progress: {}".format(sensing_info.lap_progress))

            print("[MyCar] track_forward_angles: {}".format(sensing_info.track_forward_angles))
            print("[MyCar] track_forward_obstacles: {}".format(sensing_info.track_forward_obstacles))
            print("[MyCar] opponent_cars_info: {}".format(sensing_info.opponent_cars_info))
            print("[MyCar] distance_to_way_points: {}".format(sensing_info.distance_to_way_points))
            print("=========================================================")

        ###########################################################################

        # Moving straight forward
        # if self.half_road_limit / 2 < abs(sensing_info.to_middle):
        # car_controls.steering = -0.01

        # car_controls.throttle = 1
        # car_controls.brake = 0

        # if self.is_debug:
        # print("[MyCar] steering:{}, throttle:{}, brake:{}" \
        # .format(car_controls.steering, car_controls.throttle, car_controls.brake))

        #
        # Editing area ends
        # ==========================================================#
        return car_controls


    # ============================
    # If you have NOT changed the <settings.json> file
    # ===> player_name = ""
    #
    # If you changed the <settings.json> file
    # ===> player_name = "My car name" (specified in the json file)  ex) Car1
    # ============================
    def set_player_name(self):
        player_name = ""
        return player_name


if __name__ == '__main__':
    print("[MyCar] Start Bot!")
    client = DrivingClient()
    return_code = client.run()
    print("[MyCar] End Bot!")

    exit(return_code)
