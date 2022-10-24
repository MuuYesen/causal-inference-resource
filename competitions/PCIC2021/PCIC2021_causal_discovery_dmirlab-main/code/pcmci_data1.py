import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from tigramite import data_processing as pp
from tigramite.pcmci import PCMCI
from tigramite.independence_tests import ParCorr
from tqdm import tqdm
import seaborn as sns
import os

"""
pcmci模型，用于辅助先验信息的判断
"""

data_id = 1
delta_t = 3  # （时间窗口大小）
pc_alpha = 0.05
tau_max = 5


def transform_cols(data, cols=None):
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


def to_clusters(topology_data):
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


topology_ids = [1, 2, 6, 7, 8, 10]

mat_shapes_phase2 = [24, 25, 15, 17, 17, 19, 20, 20, 22, 22]

"""
读取数据
"""
print('加载数据...')
alarm_data = pd.read_csv('./datasets_phase2/%s/Alarm.csv' % data_id, encoding='utf')

# 转换数据
X = transform_cols(alarm_data)

# 获取拓扑图
if data_id in topology_ids:
    topology_data = np.load('./datasets_phase2/%s/Topology.npy' % data_id)
else:
    device_num = len(alarm_data['device_id'].unique())
    topology_data = np.zeros((device_num, device_num))

# 划分连通图
print('划分连通图...')
clusters = to_clusters(topology_data)
# for i, cluster in enumerate(clusters):
#     tensor = X[X['node'].isin(cluster)]
#     print(tensor['event'].unique(), len(tensor), i)

"""
转换数据
"""
print('转换数据...')
# 获取部分连通图，要求连通图包含所有的告警类型（事件）
for i, cluster in enumerate(clusters):
    temp = X[X['node'].isin(cluster)]
    print(len(temp['event'].unique()), len(temp), i)

selected_index = []
for i in [3, 38]:  # 选择连通图3、38，包含所有的告警类型（事件）
    selected_index += clusters[i]

# 获取最终的训练数据
if data_id == 2 or data_id == 1:
    X_tensor = X[X['node'].isin(selected_index)]
else:
    X_tensor = X[:5000]
print(len(X['event'].unique()), len(X_tensor['event'].unique()))


"""
划分时间窗口
"""
print('划分时间窗口...')
# 计算每个时间窗口的事件次数
event_uniq = X_tensor["event"].unique()
event_uniq.sort()
node_uniq = X_tensor["node"].unique()
node_uniq.sort()

max_s_t = X_tensor['timestamp'].max()
min_s_t = X_tensor['timestamp'].min()

# 计算时间间隔
tensor = X_tensor.copy()
tensor["interval"] = np.floor((tensor['timestamp'] - min_s_t) / delta_t).astype(int)
# print(tensor.head)

# 聚合操作，统计不同事件数量
tensor = tensor.groupby(
            ['event', 'node', 'interval']).apply(len).reset_index()
tensor.columns = ['event', 'node', 'interval', 'times']
tensor = tensor.reindex(columns=['node', 'interval', 'event', 'times'])
tensor.sort_values(by=['interval'])
# print(tensor.shape)
# print(tensor.head())

# 不区分不同结点进行划分
not_node_data = tensor.copy()
not_node_onehot = pd.get_dummies(not_node_data["event"])
not_node_data[not_node_onehot.columns] = not_node_onehot * np.array(not_node_data[["times"]])
not_node_data = not_node_data.drop(['event', 'times', 'node'], axis=1)
not_node_data = not_node_data.groupby('interval').apply(np.sum)
not_node_data.index = np.arange(not_node_data.shape[0])
not_node_data = not_node_data.sort_values(by=['interval'])
X_data = not_node_data.iloc[:,1:]
# print(not_node_data.head())


"""
运行模型
"""
print('运行pcmci...')
dataframe = pp.DataFrame(np.array(X_data.astype(np.float64)))
parcorr_pcmci = PCMCI(dataframe=dataframe, cond_ind_test=ParCorr())
parcorr_result = parcorr_pcmci.run_pcmci(tau_max=tau_max, pc_alpha=pc_alpha)


"""
绘制因果图
"""
print('绘制因果图...')

p_th = 0.005
print('delta_t = %s' % delta_t)
print('pc_alpha = %s' % pc_alpha)
print('tau_max = %s' % tau_max)
print('p_th = %s' % p_th)

for tau in range(tau_max+1):
    sns.heatmap(parcorr_result['p_matrix'][:, :, tau]<p_th,
                linewidths = 0.01,
                vmax=1.0,
                vmin=-1.0,
                cmap='rainbow')
    plt.xlabel("effect")
    plt.ylabel("cause")
    plt.title(r"the causal graph tau=%s" % tau)
    plt.show()

sns.heatmap((parcorr_result['p_matrix']<p_th).sum(axis=2) >= 0.7*(tau_max+1),
            linewidths = 0.01,
            vmax=1.0,
            vmin=-1.0,
            cmap='rainbow')
plt.xlabel("effect")
plt.ylabel("cause")
plt.title(r"the causal graph")
plt.show()