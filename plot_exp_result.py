# coding=utf-8
# Author: Kai WEN
# E-mail: wenkai123111 # 126.com
# Time created: 1/23/2017




import matplotlib.pyplot as plt
import matplotlib
import math
import pickle
import os
import re

# matplotlib.rc('font', serif='Times New Roman')


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
# def flow_against_y_statics(exp_result, y_column_index):
#     flows = [0.1 * i for i in range(1, 21)]
#     flows.insert(0, 0.01)
#     assert len(flows) == len(exp_result)
#     x_flows = flows
#     y_mean = []
#     y_std = []
#     for i in range(len(flows)):
#         this_result = exp_result[i]
#         all_ys_in_a_flow = []
#         for sample in this_result:
#             all_ys_in_a_flow.append(sample[y_column_index])
#         y_mean.append(_mean(all_ys_in_a_flow))
#         y_std.append(_std_sample(all_ys_in_a_flow))
#     return {'flow': x_flows, 'y_mean': y_mean, 'y_std': y_std}

def flow_against_y_statics_for_dict_file(exp_result, y_column_index):
    flows = []
    x_flows = flows
    y_mean = []
    y_std = []
    for result in exp_result:
        flows.append(result['flow'])
        all_ys_in_a_flow = []
        for sample in result['result']:
            all_ys_in_a_flow.append(sample[y_column_index])
        y_mean.append(_mean(all_ys_in_a_flow))
        y_std.append(_std_sample(all_ys_in_a_flow))
    return {'flow': x_flows, 'y_mean': y_mean, 'y_std': y_std}


def _divide_with_0(x, y):
    if y == 0:
        return 0.0
    return 1.0 * x / y


def flow_against_y_statics_for_dict_file_column1_divided_by_column2(exp_result, column1_ind, column2_ind):
    c1 = column1_ind
    c2 = column2_ind
    flows = []
    x_flows = flows
    # ys = []
    y_mean = []
    y_std = []
    for result in exp_result:
        flows.append(result['flow'])
        all_ys_in_a_flow = []
        for sample in result['result']:
            all_ys_in_a_flow.append(_divide_with_0(sample[c1], sample[c2]))
        y_mean.append(_mean(all_ys_in_a_flow))
        y_std.append(_std_sample(all_ys_in_a_flow))
    return {'flow': x_flows, 'y_mean': y_mean, 'y_std': y_std}



def plot_flow_against_y(flow_statics, y_axis_label, file_name='pics/fig.pdf'):
    fig, ax = plt.subplots()
    ax.errorbar(flow_statics['flow'], flow_statics['y_mean'], flow_statics['y_std'])
    ax.set_xlabel('traffic flow (cars per second)')
    ax.set_ylabel(y_axis_label)
    plt.tight_layout()
    plt.savefig(file_name)

    # plt.show()

def plot_flow_against_y1_y2(flow_statics1, flow_statics2, y_axis_label, file_name='pics/comparefig.pdf', legends=[]):
    fig, ax = plt.subplots()
    plotline1, caplines1, barlinecols1 = ax.errorbar(flow_statics1['flow'], flow_statics1['y_mean'],
                                                   flow_statics1['y_std'], color='b')
    plotline2, caplines2, barlinecols2 = ax.errorbar(flow_statics2['flow'], flow_statics2['y_mean'],
                                                   flow_statics2['y_std'], color='r')

    if len(legends) == 2:
        # plotline1.label = legends[0]
        # plotline2.label = legends[1]
        plt.legend(handles=[plotline1, plotline2], labels=legends, loc='lower right')
    ax.set_xlabel('traffic flow (cars per second)')
    ax.set_ylabel(y_axis_label)
    plt.tight_layout()
    plt.savefig(file_name)
    plt.close()

def plot_flow_against_ys(flow_statics, y_axis_label, file_name='pics/comparefig.pdf', legends=[]):
    fig, ax = plt.subplots()
    plotlines = []
    colors = ['b', 'r', 'g']
    for i in range(len(flow_statics)):
        fs = flow_statics[i]
        plotline, caplines, barlinecols = ax.errorbar(fs['flow'], fs['y_mean'],
                                                    fs['y_std'], color=colors[i])
        plotlines.append(plotline)

    if len(legends) == len(plotlines):
        # plotline1.label = legends[0]
        # plotline2.label = legends[1]
        plt.legend(handles=plotlines, labels=legends, loc='lower right')
    ax.set_xlabel('traffic flow (cars per second)')
    ax.set_ylabel(y_axis_label)
    plt.tight_layout()
    plt.savefig(file_name)
    plt.close()

