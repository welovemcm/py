# coding = utf-8
# Author: Yanda Li
# E-mail: 15810271029@163.com
# Time created: 2017/1/21

import random

DEC_SPEED_PRO = 0.2
CHANGE_LANE_PRO = 0.5
LANE_LENGTH = 1000

class Car:
    speed_x = None
    speed_y = None
    pos_x = None
    pos_y = None
    lane_map = None
    is_auto = None
    car_id = None

    def __init__(self, speed_x, speed_y, pos_x, pos_y, lane_map, is_auto, car_id):
        self.speed_x = speed_x
        self.speed_y = speed_y
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.lane_map = lane_map
        self.is_auto = is_auto
        self.car_id = car_id

    def get_speed_x(self):
        return self.speed_x

    def get_speed_y(self):
        return self.speed_y

    def get_pos_x(self):
        return self.pos_x

    def get_pos_y(self):
        return self.pos_y

    def get_is_auto(self):
        return self.is_auto

    def get_car_id(self):
        return self.car_id

    def gap_front(self):# 计算与前车距离
        gap = 0
        start = self.pos_y + 1
        end = min(self.pos_y + self.speed_y + 2, LANE_LENGTH)
        for i in range(start, end):
            if (self.lane_map.have_car(self.pos_x, i) == True or self.lane_map.is_road(self.pos_x, i) == False):
                gap = i - self.pos_y - 1
                break
            if (i == end - 1):
                gap = i - self.pos_y
        print("Car %d gap_front = %d" %(self.car_id, gap))
        return gap

    def gap_right(self):# 计算与右车道车距离
        gap_f = 0
        start_f = self.pos_y
        end_f = min(self.pos_y + self.speed_y + 3, LANE_LENGTH)
        for i in range(start_f, end_f):
            if (self.lane_map.have_car(self.pos_x + 1, i) == True or self.lane_map.is_road(self.pos_x + 1, i) == False):
                gap_f = i - self.pos_y - 1
                break
            if (i == end_f - 1):
                gap_f = i - self.pos_y
        gap_b = 0
        temp_b = self.pos_y
        temp_car = None
        while (temp_b >= 0):
            if (self.lane_map.have_car(self.pos_x + 1, temp_b) == True):
                gap_b = self.pos_y - temp_b - 1
                temp_car = self.lane_map.get_car()
        end_f


    def refresh_speed(self):
        if (self.is_auto == False):# 非自动驾驶
            # 行进步骤
            gap = gap_front()
            if (self.speed_y >= gap):# 速度大于等于间隔，减速至gap
                if (DEC_SPEED_PRO > random.random()):# 减速
                    self.speed_y = gap - 1
                else:# 不减速
                    self.speed_y = gap
            else:# 速度小于间隔
                if (DEC_SPEED_PRO < random.random()):# 加速
                    self.speed_y += 1
            # 换道步骤
            if (self.pos_x == 0):

        print("Car %d speed = %d, %d" %(self.car_id, self.speed_y, self.speed_x))
        return (speed_x, speed_y)

    def refresh_pos(self):
        self.pos_x += speed_x
        self.pos_y += speed_y
        print("Car %d pos = %d, %d" % (self.car_id, self.pos_y, self.pos_x))
        #if (self.pos_y > LANE_LENGTH):
            # 开出收费站

if __name__ == '__main__':
    pass