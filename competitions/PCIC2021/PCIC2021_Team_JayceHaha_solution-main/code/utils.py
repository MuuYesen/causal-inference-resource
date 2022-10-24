import os
import numpy as np
import pandas as pd
from loguru import logger


def load_data(data_id: int, data_basepath: str):
    # Read historic alarm data
    data_path = os.path.join(data_basepath, str(data_id))
    alarm_data = pd.read_csv(os.path.join(data_path, "Alarm.csv"), encoding='utf')

    # Read topology data.
    topology_matrix = None
    topo_filepath = os.path.join(data_path, "Topology.npy")
    if os.path.exists(topo_filepath):
        topology_matrix = np.load(topo_filepath)

    # Read ground true causal matrix
    true_causal_matrix = None
    dag_filepath = os.path.join(data_basepath, str(data_id), "DAG.npy")
    if os.path.exists(dag_filepath):
        true_causal_matrix = np.load(dag_filepath)

    return alarm_data, topology_matrix, true_causal_matrix


def remove_diagnal_entries(mat):
    """
    set the diagonal of a matrix to be 0
    """
    mat_copy = np.copy(mat)
    indices_diag = np.diag_indices(len(mat_copy))
    mat_copy[indices_diag] = 0
    return mat_copy


def load_ttpm_result(est_dag_path, dt_idx, best_iter):
    dag_file = os.path.join(est_dag_path, f"est_dag_data_{dt_idx}_iter_{best_iter}.npy")
    est_dag_org = np.load(dag_file).astype(np.int32)
    est_dag = remove_diagnal_entries(est_dag_org)
    return est_dag


def get_skeleton_from_dag(causal_dag: np.ndarray):
    xs, ys = causal_dag.nonzero()
    skeleton = causal_dag.copy()
    skeleton[ys, xs] = 1
    return skeleton


def markout_positive_graph(est_graph, true_graph):
    marked_graph = est_graph.copy()
    marked_graph[est_graph != true_graph] = -1
    return marked_graph


def plot_causal_graph(causal_matrix, weight_matrix=None, savefig=None):
    import graphviz

    num_edges = len(causal_matrix)
    dag = graphviz.Digraph()
    for i in range(num_edges):
        dag.node(f"{i}")
    for i in range(num_edges):
        for j in range(num_edges):
            if causal_matrix[i, j] > 0:
                if weight_matrix is not None:
                    weight = weight_matrix[i, j]
                    # dag.edge(str(i), str(j), weight=str(weight), label="{:.3f}".format(weight))
                    dag.edge(str(i), str(j), label="{:.3f}".format(weight))
                else:
                    dag.edge(str(i), str(j))
    if savefig is not None:
        dag.render(filename=savefig, view=False, cleanup=True, format="png")
        print("#### save causal graph to:", f"{savefig}.png")
    return dag


def convert_graph_to_readable_text(graph_matrix):
    """"NOTE: state_map.shape: [x_max, y_max]"""
    binary_chars = "⬜🟫🟥🟡🚫"
    num_nodes = len(graph_matrix)
    header_line = "   " + "".join(["{:02d}".format(x) for x in range(num_nodes)])
    text_lines = [header_line]
    for idx in range(num_nodes):
        readable_line = "{:02d} {}".format(idx, "".join([binary_chars[int(val)] for val in graph_matrix[idx]]))
        text_lines.append(readable_line)
    return "\n".join(text_lines)


def print_graph_text(*args):
    for lines in zip(*[mtext.split("\n") for mtext in args]):
        print(" ".join(lines))


def print_graphs(*arr_list):
    print_graph_text(*[convert_graph_to_readable_text(arr) for arr in arr_list])


def print_matrix(matrix_vals, ff="{:6.3f}"):
    header_line = "   " + "".join(["{:7d}".format(x) for x in range(len(matrix_vals[0]))])
    text_lines = [header_line]
    for idx, row in enumerate(matrix_vals):
        readable_line = "{:02d} [{}]".format(idx, " ".join([ff.format(val) for val in row]))
        text_lines.append(readable_line)
    print("-" * len(header_line))
    print("\n".join(text_lines))
    # print("-" * len(header_line))


def print_vector(*args):
    header_line = "".join(["{:7d}".format(x) for x in range(len(args[0]))])
    text_lines = [header_line]
    for vector_vals in args:
        readable_line = "[{}]".format(" ".join(["{:6.3f}".format(val) for val in vector_vals]))
        text_lines.append(readable_line)
    print("-" * len(header_line))
    print("\n".join(text_lines))


