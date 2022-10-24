import pandas as pd
import numpy as np
import json

"""
arrs_to_csv: convert your solutions (list of numpy arrays) to the submission format
check_submit_phase1: some preliminary check of the submission for phase 1
evaluate: the function for calculating the score between an estimated graph and the ground truth
"""


def arrs_to_csv(arrs, input_path='submit.csv'):
    """
    This can be used to generate the submission file in .csv

    Parameters:
        arrs: list of your solutions for each dataset; each element should be a numpy array of 0 or 1
        input_path: where to save your file; e.g., submit.csv
    -------

    """
    arrs_str = [arr_to_string(arr) for arr in arrs]
    pd.DataFrame(arrs_str).to_csv(input_path, index=False)


def check_submit_phase1(input_path):
    """
    Preliminary check of whether your submission is compatible with the system

    Parameters
        input_path: input_path: where to load your file; e.g., submit.csv

    """
    #  shapes of datasets in phase 1.
    mat_shapes_phase1 = [10, 11, 12, 13, 13, 14, 15, 16, 17, 18, 13, 20, 21, 16, 18, 24, 25, 26, 27, 29]

    arrs = csv_to_arrs(input_path)
    if len(arrs) != len(mat_shapes_phase1):
        raise ValueError('Number of solutions are not correct')

    for i, mat_int in enumerate(arrs):
        if mat_int.shape[0] != mat_shapes_phase1[i]:
            print(mat_int.shape[0])
            raise ValueError('matrix {} has an incorrect shape'.format(i))

    print('Preliminary check of phase 1: OK')


def evaluate(est_graph_matrix, true_graph_matrix):
    """
    parameters:
        est_graph_matrix: np.ndarray, 0-1 adjacency matrix for the estimated graph
        true_graph_matrix:np.ndarray, 0-1 adjacency matrix for the true graph
    return:
        A score ranges from 0 to 1
    """
    W_p = pd.DataFrame(est_graph_matrix).applymap(lambda elem:1 if elem!=0 else 0)
    W_true = pd.DataFrame(true_graph_matrix).applymap(lambda elem:1 if elem!=0 else 0)
    num_true = W_true.sum(axis=1).sum()
    assert num_true!=0
    # true_positives
    num_tp = (W_p + W_true).applymap(lambda elem:1 if elem==2 else 0).sum(axis=1).sum()
    # False Positives + Reversed Edges
    num_fn_r = (W_p - W_true).applymap(lambda elem:1 if elem==1 else 0).sum(axis=1).sum()
    score = np.max((num_tp-num_fn_r,0))/num_true
    return score


def arr_to_string(mat):
    """
    Parameters
        mat: numpy array with each entry either 0 or 1

    Returns:
        string of the input array
    """
    mat_int = mat.astype(int)
    mat_flatten = mat_int.flatten().tolist()
    for m in mat_flatten:
        if m not in [0, 1]:
            raise TypeError("Value not in {0, 1}.")
    mat_str = ' '.join(map(str, mat_flatten))
    return mat_str


def csv_to_arrs(input_path):
    """
    read submission csv and transmit it back to list of numpy arrays

    Parameters
        input_path: where to load your file; e.g., submit.csv

    Returns
        a list of numpy arrays
    -------

    """
    arrs = []
    arrs_csv = pd.read_csv(input_path)
    arrs_str = arrs_csv.values.tolist()
    for arr in arrs_str:
        mat_flatten = np.fromstring(arr[0], dtype=int, sep=' ')
        n = int(np.sqrt(len(mat_flatten)))
        mat_int = mat_flatten.reshape(n, n)
        arrs.append(mat_int)
    return arrs


def get_test(i):
    matrix_all = []
    # thp-s
    # f = open("../Submitted_Code_thp/result_json.json", "r")
    # result_json = json.load(f)
    # matrix_all.append(np.array(result_json["THP_S"]))
    # print(matrix_all[-1])

    f = open("../phase2/thp_dict.json", "r")
    thp_para = json.load(f)
    # print(thp_para)
    for key in thp_para.keys():
        matrix_ = np.array(thp_para[key])
        # matrix_[matrix_ > 0] = 1
        # print(key)
        # print(np.sum(matrix_))
        matrix_all.append(matrix_)

    # sub_graph = np.load("../phase2/test28_1.npy", allow_pickle=True).tolist()
    # sub_dict = dict(sub_graph)
    # # input(sub_graph)
    # sub_dict_ = {}
    # dalta_list = [0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.1]
    # for key in sub_dict.keys():
    #     for d in range(len(dalta_list)):
    #         sub_dict_[str(dalta_list[d])+"_"+str(key)] = sub_dict[key][d].tolist()
    # print(sub_dict_)
    # json_str = json.dumps(sub_dict_)
    # with open("../phase2/sub_dict.json", "w") as json_file:
    #     json_file.write(json_str)
    # f = open("../phase2/para_dict.json", "r")
    # thp_para = json.load(f)
    # for key in thp_para.keys():
    #     matrix_ = np.array(thp_para[key])
    #     matrix_[matrix_ > 0] = 1
    #     # print(key)
    #     # print(np.sum(matrix_))
    #     matrix_all.append(np.array(thp_para[key]))

    # count = np.zeros(shape=(matrix_all[0].shape[0], matrix_all[0].shape[0]))
    # print(count)
    # for i in range(matrix_all[0].shape[0]):
    #     for j in range(matrix_all[0].shape[0]):
    #         flag = True
    #         for k in range(len(matrix_all)):
    #             if matrix_all[k][i][j] == 0:
    #                 flag = False
    #         if flag == True:
    #             count[i][j] = 1
    # print(count)
    # np.save("../phase2/count.npy", count)
    return matrix_all


