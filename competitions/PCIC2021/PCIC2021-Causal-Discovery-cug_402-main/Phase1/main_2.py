import os
import pandas as pd
import numpy as np
# from castle.common import GraphDAG
# from castle.metrics import MetricsDAG
# from castle.datasets import DAG, Topology
from castle.algorithms import TTPM

# Read historic alarm data and topology data.
alarm_data = pd.read_csv('D:/PycharmProjects/pythonProject/venv/2/Alarm.csv', encoding='utf')
# topology_matrix = np.load('./4/Topology.npy')
# Data preprocessing and causal structure learning
X = alarm_data.iloc[:, 0:3]
X.columns = ['event', 'node', 'timestamp']
X = X.reindex(columns=['event', 'timestamp', 'node'])

base_dir = os.path.join('D:/PycharmProjects/pythonProject/venv/2')
if os.path.exists(os.path.join(base_dir, 'Topology.npy')):
    topology_matrix = np.load(os.path.join(base_dir, 'Topology.npy'))
else:
    num_nodes = len(set(X['node']))
    topology_matrix = np.zeros((num_nodes, num_nodes))  # 全为0的空矩阵.

# topology_matrix = np.load('D:/PycharmProjects/pythonProject/venv/3/Topology.npy')

i = 40  # i为迭代次数
# g_score = 0
# while g_score < 0.9:
# causal structure learning using TTPM
ttpm = TTPM(topology_matrix, delta=0.01, max_hop=2, max_iter=i)
ttpm.learn(X)
# Obtain estimated causal structure and save it
# est_causal_matrix = ttpm.causal_matrix.to_numpy()
# true_causal_matrix = np.load('D:/PycharmProjects/pythonProject/venv/3/DAG.npy')
# Comparsion of the estimated graph and the true graph
# GraphDAG(est_causal_matrix, true_causal_matrix)
# calculate g-score
# g_score = MetricsDAG(est_causal_matrix, true_causal_matrix).metrics['gscore']
# print('g-score:%.3f' % g_score)
# i = i + 1

# print('g-score:%.3f,iter=%d' % (g_score, i-1))
# GraphDAG(est_causal_matrix, true_causal_matrix)