def plot_flow_against_y1_y2_scale(flow_statics1, flow_statics2, y_axis_label, file_name='pics/comparefig.pdf',
                            legends=[]):
    fig, ax = plt.subplots()
    y1_scale = 1.0
    y2_scale = 2.0  # every 100 grids
    plotline1, caplines1, barlinecols1 = ax.errorbar(flow_statics1['flow'], flow_statics1['y_mean'],
                                                     flow_statics1['y_std'], color='b')
    plotline2, caplines2, barlinecols2 = ax.errorbar(flow_statics2['flow'], [y2_scale * val for val in flow_statics2['y_mean']],
                                                     [y2_scale * val for val in flow_statics2['y_std']], color='r')

    if len(legends) == 2:
        # plotline1.label = legends[0]
        # plotline2.label = legends[1]
        plt.legend(handles=[plotline1, plotline2], labels=legends, loc='lower right')
    ax.set_xlabel('traffic flow (cars per second)')
    ax.set_ylabel(y_axis_label)
    plt.tight_layout()
    plt.savefig(file_name)
    plt.close()



def plot_two_dump_files_in_one_fig(file_name1, file_name2, path, legends=[], compare_target=''):
    with open(path + file_name1, 'r') as f:
        exp_results1 = pickle.load(f)
    with open(path + file_name2, 'r') as f:
        exp_results2 = pickle.load(f)
    save_picture_fname = 'pics_two_in_one/' + compare_target +'_' + file_name1 + '_VS_' + file_name2 + '_'
    statics1 = flow_against_y_statics_for_dict_file(exp_results1, 1)
    statics2 = flow_against_y_statics_for_dict_file(exp_results2, 1)
    plot_flow_against_y1_y2(statics1, statics2, 'crash index',
                            file_name=save_picture_fname + 'crash_index' + '.png',
                            legends=legends)
    statics1 = flow_against_y_statics_for_dict_file(exp_results1, 2)
    statics2 = flow_against_y_statics_for_dict_file(exp_results2, 2)
    plot_flow_against_y1_y2(statics1, statics2, 'total exited cars',
                            file_name=save_picture_fname + 'total_exit_cars' + '.png',
                            legends=legends)
    statics1 = flow_against_y_statics_for_dict_file(exp_results1, 4)
    statics2 = flow_against_y_statics_for_dict_file(exp_results2, 4)
    plot_flow_against_y1_y2(statics1, statics2, 'average time spent (second)',
                            file_name=save_picture_fname + 'average_time_spent' + '.png',
                            legends=legends)
    statics1 = flow_against_y_statics_for_dict_file_column1_divided_by_column2(exp_results1, 1, 2)
    statics2 = flow_against_y_statics_for_dict_file_column1_divided_by_column2(exp_results2, 1, 2)
    plot_flow_against_y1_y2(statics1, statics2, 'average crash index per car',
                            file_name=save_picture_fname + 'average_crash_index' + '.png',
                            legends=legends)

def plot_multi_dump_files_in_one_fig(file_names, path, legends=[], compare_target=''):
    exp_results = []
    for fname in file_names:
        with open(path + fname, 'r') as f:
            exp_results .append(pickle.load(f))
    save_picture_fname = 'pics_two_in_one/3_' + compare_target +'_' + file_names[1] + '_VS_' + file_names[2] + '_'
    statics = [flow_against_y_statics_for_dict_file(exp_result, 1) for exp_result in exp_results]
    plot_flow_against_ys(statics, 'crash index',
                            file_name=save_picture_fname + 'crash_index' + '.png',
                            legends=legends)
    statics = [flow_against_y_statics_for_dict_file(exp_result, 2) for exp_result in exp_results]
    plot_flow_against_ys(statics, 'total exited cars',
                            file_name=save_picture_fname + 'total_exit_cars' + '.png',
                            legends=legends)
    statics = [flow_against_y_statics_for_dict_file(exp_result, 4) for exp_result in exp_results]
    plot_flow_against_ys(statics, 'average time spent (second)',
                            file_name=save_picture_fname + 'average_time_spent' + '.png',
                            legends=legends)
    statics = [flow_against_y_statics_for_dict_file_column1_divided_by_column2(exp_result, 1, 2) for exp_result in exp_results]
    plot_flow_against_ys(statics, 'average crash index per car',
                            file_name=save_picture_fname + 'average_crash_index' + '.png',
                            legends=legends)

def plot_two_dump_files_in_one_fig_scale(file_name1, file_name2, path, legends=[], compare_target=''):
    with open(path + file_name1, 'r') as f:
        exp_results1 = pickle.load(f)
    with open(path + file_name2, 'r') as f:
        exp_results2 = pickle.load(f)
    save_picture_fname = 'pics_two_in_one/' + compare_target +'_' + file_name1 + '_VS_' + file_name2 + '_'
    statics1 = flow_against_y_statics_for_dict_file(exp_results1, 1)
    statics2 = flow_against_y_statics_for_dict_file(exp_results2, 1)
    plot_flow_against_y1_y2_scale(statics1, statics2, 'crash index per 100 grids',
                            file_name=save_picture_fname + 'crash_index' + '.png',
                            legends=legends)
    statics1 = flow_against_y_statics_for_dict_file(exp_results1, 2)
    statics2 = flow_against_y_statics_for_dict_file(exp_results2, 2)
    plot_flow_against_y1_y2(statics1, statics2, 'total exited cars',
                            file_name=save_picture_fname + 'total_exit_cars' + '.png',
                            legends=legends)
    statics1 = flow_against_y_statics_for_dict_file(exp_results1, 4)
    statics2 = flow_against_y_statics_for_dict_file(exp_results2, 4)
    plot_flow_against_y1_y2_scale(statics1, statics2, 'average time spent per 100 grids (second)',
                            file_name=save_picture_fname + 'average_time_spent' + '.png',
                            legends=legends)
    statics1 = flow_against_y_statics_for_dict_file_column1_divided_by_column2(exp_results1, 1, 2)
    statics2 = flow_against_y_statics_for_dict_file_column1_divided_by_column2(exp_results2, 1, 2)
    plot_flow_against_y1_y2_scale(statics1, statics2, 'average crash index per car per 100 grids',
                            file_name=save_picture_fname + 'average_crash_index' + '.png',
                            legends=legends)






