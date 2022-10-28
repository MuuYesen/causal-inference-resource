# 因果推断竞赛


### 一、相关竞赛

| 竞赛      | 全称 |
| ----------- | ----------- |
| PCIC 2021      | 华为 & 北京大学因果推理挑战赛 |
| WAIC 2022      | 黑客松九章云极赛道 - 因果学习和决策优化挑战赛 |
| PCIC 2022      | 华为 & 北京大学因果推理挑战赛 |

### 二、如何使用

#### 1. 安装anaconda
https://mirrors.tuna.tsinghua.edu.cn/anaconda/archive/

#### 2. 创建conda虚拟环境
```python
conda create -n causal-inference-resource python==3.7.12
```

#### 3. 安装其它依赖包
```python
conda activate causal-inference-resource

pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

#### 4. 安装cdt所需的R包
https://zhuanlan.zhihu.com/p/354912485

注意，修改的文件是conda虚拟环境中的Setting.py， 如：
```python
D:\Learn_Software\anaconda3\envs\causal-inference-resource\Lib\site-packages\cdt\utils\Settings.py
```

#### 5. 环境搭建完成
执行该目录下任一子目录的主函数并得到结果。



