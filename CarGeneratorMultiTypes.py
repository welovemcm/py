# coding=utf-8
# Author: Kai WEN
# E-mail: wenkai123111 # 126.com
# Time created: 1/21/2017

import Queue
import random
import math
import Map
import Car as car_cls


g_update_interval = 1  # 默认每次更新过1s
etc_car_out_speed = 3 # etc车辆驶出收费站的速度是 3格每秒
# generate cars for map to use

# 模型假设
# 司机在选择收费站时会考虑当前排队的长度，总是选择排队最短收费站
# 如果都空闲，就选择最近的收费站

# 假设 每个收费站对应一个道路

# TODO 升级，
class CarGeneratorMultiTypes:
    def __init__(self, map, incoming_traffic_flow, tollbooths, car_tollbooth_proportion_accum_list, car_tollbooth_types, car_is_auto=False):
        self.map = map
        self.update_interval = g_update_interval   # 每次调用update，系统时间过去0.1s
        self.update_count = 0  # 到目前为止调用了多少次更新
        self.toll_booths = []
        self.etc_car_fit_tollbooths = []
        self.atc_car_fit_tollbooths = []
        self.mtc_car_fit_tollbooths = []
        self.set_toll_booths(tollbooths)
        self.incoming_traffic_flow = incoming_traffic_flow  # 在fan_out_start_point进入的车辆数目
        self.car_tollbooth_proportion_list = car_tollbooth_proportion_accum_list
        self.car_tollbooth_types = car_tollbooth_types
        self.cur_generated_car_id = 0
        self.new_cars_cnt = 0
        self.car_is_auto = car_is_auto
        # 初始化概率表
        self.max_probability_lst_len = 10
        self.probability_lst = [self.__vehicle_flow_probability_function(i) for i in range(self.max_probability_lst_len)]
        self.debug = False
        for i in range(1, self.max_probability_lst_len):
            self.probability_lst[i] += self.probability_lst[i - 1]

    @classmethod
    def init_with_default_paras(cls, map, incoming_traffic_flow, car_is_auto=False):
        car_tollbooth_proportion_accum_list = [0.4, 0.4 + 0.55, 0.4 + 0.55 + 0.05]  # 最后一个必须是1
        car_tollbooth_types = ['ETC', "ATC", 'MTC']
        tollbooth_types = ['ETC', 'ETC', 'ATC', 'ATC', 'ATC', 'ATC', 'ATC', 'MTC']
        tollbooths = []
        for i in range(8):
            tollbooth = TollBooth(map, i, tollbooth_types[i])
            tollbooths.append(tollbooth)
        return CarGeneratorMultiTypes(map, incoming_traffic_flow, tollbooths, car_tollbooth_proportion_accum_list, car_tollbooth_types, car_is_auto=car_is_auto)

    def __this_car_id(self):
        self.cur_generated_car_id += 1
        return self.cur_generated_car_id

    def set_toll_booths(self, tollbooths):  # 设置不同类型的收费站
        assert len(tollbooths) == self.map.get_B()
        self.toll_booths = tollbooths
        self.etc_car_fit_tollbooths = [tollbooth for tollbooth in self.toll_booths if tollbooth.type == 'ETC']
        self.mtc_car_fit_tollbooths = [tollbooth for tollbooth in self.toll_booths if tollbooth.type == 'MTC']
        self.atc_car_fit_tollbooths = [tollbooth for tollbooth in self.toll_booths if tollbooth.type == 'ATC']
        assert sum([len(l) for l in [self.etc_car_fit_tollbooths, self.mtc_car_fit_tollbooths, self.atc_car_fit_tollbooths]]) == len(self.toll_booths)
        self.mtc_car_fit_tollbooths.extend(self.atc_car_fit_tollbooths)
        self.etc_car_fit_tollbooths.extend(self.mtc_car_fit_tollbooths)


    # def set_car_proportions(self, car_proportion_dict):
    #     self.car_tollbooth_proportion_list = car_proportion_dict
    #     self.car_tollbooth_types = ['ETC', 'ATC', 'MTC']

    def rnd_car_tollbooth_type(self):  # TODO 初始化时需要设置车辆比例
        rnd = random.random()
        for i in range(len(self.car_tollbooth_proportion_list)):
            if rnd <= self.car_tollbooth_proportion_list[i]:
                return self.car_tollbooth_types[i]
        raise Exception('unmatched prob')

    def print_toll_booths_waiting_queue(self):
        print [tb.get_waiting_cars_cnt() for tb in self.toll_booths]

    def sum_toll_booths_waiting_cars_cnt(self):
        return sum([tb.get_waiting_cars_cnt() for tb in self.toll_booths])

    def __init_toll_baths(self):  # 还要支持不同收费站比例的变化， 默认全是自动收费站
        return [TollBooth(self.map, i, 'ATC') for i in range(self.map.get_B())]


    def __vehicle_flow_probability_function(self, n_incoming_cars):
        lam = self.incoming_traffic_flow * self.update_interval
        exp_lam = math.exp(-1.0 * lam)
        if n_incoming_cars == 0:
            return exp_lam
        return 1.0 * pow(lam, n_incoming_cars) / math.factorial(n_incoming_cars) * exp_lam


    def __determine_k(self, prob):
        for i in range(self.max_probability_lst_len):
            if prob < self.probability_lst[i]:
                return i
        return self.max_probability_lst_len

    def update(self):
        self.__update_constant_vehicle_flow()


    def __update_constant_vehicle_flow(self):
        # 系统更新到下一个时间点
        # 结果：对map进行读写，将车辆放出收费站，放入map的第0行
        self.update_count += 1


        # 第一步 在 fan_out_start_point 生成车流，其车流量为 incoming_traffic_flow
        # 可以是每秒钟固定有 incoming_traffic_flow 辆车
        n_this_time_interval_incoming_cars = self.calc_this_time_interval_coming_cars()
        self.new_cars_cnt += n_this_time_interval_incoming_cars
        if (self.debug):
            print "Cargenerator: cycle ", self.update_count, " new cars this time: ", n_this_time_interval_incoming_cars, "new cars cnt: ", self.new_cars_cnt
        cars = [car_cls.Car(0, 10, 0, 0, self.map, self.car_is_auto, self.__this_car_id()) for i in range(n_this_time_interval_incoming_cars)]
        for car in cars:
            car.tollbooth_type = self.rnd_car_tollbooth_type()
            # print car.tollbooth_type

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
        # 每次取期望等待时间最短
        for car in cars:
            if car.tollbooth_type == 'ATC':
                toll_booths_fit_car = self.atc_car_fit_tollbooths
            elif car.tollbooth_type == 'MTC':
                toll_booths_fit_car = self.mtc_car_fit_tollbooths
            elif car.tollbooth_type == 'ETC':
                toll_booths_fit_car = self.etc_car_fit_tollbooths
            else:
                raise Exception('unknown car type')
            waiting_cars_cnt_lst = [toll_booth.get_approx_expected_waiting_time(car) for toll_booth in toll_booths_fit_car]
            min_ind_lst = _get_min_indexes(waiting_cars_cnt_lst)
            min_ind = min_ind_lst[random.randint(0, len(min_ind_lst) - 1)]  # 随机选择一个
            toll_booths_fit_car[min_ind].add_car_new(car)


