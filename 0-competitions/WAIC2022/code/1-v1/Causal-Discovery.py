import graphviz
import networkx as nx
import pandas as pd
import numpy as np
from IPython.core.display import display
from matplotlib import pyplot as plt
from sklearn.preprocessing import OrdinalEncoder, StandardScaler

import cdt

train = pd.read_csv('../../data/train.csv')
test = pd.read_csv('../../data/test.csv')

# replace nan
def build_data(train):
    train_ = {}
    for i in train.columns:
        train_i = train[i]
        if any(train[i].isna()):
            train_i = train_i.replace(np.nan, train[i].mean())
        if len(train_i.value_counts()) <= 20 and train_i.dtype != object:
            train_i = train_i.astype(int)
        train_[i] = train_i

    return pd.DataFrame(train_)

train = build_data(train)
test = build_data(test)

all_cov = list(train.columns)
# save data and their corresponding transformers
class TransData:
    def __init__(self, name, is_obj=False):
        self.is_obj = is_obj
        self.name = name
        self.transformer = None

    def __call__(self, data):
        self.df = data[self.name]
        series = self.df.to_numpy().reshape(-1, 1)
        if self.df.dtype == object:
            self.is_obj = True
            self.transformer = OrdinalEncoder()
            self.data = self.transformer.fit_transform(series).astype(int)
        elif self.df.dtype != int:
            self.transformer = StandardScaler()
            self.data = self.transformer.fit_transform(series)
        else:
            self.data = series

# data preprocessing
data_dict = {}
cat_name = []
test_dict = {}

for name in all_cov:
    t = TransData(name=name)
    t(train)
    data_dict[name] = t.data.reshape(-1, )
    if t.is_obj:
        cat_name.append(name)
    if name not in ['treatment', 'outcome']:
        try:
            test_i = t.transformer.transform(test[name].values.reshape(-1, 1)).reshape(-1, )
        except:
            test_i = test[name]
        test_dict[name] = test_i
train_transformed = pd.DataFrame(data_dict)
test_data = pd.DataFrame(test_dict)

print(train_transformed.shape)
train_transformed = train_transformed.drop(['V_20','V_26','V_27'],axis=1)
print(train_transformed.shape)

def make_graph(adjacency_matrix, labels=None):
    idx = np.abs(adjacency_matrix) > 0.01
    dirs = np.where(idx)
    d = graphviz.Digraph(engine='dot')
    names = labels if labels else [f'x{i}' for i in range(len(adjacency_matrix))]
    for name in names:
        d.node(name)
    for to, from_, coef in zip(dirs[0], dirs[1], adjacency_matrix[idx]):
        d.edge(names[from_], names[to], label=str(coef))
    return d


def str_to_dot(string):
    '''
    Converts input string from graphviz library to valid DOT graph format.
    '''
    graph = string.replace('\n', ';').replace('\t', '')
    graph = graph[:9] + graph[10:-2] + '}'
    return graph


from cdt.causality.graph import LiNGAM, PC, GES

graphs = {}
method_dict = {
    'LiNGAM': LiNGAM,
    'PC': PC,
    'GES': GES,
}

for method in method_dict.keys():
    print("Method : %s" % (method))

    obj = method_dict[method]()
    output = obj.predict(train_transformed)  # networkx.classes.digraph.DiGraph

    adj_matrix = nx.to_numpy_matrix(output)  # numpy.matrix
    adj_array = np.asarray(adj_matrix)  # numpy.ndarray
    graph_dot = make_graph(adj_array, train.columns.tolist())  # graphviz.graphs.Digraph

    display(graph_dot)
    graphs[method] = graph_dot
    # Infer the causal diagram
    # Visualize the diagram
    nx.draw_networkx(output)
    plt.show()
