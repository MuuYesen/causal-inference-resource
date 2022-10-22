### PCIC 2022 | 华为 & 北京大学因果推理挑战赛

#### 一、竞赛主页
https://competition.huaweicloud.com/information/1000041792/circumstance

#### 二、任务与主题
Given a dataset, build a transfer learning solution using the labeled source samples (city A) plus a few labeled target samples (city B) to train a failure prediction model for the unlabeled samples of city B.

#### 三、当前方案进展

| 方案      | 结果 | 分数 |
| ----------- | ----------- | ----------- |
| 0-default      |             | 0.62 |
| 1-explore      |        |  |
| 2-convlstm     |             | |
| 3-causal_autoencoder            |             | |
|             |             | |

#### 四、迁移学习の参考资料

##### 1. 仅源域样本【带标签】：比如 因果学习、稳定学习、特殊领域自适应

《Learning Causal Representations for Robust Domain Adaptation》：https://arxiv.org/abs/2011.06317

##### 2. 同时源域样本【带标签】和目标域样本【无标签】：比如 无监督领域自适应

《Dual-Representation-Based Autoencoder for Domain Adaptation》：https://ieeexplore.ieee.org/abstract/document/9314101

《Time Series Domain Adaptation via Sparse Associative Structure Alignment》：https://arxiv.org/abs/2012.11797

《Time-Series Domain Adaptation via Sparse Associative Structure Alignment: Learning Invariance and Variance》：https://arxiv.org/abs/2205.03554

##### 3. 同时源域样本【带标签】和目标域样本【有标签】：比如 参数微调、有监督领域自适应

《基于LSTM与迁移学习的滚动轴承故障诊断》：http://clgzk.qks.cqut.edu.cn/CN/abstract/abstract5417.shtml

《Transferable Time-Series Forecasting under Causal Conditional Shift》：https://arxiv.org/abs/2111.03422


##### 4. 其余的资料

《迁移学习简介与分类》：https://zhuanlan.zhihu.com/p/436377664