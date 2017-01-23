# coding=utf-8
# Author: Yanda Li
# E-mail: 15810271029@163.com
# Time created: 2017/1/22

from Car import Car
from CarGenerator import CarGenerator
from Map import Map
import random
import pickle
from multiprocessing.dummy import Pool

def one_run(traffic_flow):
    out = []
    case = 0
    while (case < 10):
        debug = False
        time_t = 0
        mmap = Map('./map_scheme_test_left_to_right')
        if (debug):
            print mmap.get_L()
            print mmap.get_B()
            print mmap.get_length()

        car_generator = CarGenerator(mmap, traffic_flow)  # 每秒10辆车

        car_list = mmap.avi()
        random.shuffle(car_list)

        while (time_t < 1000):
            if (debug):
                print("Current Cycle: %d" % (car_generator.update_count))

            for a_car in car_list:
                a_car.refresh_speed()
                a_car.refresh_pos()

            car_generator.update()

            if (debug):
                car_generator.print_toll_booths_waiting_queue()
                mmap.show_map()

            time_t += 1

        ave_spend_time = 1.0 * mmap.total_exit_time / mmap.exit_car_cnt
        if (debug):
            print ("Total crash cnt: %d\nTotal exit cars: %d\nTotal spend time: %d\nAverage spend time: %f" % (
            mmap.crash_cnt, mmap.exit_car_cnt, mmap.total_exit_time, ave_spend_time))
        else:
            print ("flow:%f\t%d\t%d\t%d\t%d\t%f\t%d" % (traffic_flow,
            case, mmap.crash_cnt, mmap.exit_car_cnt, mmap.total_exit_time, ave_spend_time,
            car_generator.sum_toll_booths_waiting_cars_cnt()))
        out.append((case, mmap.crash_cnt, mmap.exit_car_cnt, mmap.total_exit_time, ave_spend_time,
            car_generator.sum_toll_booths_waiting_cars_cnt()))

        case += 1
    return {'flow': traffic_flow, 'result': out}


def vary_traffic_flow():
    flows = [0.1 * i for i in range(1, 21)]
    flows.insert(0, 0.01)
    results = []
    for flow in flows:
        print "===== flow:", flow
        results.append(one_run(flow))
    with open('exp_left_to_right.dump', 'wb') as f:
        pickle.dump(results, f)

def vary_traffic_flow_multi():
    flows = [0.1 * i for i in range(1, 21)]
    flows.insert(0, 0.01)
    # results = []
    pool = Pool(7)
    results = pool.map(one_run, flows)
    with open('exp_left_to_right_ver2.dump', 'wb') as f:
        pickle.dump(results, f)
    pool.close()
    pool.join()



if __name__ == "__main__":
    vary_traffic_flow_multi()
