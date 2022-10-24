import cdt
import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt
from cdt.causality.graph import PC, LiNGAM

# Load the data
data = pd.read_csv("http://www.causality.inf.ethz.ch/data/lucas0_train.csv")


# Infer the causal diagram
pc_output = LiNGAM().create_graph_from_data(data)

# Visualize the diagram
nx.draw_networkx(pc_output)
plt.show()