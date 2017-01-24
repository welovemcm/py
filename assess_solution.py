# coding=utf-8
# Author: Kai WEN
# E-mail: wenkai123111 # 126.com
# Time created: 1/24/2017

import pickle
import math
import os
# 用于对模拟方案的效果进行评估

def _mean(lst):
    return float(sum(lst)) / max(len(lst), 1)

def _std_sample(lst):
    if len(lst) == 0:
        raise Exception('empty lst!')
    if len(lst) == 1:
        return 0.0
    ave = _mean(lst)
    var = [1.0 * (lst[i]-ave) * (lst[i]-ave) for i in range(len(lst))]
    ss = sum(var)
    std = math.sqrt(float(ss) / (len(var) - 1))
    return std

map_size = {''}

def get_map_size(dump_file_name):
    if dump_file_name.startswith('l2r_1ci1dao'):
        return 548
    if dump_file_name.startswith('l2r_1ci2dao'):
        return 596
    if dump_file_name.startswith('lr2m_1ci1dao'):
        return 552
    if dump_file_name.startswith('lr2m_1ci2dao'):
        return 596
    if dump_file_name.startswith('lr2m_1ci1dao_short'):
        return 274
    if dump_file_name.startswith('lr2m_1ci2dao_short'):
        return 298
    if dump_file_name.startswith('r2l_1ci1dao'):
        return 548
    if dump_file_name.startswith('r2l_1ci2dao'):
        return 596
    raise Exception('unknown map name!')



def assess_one_solution(file_name, path, flow_level):  # 按照产生的经济效益（对公路管理局的）和社会效益
    with open(path + file_name, 'r') as f:
        exp_results = pickle.load(f)
    for result in exp_results:
        if result['flow'] == flow_level:
            many_exps = result['result']
    exit_car_cnt_ind = 2
    total_exit_time_ind = 3
    crash_cnt_ind = 1
    q_traffics = [exp[exit_car_cnt_ind] for exp in many_exps]
    total_exit_times = [exp[total_exit_time_ind] for exp in many_exps]
    crashes = [exp[crash_cnt_ind] for exp in many_exps]
    q_traffic = _mean(q_traffics)
    total_exit_time = _mean(total_exit_times)
    crash_cnt = _mean(crashes)
    # 假设设计年限为15年
    # 平均每米费用为1万美元，每平方米费用1000美元，使用15年，平均每一千秒 1000/365/24/3600 * 1000
    benifit = 10.5 * q_traffic - 13.54 * total_exit_time / 3600 - 0.001 * crash_cnt * 3144 - 0.0317 * get_map_size(file_name)
    return benifit


def assess_path():
    path = 'exp/'
    f_names = []
    for (dirpath, dirnames, filenames) in os.walk(path):
        f_names.extend(filenames)
        break
    results = []
    for name in f_names:
        results.append((name, assess_one_solution(name, path, 0.8)))
        print (name, assess_one_solution(name, path, 0.8))
    srted = sorted(results, key=lambda x:x[1])
    print srted

if __name__ == '__main__':
    assess_path()





