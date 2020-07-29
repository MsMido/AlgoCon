import DrivingInterface.drive_controller

from v1.DrivingInterface.drive_controller import DrivingController

class DrivingClient(DrivingController):
    import math
    def __init__(self):
        # =========================================================== #
        #  Area for member variables =============================== #
        # =========================================================== #
        # Editing area starts from here
        #

        self.is_debug = False

        #
        # Editing area ends
        # ==========================================================#
        super().__init__()

    def control_driving(self, car_controls, sensing_info):

        # =========================================================== #
        # Area for writing code about driving rule ================= #
        # =========================================================== #
        # Editing area starts from here
        #

        if self.is_debug:
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



        set_brake: float = 0.0
        set_throttle : float = 1
        set_steering : float = 0.0
        angle_num = (int)(sensing_info.speed/100)
        ref_angle = sensing_info.track_forward_angles[angle_num]
        middle_add  = (sensing_info.to_middle / 70) * -1
        set_steering = (ref_angle - sensing_info.moving_angle) / (220 - sensing_info.speed)
        set_steering += middle_add
        print(sensing_info.track_forward_angles)
        print(sensing_info.moving_angle)
        if(sensing_info.track_forward_angles[9] > 100 and sensing_info.speed > 60) :
            set_throttle = -1
            set_brake = 1



#        if len(sensing_info.track_forward_angles)>0 :
#           fwd_obstacle = sensing_info.track_forward_angles[0]
#            avoid_width : float = 2.7
#            diff : float = fwd_obstacle.to_middle - sensing_info.to_middle
#            if(abs(diff) < avoid_width) :
#                ref_angle = abs(math.atan(diff - avoid_width) / fwd_obstacle.dist) * 57.29579



        # Moving straight forward
        car_controls.steering = set_steering  #-1 ~ 1
        car_controls.throttle = set_throttle #-1 ~ 1
        car_controls.brake = set_brake # 0 ~ 1

        if self.is_debug:
            print("[MyCar] steering:{}, throttle:{}, brake:{}"\
                  .format(car_controls.steering, car_controls.throttle, car_controls.brake))

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
