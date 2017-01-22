# coding=utf-8
# Author: Yanda Li
# E-mail: 15810271029@163.com
# Time created: 2017/1/22

from Car import Car
from CarGenerator import CarGenerator
from Map import Map
import random

if __name__ == "__main__":
    time_t = 0
    mmap = Map('./map_scheme_test')
    print mmap.get_L()
    print mmap.get_B()
    print mmap.get_length()

    car_generator = CarGenerator(mmap, 10)  # 每秒10辆车

    car_list = mmap.avi()
    random.shuffle(car_list)

    while (time_t < 1000):
        print("Current Cycle: %d" %(car_generator.update_count))

        for a_car in car_list:
            a_car.refresh_speed()
            a_car.refresh_pos()

        car_generator.update()

        car_generator.print_toll_booths_waiting_queue()
        mmap.show_map()

        time_t += 1