# class TollBooth:  # 收费站的基类
#     def __init__(self, process_time):
#         self.wait_queue = Queue.Queue()
#     def process(self):


# 收费站还包括一个放行规则
# 先写最简单的，处理完之后直接放行

class TollBooth:  # 由人控制的收费站
    def __init__(self, map, location, tb_type):
        self.wait_queue = []
        self.in_road_queue = []
        self.in_road_queue_remaining_time = []
        self.update_count = 0
        self.car_in_process = None
        self.current_car_remaining_process_time = None
        self.solid_car_process_time = 1
        self.map = map
        self.update_interval = g_update_interval
        self.location = location  # 所处道路的编号
        self.type = tb_type  # 收费站的类型，有三种，类型会影响车辆放行的时间，此外还会影响放行车辆时车辆的速度
        # MTC: conventional (human-staffed) tollbooths,
        # ATC: exact-change (automated) tollbooths, and
        # ETC: electronic toll collection booths
        # 对于有人的，车辆肯定会停下来
        # 三种类型：
        # 对于exact-change tollbooths?


        self.in_distance = 50  # 假设是要先行驶100格才能到收费站
        self.mean_service_time = 20  # 秒
        self.service_time_std = 10  # 秒
        if self.type == 'MTC':
            self.mean_service_time = 5
            self.service_time_std = 1
        elif self.type == 'ATC':
            self.mean_service_time = 1
            self.service_time_std = 0.2
        elif self.type == 'ETC':
            self.mean_service_time = 0
            self.service_time_std = 0
        else:
            raise Exception('unknown tollbooth type ')

    # def car_in(self, car):
    #     if len(self.wait_queue) < 1:  # 等待队列中没有车

    def calc_this_car_process_time(self):  # 应对以后需要随机处理时间的情况, 包括两部分，减速时间和处理时间
        car = self.car_in_process
        if self.type == 'ETC':
            return 0.0
        elif self.type == 'MTC' or self.type == 'ATC':
            t_in = 2.0 * self.in_distance / car.get_speed_y()
            t_service = random.normalvariate(self.mean_service_time, self.service_time_std)
            # return t_in + t_service
            return t_service  # t_in 单独考虑
        raise Exception('unknown toll booth type')

    def get_waiting_cars_cnt(self):  # 返回等待队列中的车数 + 当前收费站正在处理的车数
        if self.car_in_process:
            return len(self.wait_queue) + 1 +len(self.in_road_queue)
        else:
            return len(self.wait_queue) + len(self.in_road_queue)

    def get_approx_expected_waiting_time(self, car):  # 并不是完全精确的等待时间.估算方式：max(当前等待车辆数* 平均每车处理时间 - 驶到收费站时间,0) + 收费站服务时间. # 确保ETC车辆总是选择ETC
        return max(self.get_waiting_cars_cnt() * self.mean_service_time - self.calc_car_in_distance_time(car), 0) + self.mean_service_time

    def calc_car_in_distance_time(self, car):
        if self.type == 'MTC' or self.type == 'ATC':
            return 2.0 * self.in_distance / car.get_speed_y()
        elif self.type == 'ETC':
            return 1.0 * self.in_distance / car.get_speed_y()
        else:
            raise Exception('unknown tollbooth type')



    def add_car_new(self, car):
        self.add_car_to_in_road_queue(car)



    def add_car_to_in_road_queue(self, car):
        self.in_road_queue.append(car)
        if self.type == 'MTC' or self.type == 'ATC':
            self.in_road_queue_remaining_time.append(2.0 * self.in_distance / car.get_speed_y())
        elif self.type == 'ETC':
            self.in_road_queue_remaining_time.append(1.0 * self.in_distance / car.get_speed_y())
        else:
            raise Exception('unknown toll booth type!')

    def add_car_to_process_queue(self, car):  # 收费站收费队列
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

        # 检查是否有车进入了等待队列
        assert len(self.in_road_queue_remaining_time) == len(self.in_road_queue)
        for i in range(len(self.in_road_queue_remaining_time)):
            self.in_road_queue_remaining_time[i] -= self.update_interval
        while (len(self.in_road_queue_remaining_time) > 0) and (self.in_road_queue_remaining_time[0] <= 0):
            self.wait_queue.append(self.in_road_queue.pop(0))
            self.in_road_queue_remaining_time.pop(0)

        # 首先检查当前是否有车辆在处理
        if self.car_in_process:
            self.current_car_remaining_process_time -= self.update_interval
            if self.current_car_remaining_process_time <= 0:  # 当前车辆已经处理完了，需要决定是否放行，TODO  要检查相邻收费站的情况，有同时放行车辆是否要延后其中某一辆
                if self.map.have_car(self.location, 0):  # 如果要放入的格子里有车，就不能放行
                    # print "have car in map x,0"
                    self.current_car_remaining_process_time = self.update_interval  # 放入下次update中继续检查
                else:  # 要放入的格子里没有车
                    if self.type == 'MTC' or self.type == 'ATC':
                        self.car_in_process.set_speed_y(0)  # 非自动收费的要减速到0
                    elif self.type == 'ETC':
                        self.car_in_process.set_speed_y(etc_car_out_speed)  # ETC 车辆驶出收费站的速度
                    self.car_in_process.set_pos_x(self.location)
                    self.car_in_process.set_pos_y(0)
                    self.map.put_car(self.location, 0, self.car_in_process)
                    # print ("put %d" %(self.location))
                    self.car_in_process = None  # 清空当前处理的car
                    # 放进来新的car 到收费站
                    if len(self.wait_queue) > 0:  # 如果当前有车正在等待
                        self.car_in_process = self.wait_queue.pop(0)
                        self.current_car_remaining_process_time = self.calc_this_car_process_time()
                    else:  # 当前没有车正在等待
                        pass  # 什么也不做
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

def _get_min_indexes(lst):
    min_val = min(lst)
    out = []
    for i in range(len(lst)):
        if lst[i] == min_val:
            out.append(i)
    return out

def test_car_generator():
    map = Map.Map('./map_scheme_test_1')
    car_tollbooth_proportion_accum_list = [3.0/8, 7.5/8, 8/8]  # 最后一个必须是1
    car_tollbooth_types = ['ETC', "ATC", 'MTC']
    tollbooth_types = ['ETC', 'ATC', 'ATC', 'ATC', 'ATC', 'ATC', 'ATC', 'MTC']
    tollbooths = []
    for i in range(8):
        tollbooth = TollBooth(map, i, tollbooth_types[i])
        tollbooths.append(tollbooth)
    car_generator = CarGeneratorMultiTypes(map, 10, tollbooths, car_tollbooth_proportion_accum_list, car_tollbooth_types)  # 每秒10辆车
    for i in range(100):
        print("cur cycle: ", car_generator.update_count)
        car_generator.update()
        car_generator.print_toll_booths_waiting_queue()
        car_generator.map.show_map()





if __name__ == '__main__':
    test_car_generator()
    pass
