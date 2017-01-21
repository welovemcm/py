# coding=utf-8
# Author: Kai WEN
# E-mail: wenkai123111 # 126.com
# Time created: 1/21/2017

import Queue
import random
import math
import Car_mock as car_cls

g_update_interval = 0.1
# generate cars for map to use

# 模型假设
# 司机在选择收费站时会考虑当前排队的长度，总是选择排队最短收费站
# 如果都空闲，就选择最近的收费站

# 假设 每个收费站对应一个道路

class CarGenerator:
    def __init__(self, map, incoming_traffic_flow):
        self.map = map
        self.update_interval = g_update_interval   # 每次调用update，系统时间过去0.1s
        self.update_count = 0  # 到目前为止调用了多少次更新
        self.toll_booths = self.__init_toll_baths()
        self.incoming_traffic_flow = incoming_traffic_flow  # 在fan_out_start_point进入的车辆数目

        # 初始化概率表
        self.max_probability_lst_len = 100
        # 累积一下
        self.probability_lst = [self.__vehicle_flow_probability_function(i) for i in range(self.max_probability_lst_len)]
        for i in range(1, self.max_probability_lst_len):
            self.probability_lst[i] += self.probability_lst[i - 1]

    def __init_toll_baths(self):
        return [TollBooth for i in range(10)]


    def __vehicle_flow_probability_function(self, n_incoming_cars):
        lam = self.incoming_traffic_flow / self.update_interval
        exp_lam = math.exp(-1.0 * lam)
        if n_incoming_cars == 0:
            return exp_lam
        return pow(lam, n_incoming_cars) / math.factorial(n_incoming_cars)


    def __determine_k(self, prob):
        for i in range(self.max_probability_lst_len):
            if prob < self.probability_lst[i]:
                return i - 1


    def __update_constant_vehicle_flow(self):
        # 系统更新到下一个时间点
        # 结果：对map进行读写，将车辆放出收费站，放入map的第0行
        self.update_count += 1


        # 第一步 在 fan_out_start_point 生成车流，其车流量为 incoming_traffic_flow
        # 可以是每秒钟固定有 incoming_traffic_flow 辆车
        n_this_time_interval_incoming_cars = self.calc_this_time_interval_coming_cars()
        cars = [car_cls.Car() for i in range(n_this_time_interval_incoming_cars)]

        # 第二步，在收费站之间分配车辆
        self.dispatch_cars_between_toll_booths_in_one_update_interval(cars)

        # 第三步，更新每个收费站的状态
        for toll_bath in self.toll_booths:
            toll_bath.update()



    def calc_this_time_interval_coming_cars(self):  # 计算这一时间段到达车辆的数目
        rnd_prob = random.random()  # [0.0, 1.0)
        n_this_interval_incoming_cars = self.__determine_k(rnd_prob)
        return n_this_interval_incoming_cars

    def dispatch_cars_between_toll_booths_in_one_update_interval(self, cars):
        # 每次取等待队列中在等待车辆最少的收费站
        for car in cars:
            waiting_cars_cnt_lst = [toll_booth.get_waiting_cars_cnt() for toll_booth in self.toll_booths]
            min_ind = _get_min_index(waiting_cars_cnt_lst)
            self.toll_booths[min_ind].add_car(car)


# class TollBooth:  # 收费站的基类
#     def __init__(self, process_time):
#         self.wait_queue = Queue.Queue()
#     def process(self):


# 收费站还包括一个放行规则
# 先写最简单的，处理完之后直接放行

class TollBooth:  # 由人控制的收费站
    def __init__(self, map, location, type):
        self.wait_queue = []
        self.update_count = 0
        self.car_in_process = None
        self.current_car_remaining_process_time = None
        self.solid_car_process_time = 0
        self.map = map
        self.update_interval = g_update_interval
        self.location = location  # 所处道路的编号
        self.type = type  # 收费站的类型，有三种

    # def car_in(self, car):
    #     if len(self.wait_queue) < 1:  # 等待队列中没有车

    def calc_this_car_process_time(self):  # 应对以后需要随机处理时间的情况
        return self.solid_car_process_time

    def get_waiting_cars_cnt(self):  # 返回等待队列中的车数 + 当前收费站正在处理的车数
        if self.car_in_process:
            return len(self.wait_queue) + 1
        else:
            return len(self.wait_queue)

    def add_car(self, car):
        if self.car_in_process:  # 当前有车正在处理
            self.wait_queue.append(car)
        else:  # 当前没有车
            if len(self.wait_queue) == 0:
                self.car_in_process = car
                self.current_car_remaining_process_time = self.calc_this_car_process_time()
            else:
                self.wait_queue.append(car)

    def process(self):
        pass

    def update(self):
        self.update_count += 1

        # 首先检查当前是否有车辆在处理
        if self.car_in_process:
            self.current_car_remaining_process_time -= self.update_interval
            if self.current_car_remaining_process_time <= 0:  # 当前车辆已经处理完了，需要决定是否放行，TODO  要检查相邻收费站的情况，有同时放行车辆是否要延后其中某一辆
                if self.map.have_car(self.location, 0):  # 如果要放入的格子里有车，就不能放行
                    self.current_car_remaining_process_time = self.update_interval  # 放入下次update中继续检查
                else:  # 要放入的格子里没有车
                    self.map.put_car(self.location, 0, self.car_in_process)
                    self.car_in_process = None  # 清空当前处理的car
                    # 放进来新的car 到收费站
                    if len(self.wait_queue) > 0:  # 如果当前有车正在等待
                        self.car_in_process = self.wait_queue.pop(0)
                        self.current_car_remaining_process_time = self.calc_this_car_process_time()
                    else: # 当前没有车正在等待
                        pass # 什么也不做
        else:  # 如果当前没有处理车辆
            if len(self.wait_queue) > 0:  # 如果有车在等待了，取一辆车进行处理
                self.car_in_process = self.wait_queue.pop(0)
                self.current_car_remaining_process_time = self.calc_this_car_process_time()
            else:  # 没有车
                pass


def _get_min_index(lst):
    min_val = min(lst)
    for i in range(len(lst)):
        if lst[i] == min_val:
            return i





if __name__ == '__main__':

    pass