def plot_dump_file(file_name, path):
    with open(path + file_name, 'r') as f:
        exp_results = pickle.load(f)
    save_picture_fname = 'pics/' + file_name + '_'
    statics = flow_against_y_statics_for_dict_file(exp_results, 1)
    plot_flow_against_y(statics, 'crash index', save_picture_fname + 'crash_index' + '.png')
    statics = flow_against_y_statics_for_dict_file(exp_results, 2)
    plot_flow_against_y(statics, 'total exited cars', save_picture_fname + 'total_exit_cars.png')
    statics = flow_against_y_statics_for_dict_file(exp_results, 4)
    plot_flow_against_y(statics, 'average time spent (second)', save_picture_fname + 'average_time_spent.png')
    statics = flow_against_y_statics_for_dict_file_column1_divided_by_column2(exp_results, 1, 2)
    plot_flow_against_y(statics, 'average crash index per car', save_picture_fname + 'average_crash_index.png')



def collect_statics():
    pass


pattern = re.compile('.*')
def plot_multi_files():
    path = 'exp/'
    f_names = []
    for (dirpath, dirnames, filenames) in os.walk(path):
        f_names.extend(filenames)
        break
    filtered_names = []
    for name in f_names:
        if pattern.search(name):
            filtered_names.append(name)
    for name in filtered_names:
        plot_dump_file(name, path)







base_line_file_name = 'lr2m_1ci2dao_m.dump'
dump_file_path = 'exp/'



if __name__ == '__main__':
    plot_dump_file('lr2m_1ci2dao_m.dump', 'exp/')
    # plot_multi_files()

    # # etc merge pattern
    # # plot_two_dump_files_in_one_fig('r2l_1ci1dao_barrier_a.dump', 'r2l_1ci1dao_mixed_tb_a.dump', dump_file_path, legends=['seperate ETC lanes, auto drive', 'mixed ETC lanes, auto drive'], compare_target='etcMergePattern')
    # plot_two_dump_files_in_one_fig('r2l_1ci1dao_barrier_m.dump', 'r2l_1ci1dao_mixed_tb_m.dump', dump_file_path,
    #                                legends=['seperate ETC lanes, human', 'mixed ETC lanes, human'],
    #                                compare_target='etcMergePattern')
    #
    # # size
    # plot_two_dump_files_in_one_fig('lr2m_1ci2dao_m.dump', 'lr2m_1ci1dao_m.dump', dump_file_path, legends=['two lanes per merge, human', 'one lanes per merge, human'], compare_target='mergePattern')
    # plot_two_dump_files_in_one_fig('lr2m_1ci2dao_a.dump', 'lr2m_1ci1dao_a.dump', dump_file_path,
    #                                      legends=['two lanes per merge, auto drive', 'one lanes per merge, auto drive'],
    #                                      compare_target='mergePattern')
    #
    # # tollbooth proportion
    # plot_two_dump_files_in_one_fig('lr2m_1ci2dao_m.dump', 'lr2m_1ci2dao_mixed_tb_m.dump', dump_file_path, legends=['all ATC, human', '2 ETCs, 5 ATCs, 1 MTC, human'], compare_target='tbprop')
    #
    #
    #
    # # ETC merge pattern
    # plot_two_dump_files_in_one_fig('lr2m_1ci2dao_mixed_tb_m.dump', 'r2l_1ci1dao_mixed_tb_m.dump', dump_file_path, legends=['all ATC, human, r2l', '2 ETCs, 5 ATCs, 1 MTC, human, r2l'], compare_target='tbprop')
    #
    # # auto drive
    # plot_two_dump_files_in_one_fig('lr2m_1ci2dao_m.dump', 'lr2m_1ci2dao_a.dump', dump_file_path, legends=['human', 'auto drive'], compare_target='auto_drive')
    #
    # # left_road_loc
    # plot_multi_dump_files_in_one_fig(['lr2m_1ci2dao_m.dump', 'r2l_1ci2dao_m.dump', 'l2r_1ci2dao_m.dump'], dump_file_path,
    #                                  legends=['center lanes', 'left lanes', 'right lanes'], compare_target='left_road_loc')


