import numpy as np
import pandas as pd
from tqdm import tqdm
import os

"""
通过统计在相同连通图内，每一告警前后出现的其他告警数量，来辅助先验信息的获取
"""

data_id = 1  # data_id = 2

topology_ids = [1, 2, 6, 7, 8, 10]

mat_shapes_phase2 = [24, 25, 15, 17, 17, 19, 20, 20, 22, 22]


def to_clusters(topology_data):
    """
    根据拓扑图划分连通图
    """
    clusters = []
    ii = list(range(topology_data.shape[0]))
    nu = 0
    for i in range(topology_data.shape[0]):
        if i not in ii:
            continue
        cluster = [i]
        ii.remove(i)
        run = True
        while run:
            run = False
            for j in ii:
                if topology_data[j, cluster].sum() > 0:
                    cluster.append(j)
                    ii.remove(j)
                    run = True
                    nu += 1
                    # print(nu)
        clusters.append(cluster)
    return clusters


def transform_cols(data, cols=None):
    """
    转换告警数据
    """
    if cols is None:
        cols = ['event', 'node', 'timestamp']
    if len(cols) != 3:
        raise ValueError("the length of cols must be 3")
    for col in cols:
        if col not in cols:
            raise ValueError("the values of cols is wrong: %s" % col)

    trans_data = data.iloc[:, 0:3]
    trans_data.columns = cols
    trans_data = trans_data.reindex(columns=['event', 'timestamp', 'node'])

    return trans_data


def get_cluster_data(X, cluster):
    tensor = X[X['node'].isin(cluster)]
    return tensor


def cal_front_alarm_times(i, j, tensor, tau_max=10):
    """
    查看告警 i 前告警 j 出现的次数
    """
    mask = (tensor['event'] == j)
    roll = (tensor['event'] == i)
    temp = roll.copy()
    for _ in range(tau_max):
        temp = np.roll(temp, -1)
        roll = (roll | temp)
    return np.sum(mask & roll)


def cal_after_alarm_times(i, j, tensor, tau_max=10):
    """
    查看告警 i 前告警 j 出现的次数
    """
    mask = (tensor['event'] == j)
    roll = (tensor['event'] == i)
    temp = roll.copy()
    for _ in range(tau_max):
        temp = np.roll(temp, 1)
        roll = (roll | temp)
    return np.sum(mask & roll)


def load_data(d_id):
    """
    加载数据
    """
    # 获取告警数据
    alarm_data = pd.read_csv('./datasets_phase2/%s/Alarm.csv' % d_id, encoding='utf')

    # 获取拓扑图
    if d_id in topology_ids:
        topology_data = np.load('./datasets_phase2/%s/Topology.npy' % d_id)
    else:
        device_num = len(alarm_data['device_id'].unique())
        topology_data = np.zeros((device_num, device_num))

    print('加载告警数据...')
    print(alarm_data.head())

    print('转换数据...')
    X = transform_cols(alarm_data)
    print(X.head())

    return alarm_data, topology_data, X


def split_graph(X, topology_data):
    """
    划分连通图
    """
    print('划分连通图...')
    clusters = to_clusters(topology_data)

    for i, cluster in enumerate(clusters):
        tensor = X[X['node'].isin(cluster)]
        print(str(i) + ': ', cluster, tensor['event'].unique())

    return clusters


def count_front_alarm(clusters, X, tau_max=7, bias_rate=0.005):
    """
    统计发生在每一告警前的其他告警的数量（按照连通图），可认为是可能的父结点
    """
    front_time_dict = {}
    tau_max = 7
    bias_rate = 0.005
    for i in tqdm(range(mat_shapes_phase2[data_id - 1])):
        front_time_dict[i] = {}
        for j in range(mat_shapes_phase2[data_id - 1]):
            if i == j:
                continue
            all_time = 0
            for cluster in clusters:
                tensor = get_cluster_data(X, cluster)
                indi_time = cal_front_alarm_times(i, j, tensor, tau_max=tau_max)
                indi_time -= np.sum(tensor['event'] == j) * bias_rate
                all_time += indi_time
            front_time_dict[i][j] = all_time
    # print(front_time_dict)

    return front_time_dict


def count_after_alarm(clusters, X, tau_max=7, bias_rate=0.005):
    """
    统计发生在每一告警后的其他告警的数量（按照连通图），可认为是可能的子结点
    """
    after_time_dict = {}
    tau_max = 7
    bias_rate = 0.005
    for i in tqdm(range(mat_shapes_phase2[data_id - 1])):
        after_time_dict[i] = {}
        for j in range(mat_shapes_phase2[data_id - 1]):
            if i == j:
                continue
            all_time = 0
            for cluster in clusters:
                tensor = get_cluster_data(X, cluster)
                indi_time = cal_after_alarm_times(i, j, tensor, tau_max=tau_max,)
                indi_time -= np.sum(tensor['event'] == j) * bias_rate
                all_time += indi_time
            after_time_dict[i][j] = all_time
    # print(after_time_dict)

    return after_time_dict


def sort_time_alarm(time_dict):
    """
    按次数排序，找出次数最多的
    """
    event_dict = {}
    for i in tqdm(range(mat_shapes_phase2[data_id - 1])):
        event_list = np.array([key for key in time_dict[i].keys()])
        time_event_list = np.array([time_dict[i][key] for key in time_dict[i].keys()])
        event_order = event_list[np.argsort(time_event_list)[::-1]]
        event_dict[i] = list(event_order)

    for key, value in event_dict.items():
        print(str(key) + ":", value[:10])

    return event_dict


if __name__ == '__main__':
    alarm_data, topology_data, X = load_data(data_id)
    clusters = split_graph(X, topology_data)
    front_time_dict = count_front_alarm(clusters, X)
    print('可能的父结点...')
    sort_time_alarm(front_time_dict)
    after_time_dict = count_front_alarm(clusters, X)
    print('可能的字结点...')
    sort_time_alarm(after_time_dict)

