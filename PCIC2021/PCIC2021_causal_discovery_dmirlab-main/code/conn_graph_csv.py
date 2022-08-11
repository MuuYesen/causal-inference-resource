import numpy as np
import pandas as pd
from tqdm import tqdm
import os

"""
根据拓扑图来划分连通图，并将每个连通图保存为csv文件，用于观察
"""

data_id = 1  # data_id = 2

topology_ids = [1, 2, 6, 7, 8, 10]

mat_shapes_phase2 = [24, 25, 15, 17, 17, 19, 20, 20, 22, 22]

cluster_result_path = "./results/test_cluster/%s" % data_id
if not os.path.exists(cluster_result_path):
    os.makedirs(cluster_result_path)


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

    print(alarm_data.head())

    return alarm_data, topology_data


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


def conn_graph_to_csv(alarm_data, clusters):
    for i, cluster in enumerate(clusters):
        alarm_data_cluster = alarm_data[alarm_data['device_id'].isin(cluster)]
        cluster_path = os.path.join(cluster_result_path, 'data1_%s.csv'%i)
        alarm_data_cluster.to_csv(cluster_path)


if __name__ == '__main__':
    alarm_data, topology_data = load_data(data_id)
    clusters = to_clusters(topology_data)
    conn_graph_to_csv(alarm_data, clusters)
