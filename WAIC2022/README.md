### WAIC 2022 黑客松九章云极赛道-因果学习和决策优化挑战赛

#### 一、竞赛主页
https://tianchi.aliyun.com/competition/entrance/532019/information

#### 二、任务与主题

因果学习可以通俗地定义为一个结合了因果推断和机器学习，研究因果关系和回答因果问题的人工智能技术。本次挑战赛以“如何优化干预方案能使因果效应最大”为主题，考察参赛者在基于因果推断策略制定问题上的估计能力。

#### 三、赛题讲解直播回放
https://pan.baidu.com/wap/init?surl=Jsc3L1Sn4UJQvKdYzygWKQ         &emsp;&emsp;&emsp;提取码：0c6s

#### 四、当前方案进展

| 方案      | 结果 | 分数 |
| ----------- | ----------- | ----------- |
| 0-baseline      | ce.csv       | 2.8975 |
|             |   ce_ct_all.csv       | 3.3110 |
|             |    ce_dml_all.csv        | 2.8193 |
|             |    ce_0_0.csv        | ERROR Wrong input file format |
|             |    ce_e-13_e-13.csv     | 2.8797 |
|             |    ce_0.1_0.046.csv         | 2.8359 |
|    1-v1         |             | |
|             |             | |

#### 五、因果发现の参考资料

##### 1. 结构方程模型

《Causal Models》：https://plato.stanford.edu/entries/causal-models/

《因果关系是什么？结构因果模型入门》：https://mp.weixin.qq.com/s/4g_dQSrr9bmxjkl1B3TLVg

《基于时序数据的线性非高斯模型》：https://zhuanlan.zhihu.com/p/369722509

《非时序线性非高斯模型 —— LiNGAM》：https://zhuanlan.zhihu.com/p/369720949

##### 2. 图模型
《基于约束学习的因果发现基础概念》：https://mp.weixin.qq.com/s/gqOpipOhUaRlPdB7f-1TvA

##### 3. 点过程

《R语言和Python用泊松过程扩展：霍克斯过程Hawkes Processes分析比特币交易数据订单到达自激过程时间序列》：https://zhuanlan.zhihu.com/p/488319642

《因果推理之霍克斯过程 Hawkes process》：https://dreamhomes.top/posts/202106241018/

##### 4. 实际应用

《因果发现在因子选择（特征选择）场景下的应用》：https://mp.weixin.qq.com/s/EOuo2rNzt4g01AI0JLn8PQ

##### 5. 其余的资料

《概述：马尔可夫边界、因果发现和因果推理》：https://mp.weixin.qq.com/s/SU61XQnlY8IX44FlQZzp2A

《【翻译】机器学习的理论障碍及因果革命的七个希望》：https://zhuanlan.zhihu.com/p/49461195

#### 六、因果推理の参考资料
##### 1. 平均因果效应 ATE

《大白话谈因果系列文章（二）因果效应估计及论文介绍》：https://zhuanlan.zhihu.com/p/397974913

##### 2. 双重机器学习 DML

《Econml仓库中的DML接口文档页面》：https://econml.azurewebsites.net/_autosummary/econml.dml.DML.html

《【因果推断/uplift建模】Double Machine Learning(DML)》：https://zhuanlan.zhihu.com/p/401010271

《因果推断——借微软EconML测试用DML和deepIV进行反事实预测实验（二十五）》：https://zhuanlan.zhihu.com/p/456080557

《前沿, 双重机器学习方法DML用于因果推断, 实现它的code是什么？》：https://www.shangyexinzhi.com/article/4904811.html

《因果推断笔记——DML ：Double Machine Learning案例学习（十六）》：https://cloud.tencent.com/developer/article/1913968

##### 3. 因果森林 CF

《当机器学习遇上因果推断》:https://cec.blog.caixin.com/archives/216372

《【机器学习-因果推断】因果森林 causalForest 估计 HTE R语言官方案例2》：https://zhuanlan.zhihu.com/p/480466543

《因果森林总结：基于树模型的异质因果效应估计》：https://zhuanlan.zhihu.com/p/448524822

##### 4. 工具变量 IV

《因果推断简介之六：工具变量（instrumental variable）》：https://cosx.org/2013/08/causality6-instrumental-variable

##### 5. 断点回归 RDD

《Stata: 断点回归 (RDD) 教程》：https://zhuanlan.zhihu.com/p/100524478

《断点回归（regression discontinuity design）学习笔记》：https://blog.csdn.net/claire_chen_jia/article/details/108857734

##### 6. 双重差分法 DID

《双重差分法（DID）的原理与实际应用》：https://zhuanlan.zhihu.com/p/400085535

《双重差分法（DID）介绍》：https://zhuanlan.zhihu.com/p/48952513

##### 7. 元学习 ML

《想了解 Meta Learning? 这篇论文一定要读！》：https://juejin.cn/post/6844904116574011400

##### 8. 增量模型 Uplift

《【Uplift】参考资料篇》：https://zhuanlan.zhihu.com/p/358582762

《【Uplift】因果推断基础篇》：https://zhuanlan.zhihu.com/p/362311467

《【Uplift】模拟数据篇》：https://zhuanlan.zhihu.com/p/362411150

《【Uplift】建模方法篇>：https://zhuanlan.zhihu.com/p/362788755

《【Uplift】评估方法篇》：https://zhuanlan.zhihu.com/p/363082639

《【Uplift】特征选择篇》：https://zhuanlan.zhihu.com/p/363866684


##### 9. 倾向性得分匹配法 PSM

《倾向得分匹配法的详细解读》：https://zhuanlan.zhihu.com/p/299976222

《从关联到逻辑：因果推断初探》：https://mp.weixin.qq.com/s/qGNP_XeyQYbrRerQCVR5Xg


##### 10. 其余的资料

《Dowhy因果推断，简单教程》：https://mp.weixin.qq.com/s/p69Vzll7cxRxiSRtUiYb9g

《被忽视的因果结构：为什么合理选择控制变量很重要？》：https://zhuanlan.zhihu.com/p/371216533

《因果推断概要》：https://zhuanlan.zhihu.com/p/362587309

《因果推理综述——《A Survey on Causal Inference》一文的总结和梳理》：https://www.cnblogs.com/caoyusang/p/13518354.html

《因果科学应用范式》：https://zhuanlan.zhihu.com/p/421540391