import pandas as pd
import numpy as np
from castle.metrics import MetricsDAG
from castle.algorithms import TTPM
from castle_mod.algorithms import PTHP
from castle.competition import submission
path = './datasets_phase2/data phase2/'


class Find_casual(object):
    def __init__(self):
        self.num = 0
        self.alarm_data = None   # 告警
        self.topology_matrix = None  # 拓扑结构
        self.est_causal_matrix = None   # 估计得到的因果图
        self.para_with_topo = {
            6: {"delta": 0.015, "epsilon": 0.6, "sep": []},
            7: {"delta": 0.01, "epsilon": 0.5, "sep": [-11, -3]},
            8: {"delta": 0.015, "epsilon": 0.6, "sep": []},
            10: {"delta": 0.01, "epsilon": 1, "sep": [-18, -2]}
        }

    def read_data(self, k, count):
        self.num = k
        alarm_data = pd.read_csv(path+str(self.num)+'/Alarm.csv', encoding='utf')
        alarm_data = alarm_data.iloc[:, 0:3]
        alarm_data.columns = ['event', 'node', 'timestamp']
        self.alarm_data = alarm_data.reindex(columns=['event', 'timestamp', 'node'])
        if count == 0:
            self.alarm_data = self.alarm_data.iloc[:, :]
        else:
            self.alarm_data = self.alarm_data.iloc[:count, :]
        try:
            self.topology_matrix = np.load(path + str(self.num) + '/Topology.npy')
        except:
            # print(max(self.alarm_data["event"].values)+1)
            self.topology_matrix = np.zeros(shape=(max(self.alarm_data["node"].values)+1, max(self.alarm_data["node"].values)+1))

        if self.num in [1, 2]: #
            self.topology_matrix = np.zeros(
                shape=(max(self.alarm_data["node"].values) + 1, max(self.alarm_data["node"].values) + 1))

    def run_ttpm(self, delta=0.1, max_hop=1, penalty='AIC', max_iter=100, epsilon=1.0, sep=[], prior_matrix=None):
        if prior_matrix is None:
            ttpm = TTPM(self.topology_matrix, max_hop=max_hop, max_iter=max_iter, delta=delta, penalty=penalty, epsilon=epsilon)
        else:
            ttpm = PTHP(self.topology_matrix, prior_matrix=prior_matrix, max_hop=max_hop, max_iter=max_iter, delta=delta, penalty=penalty, epsilon=epsilon)
        ttpm.learn(self.alarm_data)
        self.est_causal_matrix = ttpm.causal_matrix.to_numpy()
        np.fill_diagonal(self.est_causal_matrix, 0)
        if sep:
            self.est_causal_matrix[sep[0]][sep[0]] = 1
        np.save('./submitnpy/'+str(self.num)+'.npy', self.est_causal_matrix)

    def main(self):
        for i in range(1, 11):
            # 3\4\5\9 without topo
            # 依据初赛的先验，由于不太设备间不会存在影响，我们采用TTPM模型，并使用如下参数：
            if i in [3, 4, 5, 9]:
                self.read_data(i, 0)
                self.run_ttpm(delta=0.01, max_hop=2, penalty='BIC', max_iter=100, epsilon=1.0)
            # 1\2\6\7\8\10包含拓扑结构，经过分析可知1、2数据集的拓扑图较大、结构类似，故以此对其进行分类。
            if i in [6, 7, 8, 10]:
                self.read_data(i, 5000)
                self.run_ttpm(delta=self.para_with_topo[i]["delta"], max_hop=2, penalty='BIC', max_iter=100, epsilon=self.para_with_topo[i]["epsilon"], sep=self.para_with_topo[i]["sep"])
            # 查看其拓扑图，可以看到这两个数据的拓扑图包含多个独立的连通子图，可以通过两方面来寻找根因
            # 通过预处理及pcmic等模型来寻找潜在的因果结构（设备间的影响）
            # 暂时不考虑拓扑结构，找出自身因果关系（设备自身影响）
            if i in [1, 2]:
                self.read_data(i, 5000)
                prior_matrix = np.load("./results/prior_matrix"+str(i)+".npy")
                # 寻找自身因果关系
                self.run_ttpm(delta=self.para_with_topo[i]["delta"], max_hop=2, penalty='BIC', max_iter=100,
                              epsilon=self.para_with_topo[i]["epsilon"], sep=self.para_with_topo[i]["sep"],prior_matrix=prior_matrix)
                # 添加设备间影响
                self.est_causal_matrix[self.est_causal_matrix > 0] = 1
                np.save('./submitnpy/' + str(i) + '.npy', self.est_causal_matrix)


if __name__ == '__main__':
    ttpm = Find_casual()
    ttpm.main()