def get_matrix_avg_std(matrix):
    """calculate delta, mean, std along row axis without diagonal values"""
    N = len(matrix)
    avg_vector = np.sum(matrix, axis=0, keepdims=True) / (N - 1)
    diag_mask = 1 - np.identity(N, dtype=np.float32)
    dlt_matrix = (matrix - avg_vector) * diag_mask
    std_vector = np.sqrt(np.sum(np.square(dlt_matrix), axis=0, keepdims=True)) / (N - 1)
    return dlt_matrix, avg_vector, std_vector


def get_dag_by_sort(matrix, ratio=0.25, larger_better=True):
    num_edges = len(matrix)
    matrix_flatten = matrix.reshape(-1)
    sorted_indexs = np.argsort(matrix_flatten)
    if larger_better:
        sorted_indexs = sorted_indexs[::-1]
    num_cut = int(num_edges*num_edges * ratio)
    # logger.info("num_edges: {}, num_cut: {}", num_edges, num_cut)
    selected_indexs = sorted_indexs[:num_cut]
    selected_rows = selected_indexs // num_edges
    selected_cols = selected_indexs % num_edges
    est_dag_by_sort = np.zeros_like(matrix, dtype=np.int32)
    est_dag_by_sort[selected_rows, selected_cols] = 1

    xs, ys = np.nonzero(est_dag_by_sort)
    pairs = set([(x, y) for x, y in zip(xs, ys)])
    pairs_t = set([(y, x) for x, y in zip(xs, ys)])
    loop_edges = [p for p in pairs if p in pairs_t]
    print("#### loop edges:", loop_edges)
    # print_graphs(est_dag_by_sort)

    for x, y in loop_edges:
        if (matrix[x, y] > matrix[y, x]) and larger_better:
            # print((x, y), matrix[x, y], matrix[y, x], larger_better, "remove:", (y, x))
            est_dag_by_sort[y, x] = 0
        else:
            # print((x, y), matrix[x, y], matrix[y, x], larger_better, "remove:", (x, y))
            est_dag_by_sort[x, y] = 0

    return est_dag_by_sort


def remove_loop_edges(edge_mat, weight_mat):
    # sort edges
    row_idxs, col_idxs = np.nonzero(edge_mat)
    selected_effects = weight_mat[row_idxs, col_idxs]
    indexs = np.argsort(selected_effects)
    edges_sorted = list(zip(row_idxs[indexs], col_idxs[indexs]))
    print("######## edges_sorted", edges_sorted)

    node_children_dict = dict()
    for i in range(len(edge_mat)):
        children = np.nonzero(edge_mat[i])[0]
        if len(children) == 0:
            continue
        indexs = np.argsort(weight_mat[i, children])
        children = children[indexs]
        node_children_dict[i] = children

    # print("node_children_dict:", node_children_dict)

    invalid_edges = list()

    def _rm_loop(c, path):
        if c not in node_children_dict:
            # no more child
            return False
        for child in node_children_dict[c]:
            # if child in path:
            if child == path[0]:
                # found a loop
                # print("found a loop, root: {}, path: {}".format((path[0], path[1]), path))
                invalid_edges.append((path[0], path[1]))
                return True
            elif child in path:
                continue
            else:
                if _rm_loop(child, path + [child]):
                    return True
        return False

    for i, j in edges_sorted:
        if _rm_loop(j, [i, j]):
            children = node_children_dict[i]
            children = [n for n in children if n != j]
            node_children_dict[i] = children
            # print("delete {}, update children as: {}".format((i, j), children))

    edge_mat_filtered = np.copy(edge_mat)
    for i, j in invalid_edges:
        edge_mat_filtered[i, j] = 0
    print("invalid_edges:", invalid_edges)
    return edge_mat_filtered


def merge_dag_by_sort(dags, ratio=0.25):
    num_edges = len(dags[0][0])
    orders_list = [np.argsort(dag.flatten()) for dag in dags]
    orders_sum = np.sum(orders_list, axis=0)
    sorted_indices = np.argsort(orders_sum)
    num_cut = int(num_edges*num_edges * ratio)
    final_indices = sorted_indices[:num_cut]

    selected_rows = final_indices // num_edges
    selected_cols = final_indices % num_edges
    est_dag_by_sort = np.zeros((num_edges, num_edges), dtype=np.int32)
    est_dag_by_sort[selected_rows, selected_cols] = 1
    return est_dag_by_sort


def get_common_parent(dag, edge):
    pa = np.nonzero(dag[:, edge[0]])[0]
    pb = np.nonzero(dag[:, edge[1]])[0]
    return [p for p in pa if p in pb]