def key_point():
    # print(np.load("../phase2/count.npy"))
    count = np.zeros(shape=(24, 24))
    mix = {}
    f = open("./results/sub_dict.json", "r")
    sub_dict = json.load(f)
    f = open("./results/thp_dict.json", "r")
    thp_para = json.load(f)
    # input(np.load("../phase2/testing/1_notopo_5000_0.01_1.npy"))
    for key in thp_para.keys():
        matrix_ = np.array(thp_para[key])
        mix[key] = [matrix_, np.array(sub_dict[key])]
        print(key, np.sum(thp_para[key]), np.sum(sub_dict[key]))
        # print(np.array(sub_dict[key]), np.array(thp_para[key]))
        # print(np.array(sub_dict[key]) == np.array(thp_para[key]))
    # print(mix)

    for i in range(mix["0.02_1"][0].shape[0]):
        for j in range(mix["0.02_1"][0].shape[0]):
            flag = True
            for key in mix.keys():
                if mix[key][0][i][j] == 0:
                    flag = False
                if mix[key][1][i][j] == 0:
                    flag = False
            if flag == True:
                count[i][j] = 1
    print(count)


def fun(topology_data):
    clusters = []
    ii = list(range(topology_data.shape[0]))
    nu = 0
    for i in range(topology_data.shape[0]):
        if i not in ii:
            continue
        cluster = [i]
        ii.remove(i)
        run = True
        while run:
            run = False
            for j in ii:
                if topology_data[j, cluster].sum() > 0:
                    cluster.append(j)
                    ii.remove(j)
                    run = True
                    nu += 1
        clusters.append(cluster)
    return clusters


def data_eda(i):
    path = path = './datasets_phase2/data phase2/'
    alarm_data = pd.read_csv(path + str(i) + '/Alarm.csv', encoding='utf')
    topology_matrix = np.load(path + str(i) + '/Topology.npy')
    # time_dict = {}
    device_dict = {}
    # input(topology_matrix.shape)
    # input(max(alarm_data["device_id"].values))
    # 找连通图,给子图进行标记
    clusters = fun(topology_matrix)
    clusters = dict(zip(range(len(clusters)+1), clusters))
    # input(clusters)
    for index, row in alarm_data.iterrows():
        pass
        # if row["alarm_id"] not in time_dict.keys():
        #     time_dict[row["alarm_id"]] = []
        # time_dict[row["alarm_id"]].append([row["start_timestamp"], row["end_timestamp"], row["start_timestamp"] == row["end_timestamp"]])
        # if row["alarm_id"] not in device_dict.keys():
        #     device_dict[row["alarm_id"]] = []
        # for key in clusters.keys():
        #     if row["device_id"] i
        # device_dict[row["alarm_id"]].append(row["device_id"])
    for key in device_dict.keys():
        device_dict[key] = set(device_dict[key])
        print(device_dict[key])
        print("\n")
    # print(time_dict)
    # print(device_dict)


if __name__ == '__main__':
    # 补全自身
    # f = open("../phase2/node_dict.json", "r")
    # node_dict = json.load(f)
    # matrix = np.load("../phase2/connectgraph.npy")
    # input(matrix)
    # for key in node_dict.keys():
    #     for node in range(len(node_dict[key])-1):
    #         matrix[int(node_dict[key][node])][int(node_dict[key][node+1])] = 1
    # np.save("../phase2/full.npy", matrix)
    len_ = []
    path = './datasets_phase2/data phase2/'
    for num in range(1, 11):
        alarm_data = pd.read_csv(path + str(num) + '/Alarm.csv', encoding='utf')
        len_.append(max(alarm_data["alarm_id"].values)+1)
        # print(max(alarm_data.iloc[:5000, :]["alarm_id"].values))
    print(len_)
    # 测试长度, 所有数据
    arrs = []
    for i in range(1, 11):
        matrix_ = np.load("./submitnpy/"+str(i)+".npy")
        arrs.append(matrix_)
    arrs_to_csv(arrs, "./submitnpy/0825.csv")
    # check_submit_phase1("../new_submit/0825.csv")
    # get_test(1)
    # print(np.sum(np.load("../new_submit/" + str(1) + '.npy')))
    # # print(np.sum(np.load("../new/" + str(1) + '.npy')))
    # print(np.sum(np.load("../phase2/testing/"+str(11111)+".npy")))
    # print(np.load("../new_submit/" + str(1) + '.npy'))
    # print(np.load("../phase2/testing/"+str(11111)+".npy"))
    # print(np.load("../new_submit/" + str(1) + '.npy') == np.load("../phase2/testing/"+str(11111)+".npy"))
    # data_eda(1)
    # matrix_list = get_test(1)
    # final = matrix_list[0]
    # for matrix in range(1, len(matrix_list)):
    #     print(matrix_list[matrix])
    #     final += matrix_list[matrix]
    # final[final > 0] = 1
    # print(final)
    # print(np.sum(final))
    # np.save("../phase2/all.npy", final)
    # print(np.load("D:/Study/code/python_study/python_/PCIC/phase2/testing/1_notopo_5000_0.01_1.npy"))
    # input(np.load("../new/1_prior.npy"))



