# coding=utf-8
# Author: Kai WEN
# E-mail: wenkai123111 # 126.com
# Time created: 1/23/2017




import matplotlib.pyplot as plt
import math
import pickle


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

# plot flow against ave. wait time
def flow_against_y_statics(exp_result, y_column_index):
    flows = [0.1 * i for i in range(1, 21)]
    flows.insert(0, 0.01)
    assert len(flows) == len(exp_result)
    x_flows = flows
    y_mean = []
    y_std = []
    for i in range(len(flows)):
        this_result = exp_result[i]
        all_ys_in_a_flow = []
        for sample in this_result:
            all_ys_in_a_flow.append(sample[y_column_index])
        y_mean.append(_mean(all_ys_in_a_flow))
        y_std.append(_std_sample(all_ys_in_a_flow))
    return {'flow': x_flows, 'y_mean': y_mean, 'y_std': y_std}


def plot_flow_against_y(flow_statics, y_axis_label, file_name='pics/fig.pdf'):
    fig, ax = plt.subplots()
    ax.errorbar(flow_statics['flow'], flow_statics['y_mean'], flow_statics['y_std'])
    ax.set_xlabel('traffic flow (cars per second)')
    ax.set_ylabel(y_axis_label)
    plt.savefig(file_name)

    # plt.show()


def plot_dump_file(file_name):
    with open(file_name, 'rb') as f:
        exp_results = pickle.load(f)
    statics = flow_against_y_statics(exp_results, 1)
    tp_fname = 'pics/' + file_name + '_'
    plot_flow_against_y(statics, 'crash index', tp_fname + 'crash_index' + '.eps')
    statics = flow_against_y_statics(exp_results, 2)
    plot_flow_against_y(statics, 'total exit cars', tp_fname + 'total_exit_cars.eps')
    statics = flow_against_y_statics(exp_results, 4)
    plot_flow_against_y(statics, 'average time spent (second)', tp_fname + 'average_time_spent.eps')


if __name__ == '__main__':
    plot_dump_file('exp_wk_1ci2dao_center_AUTOCAR.dump')

