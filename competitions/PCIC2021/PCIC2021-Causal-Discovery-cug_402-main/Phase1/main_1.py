# 这是一个示例 Python 脚本。

import pandas as pd
import numpy as np
from castle.common import GraphDAG
from castle.metrics import MetricsDAG
from castle.datasets import DAG, Topology
from castle.algorithms import TTPM
from castle.competition import submission
import os

def remove_diagnal_entries(mat):
    """
    set the diagonal of a matrix to be 0
    """
    mat_copy = np.copy(mat)
    indices_diag = np.diag_indices(len(mat_copy))
    mat_copy[indices_diag] = 0
    return mat_copy

# Read historic alarm data and topology data.
alarm_data = pd.read_csv('./1/Alarm.csv', encoding ='utf')
# # topology_matrix = np.load('./1/Topology.npy')
# Data preprocessing and causal structure learning
X = alarm_data.iloc[:,0:3]
X.columns=['event','node','timestamp']
X = X.reindex(columns=['event','timestamp','node'])
base_dir = os.path.join('./1')
if os.path.exists(os.path.join(base_dir, 'Topology.npy')):
    topology_matrix = np.load(os.path.join(base_dir, 'Topology.npy'))
else:
    num_nodes = len(set(X['node']))
    topology_matrix = np.zeros((num_nodes, num_nodes))  # 全为0

# causal structure learning using TTPM
ttpm = TTPM(topology_matrix,delta=0.01,max_hop=2,max_iter=b) #b为确定的最佳迭代次数
ttpm.learn(X)
# Obtain estimated causal structure and save it
est_causal_matrix = ttpm.causal_matrix.to_numpy()
est_causal_matrix = (remove_diagnal_entries(ttpm.causal_matrix.values))  #去除对角线的值。

np.save('./1.npy',est_causal_matrix)
