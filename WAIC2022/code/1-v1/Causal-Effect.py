import re

import graphviz
import networkx as nx
import pandas as pd
import numpy as np
from IPython.core.display import display
from matplotlib import pyplot as plt
from sklearn.preprocessing import OrdinalEncoder, StandardScaler

import cdt

file = './result/Graph.txt'
graph = open(file,"r")
lines = graph.readlines()
vars_1 = []
vars_2 = []
vars_3 = []
vars_4 = []
for line in lines:
    if 'treatment -> ' in line and 'outcome' not in line:
        var = re.findall(r"V_[0-9]{0,3}",line)
        vars_1.append(var[0])
    if ' -> treatment' in line and 'outcome' not in line:
        var = re.findall(r"V_[0-9]{1,3}",line)
        vars_2.append(var[0])
    if 'outcome -> ' in line and 'treatment' not in line:
        var = re.findall(r"V_[0-9]{1,3}",line)
        vars_3.append(var[0])
    if ' -> outcome' in line and 'treatment' not in line:
        var = re.findall(r"V_[0-9]{1,3}",line)
        vars_4.append(var[0])
    if 'Method : PC' in line:
        # print(vars_1,vars_2,vars_3,vars_4)
        w = [i for i in vars_2 if i  in vars_4]
        c = [i for i in vars_1 if i  in vars_3]
        print("Method : LiNGAM:",w,c)
        vars_1 = []
        vars_2 = []
        vars_3 = []
        vars_4 = []
    if 'Method : GES' in line:
        # print(vars_1, vars_2, vars_3, vars_4)
        w = [i for i in vars_2 if i  in vars_4]
        c = [i for i in vars_1 if i  in vars_3]
        print("Method : PC:", w, c)
        vars_1 = []
        vars_2 = []
        vars_3 = []
        vars_4 = []


# print(vars_1,vars_2,vars_3,vars_4)
w = [i for i in vars_2 if i  in vars_4]
c = [i for i in vars_1 if i  in vars_3]
print("Method : GES:", w, c)