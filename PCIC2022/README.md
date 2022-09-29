### PCIC 2022 | 华为 & 北京大学因果推理挑战赛

#### 一、竞赛主页
https://competition.huaweicloud.com/information/1000041792/circumstance

#### 二、任务与主题
Given a dataset, build a transfer learning solution using the labeled source samples (city A) plus a few labeled target samples (city B) to train a failure prediction model for the unlabeled samples of city B.

#### 三、当前方案进展

| 方案      | 结果 | 分数 |
| ----------- | ----------- | ----------- |
| 0-explore      |        |  |
|    1-v1         |             | |
|             |             | |

#### 四、迁移学习の参考资料

##### 1. 仅源域样本【带标签】：基于因果 或 稳定学习

《Learning Causal Representations for Robust Domain Adaptation》：https://arxiv.org/abs/2011.06317

##### 2. 同时源域样本【带标签】和目标域样本【无标签】：基于领域自适应

《Dual-Representation-Based Autoencoder for Domain Adaptation》：https://ieeexplore.ieee.org/abstract/document/9314101

##### 3. 同时源域样本【带标签】和目标域样本【有标签】：基于参数微调

《基于LSTM与迁移学习的滚动轴承故障诊断》：http://clgzk.qks.cqut.edu.cn/CN/abstract/abstract5417.shtml

##### 4. 其余的资料

《迁移学习简介与分类》：https://zhuanlan.zhihu.com/p/436377664