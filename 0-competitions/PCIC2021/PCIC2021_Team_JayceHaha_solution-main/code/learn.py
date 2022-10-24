import os
from distutils import dir_util

import pandas as pd
import numpy as np
# from scipy.stats.stats import pearsonr

from loguru import logger
import utils
from causal_effect import learn_effect


DATASET_BASE_PATH = "./datasets_phase1_update/datasets_release/"
DATA_IDS_WITH_TOPOLOGY = [2, 4, 5, 8, 12, 13, 17, 19]
DATA_IDS_WITHOUT_TOPOLOGY = [1, 3, 6, 7, 9, 10, 11, 14, 15, 16, 18, 20]
# DATA_IDS_WITH_TRUE_DAG = [1, 2, 3, 4]
NUM_DATA_IDS_PHASE1 = 20


DATASET_PHASE2_PATH = "datasets_phase2/"
NUM_DATA_IDS_PHASE2 = 10


def learn_pc(
    data_id: int,
    win_size=12,
    clip_stats=True,
    data_basepath=DATASET_BASE_PATH
):
    from castle.metrics import MetricsDAG
    from custom_independence_tests import CI_Test
    from custom_pc import PC
    from custom_pc import FindSkeleton

    # alarm_data, columns: alarm_id, device_id, start_timestamp, end_timestamp
    alarm_data, topology_matrix, true_causal_matrix = utils.load_data(data_id, data_basepath=data_basepath)
    # true_skeleton_matrix = utils.get_skeleton_from_dag(true_causal_matrix)
    # print(true_causal_matrix)
    logger.info("Load data done, columns: {}, shape: {}", alarm_data.columns.values, alarm_data.shape)
    # print(alarm_data[:10])

    event_ids = sorted(alarm_data["alarm_id"].unique())
    num_events = len(event_ids)
    # print("event_ids:", event_ids, "num_events:", num_events)

    # alarm_id onehot
    alarm_onehot_df = pd.get_dummies(alarm_data["alarm_id"], prefix="e", columns=["alarm_id"])
    logger.info("alarm_onehot_df, columns: {}", alarm_onehot_df.columns.values)
    # print(alarm_onehot_df[:10])

    # # check corr
    # print(alarm_onehot_df.corr())

    delta_index = win_size
    data_onehot = alarm_onehot_df.values
    # print(data_onehot.shape)
    # print(data_onehot[:10])

    # apply sliding window
    data_view = np.lib.stride_tricks.sliding_window_view(data_onehot, delta_index, axis=0)
    # print(data_view.shape)
    # print("data_view[0]:")
    # print(data_view[0])

    # sum over the sliding window
    data_final = np.sum(data_view[:, :, 1:], axis=-1)
    # print(data_final.shape)
    # print("data_final[:10]:")
    # print(data_final[:10])

    if clip_stats:
        data_final_clipped = np.clip(data_final, a_min=0, a_max=1)
    else:
        data_final_clipped = data_final

    # # check corr
    # print(pd.DataFrame(data_final_clipped).corr())
    # print(pd.DataFrame(data_final).corr())
    # print(utils.convert_graph_to_readable_text(true_causal_matrix))

    # gauss ci_test, k: 10, i-j: 4, 12
    i, j = 4, 12
    ctrl_var = [0, 1, 2, 3, 5, 6, 7, 8, 9, 10]
    p_value = CI_Test.gauss_test(data_final, i, j, ctrl_var)
    print("############### p_value:", p_value)

    # gauss ci_test, k: 11, i-j: 4, 12
    i, j = 4, 12
    ctrl_var = [0, 1, 2, 3, 5, 6, 7, 8, 9, 10, 11]
    p_value = CI_Test.gauss_test(data_final, i, j, ctrl_var)

    skeleton, sep_set = FindSkeleton.origin_pc(data_final, max_k=3)
    filename = f"skeleton_{data_id}.npy"
    np.save(filename, skeleton)
    logger.info("Got skeleton:\n{}", skeleton)
    logger.info("Got dsep_set:\n{}", sep_set)
    print(utils.convert_graph_to_readable_text(skeleton))

    utils.plot_causal_graph(skeleton, f"skeleton_{data_id}")

    # pc = PC()
    # pc.learn(data_final)

    # GraphDAG(pc.causal_matrix, true_dag, 'result_pc')
    # met = MetricsDAG(pc.causal_matrix, true_causal_matrix)
    # print(met.metrics)


def learn_ttpm(
    data_id: int,
    delta=0.1,
    epsilon=1.0,
    max_iter=20,
    penalty="BIC",
    possiable_max_hop=0,
    save_prefix="est_dag",
    use_dag_by_effect=True,
    data_basepath=DATASET_PHASE2_PATH
):
    from castle.metrics import MetricsDAG
    from custom_ttpm import TTPM

    save_path = "{}_m{}_d{:02d}_ep{:02d}".format(save_prefix, max_iter, int(delta*100), int(epsilon*10))
    dir_util.mkpath(save_path)
    logger.info("delta: {}, epsilon: {}, save_path: {}", delta, epsilon, save_path)

    # alarm_data, columns: alarm_id, device_id, start_timestamp, end_timestamp
    alarm_data, topology_matrix, true_causal_matrix = utils.load_data(data_id, data_basepath=data_basepath)
    logger.info("Load data-{} done, columns: {}, shape: {}", data_id, alarm_data.columns.values, alarm_data.shape)
    # print(alarm_data.max())

    if topology_matrix is None:
        logger.warning("non topology_matrix!")
    else:
        logger.warning("has topology_matrix!")

    # Data preprocessing and causal structure learning
    X = alarm_data.iloc[:,0:3]
    X.columns = ['event', 'node', 'timestamp']
    X = X.reindex(columns=['event', 'timestamp', 'node'])

    # causal structure learning using TTPM
    max_hop = possiable_max_hop if topology_matrix is not None else 0
    if topology_matrix is None:
        num_devices = len(alarm_data["device_id"].unique())
        topology_matrix = np.zeros((num_devices, num_devices))

    ttpm = TTPM(
        topology_matrix,
        delta=delta,
        epsilon=epsilon,
        max_hop=max_hop,
        max_iter=max_iter,
        penalty=penalty,
        true_dag=true_causal_matrix,
        data_id=data_id,
        save_path=save_path
    )

    if use_dag_by_effect:
        effect_matrix, dags, (est_intial_dag, candidate_edges) = learn_effect(
            data_id,
            win_size=16,
            by_effe_std=1.6,
            by_effe_sort=0.24,
            by_time_avg_sort=0.10,
            by_time_std_sort=0.10,
            initial_dag_ratio=0.08,
            clip_stats=False,
            data_basepath=data_basepath,
            true_dag=true_causal_matrix,
        )
        est_dag_calibrated, est_dag_filtered, est_dag_no_loop, est_dag_by_sort, est_dag_by_std, dag_by_avg_effect_time, dag_by_std_effect_time = dags

        logger.info("Got est_intial_dag with {} edges:", np.sum(est_intial_dag))
        if true_causal_matrix is not None:
            utils.print_graphs(true_causal_matrix, est_intial_dag, est_intial_dag - true_causal_matrix)
        else:
            utils.print_graphs(est_intial_dag)

        logger.info("Got {} candidate_edges: {}", len(candidate_edges), candidate_edges)
        if true_causal_matrix is not None:
            utils.print_graphs(true_causal_matrix, est_dag_filtered, est_dag_filtered - true_causal_matrix)
        else:
            utils.print_graphs(est_dag_filtered)

        logger.info("Will train data-{}, max_hop: {}, max_iter: {}, datalen: {}", data_id, max_hop, max_iter, len(X))
        ttpm.learn(X, candidate_edges=candidate_edges, initial_dag=est_intial_dag)
        logger.info("Train ttmp done, data-{}", data_id)
    else:
        logger.info("Will train data-{}, max_hop: {}, max_iter: {}, datalen: {}", data_id, max_hop, max_iter, len(X))
        ttpm.learn(X)
        logger.info("Train ttmp done, data-{}", data_id)


def evalate_DAG(data_id):
    from castle.metrics import MetricsDAG

    est_causal_matrix = np.load(f"est_causal_matrix_{data_id}.npy")

    data_path = os.path.join(DATASET_BASE_PATH, str(data_id))
    true_causal_matrix = np.load(os.path.join(data_path, "DAG.npy"))
    # calculate g-score
    g_score = MetricsDAG(est_causal_matrix, true_causal_matrix).metrics['gscore']
    # about 0.8889
    logger.info("g_score: {}", g_score)


def calculate_effection_time(data_id: int, alarm_data: pd.DataFrame, true_causal_matrix: np.ndarray):
    # alarm_data, columns: alarm_id, device_id, start_timestamp, end_timestamp
    alarm_ids = sorted(alarm_data["alarm_id"].unique())
    num_nodes = len(true_causal_matrix)
    assert len(alarm_ids) == num_nodes

    logger.info("{} num_nodes: {}", num_nodes, alarm_ids)
    logger.info("true_causal_matrix:\n{}", true_causal_matrix.astype(np.int32))

    dag_edges = np.nonzero(true_causal_matrix)
    dag_edges = list(zip(*dag_edges))
    logger.info("dag_edges:\n{}", dag_edges)

    # duration
    alarm_data["duration"] = alarm_data["end_timestamp"] - alarm_data["start_timestamp"]

    # # alarm_id, device_id onehot
    # alarm_onehot_df = pd.get_dummies(alarm_data[["alarm_id", "device_id"]], prefix=["n", "d"], columns=["alarm_id", "device_id"])
    # logger.info("alarm_onehot_df, columns: {}", alarm_onehot_df.columns.values)
    # print(alarm_onehot_df[:10])
    # print(alarm_onehot_df.corr())

    # number of each kinds of alarm
    # print(alarm_data.groupby("alarm_id").agg(["count", "mean"]))
    print(alarm_data.groupby("alarm_id").agg(["count", "mean"])[["device_id", "duration"]])

    # interval between events
    start_timestamps = alarm_data["start_timestamp"]
    a = start_timestamps[1:].reset_index(drop=True)
    b = start_timestamps[:-1].reset_index(drop=True)
    delta_start_time = a - b
    print(delta_start_time[:10])
    print(delta_start_time.describe())

    # observe
    effect = 1
    selected_rows = alarm_data[alarm_data["alarm_id"] == effect]
    print(selected_rows.describe())

    data_array = alarm_data.values
    logger.info(data_array.shape)

    causes_dict = {j: set([i for i in alarm_ids if true_causal_matrix[i, j] !=  0]) for j in alarm_ids}
    logger.info("causes_dict: {}", causes_dict)

    non_root_alarm_ids = np.sum(true_causal_matrix, axis=0).nonzero()[0]
    logger.info("non_root_alarm_ids: {}", non_root_alarm_ids)

    for effect in non_root_alarm_ids:
        logger.info("effect: {}, causes: {}", effect, causes_dict[effect])
        selected_data = alarm_data[alarm_data["alarm_id"].isin([effect, *causes_dict[effect]])].reset_index()

        delta_time = selected_data["start_timestamp"].diff()
        delta_index = selected_data["index"].diff()
        has_cause = selected_data["alarm_id"].diff() != 0
        is_cause_ended = selected_data["end_timestamp"].iloc[:-1].values < selected_data["start_timestamp"].iloc[1:].values
        print(is_cause_ended[:10])
        # print(selected_data["end_timestamp"][1:])
        # print(selected_data["start_timestamp"][:-1])

        selected_data["delta_time"] = delta_time
        selected_data["delta_index"] = delta_index
        selected_data["has_cause"] = has_cause.astype(np.int32)
        # drop the first row
        selected_data = selected_data.iloc[1:]
        selected_data["is_cause_ended"] = is_cause_ended.astype(np.int32)
        print(selected_data[:10])

        selected_deltas = selected_data[(selected_data["alarm_id"] == effect) & (selected_data["has_cause"] == True)]
        print(selected_deltas[:10])

        selected_deltas = selected_deltas[["duration", "delta_time", "delta_index", "is_cause_ended"]]
        print(selected_deltas.describe())

        axes = selected_deltas.hist()
        axes[0, 0].figure.savefig(f"data_{data_id}_effect_{effect}.png")


def learn_all_by_ttpm():
    # for data_id in range(1, NUM_DATA_IDS_PHASE1+1):
    for data_id in [1, 2, 3, 4]:
        learn_ttpm(
            data_id,
            delta=0.02,
            epsilon=2.0,
            max_iter=40,
            penalty="BIC",
            possiable_max_hop=2,
            use_dag_by_effect=True,
            save_prefix="presentation",
            data_basepath=DATASET_BASE_PATH,
        )


def load_est_dag(est_dag_path, best_iter_dict):
    est_dag_dict = dict()
    max_alarm_ids = [23, 24, 14, 16, 16, 18, 19, 19, 21, 21]
    mat_shapes_phase1 = [n+1 for n in max_alarm_ids]
    for dt_idx in range(NUM_DATA_IDS_PHASE1+1):
        if dt_idx not in best_iter_dict:
            continue
        best_iter = best_iter_dict.get(dt_idx)

        dag_file = os.path.join(est_dag_path, f"est_dag_data_{dt_idx}_iter_{best_iter}.npy")
        est_dag_org = np.load(dag_file).astype(np.int32)
        est_dag_org = utils.remove_diagnal_entries(est_dag_org)
        true_shape = mat_shapes_phase1[dt_idx - 1]
        assert est_dag_org.shape[0] == true_shape, f"shape not equal, dt: {dt_idx}, should: {true_shape}, got: {est_dag_org.shape[0]}"
        est_dag_dict[dt_idx] = est_dag_org
    return est_dag_dict


def check_difference():
    # # phase 2
    # best_iters_phase2_m65_d02 = {1: 44, 2: 46, 3: 41, 4: 33, 5: 52, 6: 46, 7: 58, 8: 47, 9: 46, 10: 50 }
    # best_iters_phase2_m65_d02 = {1: 44, 2: 58, 3: 41, 4: 33, 5: 52, 7: 58, 8: 47, 9: 46, 10: 51}
    # best_iters_phase2_m65_d01 = {1: 50, 2: 57, 3: 41, 4: 33, 5: 52, 7: 57, 8: 48, 9: 46, 10: 51}
    m65_d02_ep20 = {1: 44, 2: 46, 3: 41, 4: 33, 5: 52, 9: 46}
    m65_d02_ep40 = {1: 48, 2: 49, 3: 41, 4: 33, 5: 52, 9: 46}
    print_differences("est_dag2_m65_d02_ep20", m65_d02_ep20, "est_dag2_m65_d02_ep40", m65_d02_ep40)


def try_explore(dt_idx):
    # load dags
    dags_path_a = "est_dag2_m65_d02_ep20"
    dags_path_b = "est_dag2_m65_d01_ep20"

    d02_dags = list()
    for i in range(44, 64):
        d02_dags.append(load_est_dag(dags_path_a, {dt_idx: i})[dt_idx])
    d01_dags = list()
    for i in range(50, 61):
        d01_dags.append(load_est_dag(dags_path_b, {dt_idx: i})[dt_idx])

    base = d02_dags[0]
    d02_last = d02_dags[-1]
    d01_last = d01_dags[-1]

    skeleton_text_a = utils.convert_graph_to_readable_text(base)
    skeleton_text_b = utils.convert_graph_to_readable_text(d02_last)
    skeleton_text_c = utils.convert_graph_to_readable_text(d01_last)
    delta02 = d02_last - base
    delta01 = d01_last - base
    skeleton_text_delta02 = utils.convert_graph_to_readable_text(delta02)
    skeleton_text_delta01 = utils.convert_graph_to_readable_text(delta01)
    utils.print_graph_text(skeleton_text_a, skeleton_text_b, skeleton_text_delta02)
    utils.print_graph_text(skeleton_text_a, skeleton_text_c, skeleton_text_delta01)
    # utils.print_graph_text(skeleton_text_a, skeleton_text_b, skeleton_text_c, skeleton_text_delta02, skeleton_text_delta01)

    n02 = np.nonzero(delta02)
    n01 = np.nonzero(delta01)
    print(n02)
    print(n01)
    s02 = {(i, j) for i, j in zip(*n02)}
    s01 = {(i, j) for i, j in zip(*n01)}
    for s in s02:
        if s in s01:
            print(s)

    # remove deltas
    base_rm =  np.copy(base)
    print("ha?", delta01)
    base_rm[delta01 == -1] = 0
    text_base_rm = utils.convert_graph_to_readable_text(base_rm)
    text_base_rm_delta = utils.convert_graph_to_readable_text(base_rm - base)
    utils.print_graph_text(skeleton_text_a, text_base_rm, text_base_rm_delta)
    print(f"dt_{dt_idx} = {base_rm.reshape(-1).tolist()}")


def print_differences(dags_path_a, best_iters_a, dags_path_b, best_iters_b):
    # load dags
    dags_dict_a = load_est_dag(dags_path_a, best_iters_a)
    dags_dict_b = load_est_dag(dags_path_b, best_iters_b)
    print("ha?", dags_dict_a.keys(), dags_dict_b.keys())
    for dt_idx in dags_dict_a:
        # plot and compare dag
        dag_a = dags_dict_a[dt_idx]
        dag_b = dags_dict_b[dt_idx]
        dag_delta = dag_b - dag_a
        skeleton_text_a = utils.convert_graph_to_readable_text(dag_a)
        skeleton_text_b = utils.convert_graph_to_readable_text(dag_b)
        skeleton_text_delta = utils.convert_graph_to_readable_text(dag_delta)
        utils.print_graph_text(skeleton_text_a, skeleton_text_b, skeleton_text_delta)

        # plot the number of edges
        t40 = np.mean(dag_a)
        t65 = np.mean(dag_b)
        tot_a = np.sum(dag_a)
        tot_b = np.sum(dag_b)
        print("## dt: {}, a-b-delta, {:.2f}:{:.2f}, {}:{}, ratio: {:.2f}".format(dt_idx, t40, t65, tot_a, tot_b, t65/t40))

        # load eval result
        eval_result_a = np.load(os.path.join(dags_path_a, f"eval_result_{dt_idx}.npy"))
        eval_result_b = np.load(os.path.join(dags_path_b, f"eval_result_{dt_idx}.npy"))
        b40 = best_iters_a[dt_idx]
        lh_a, mean_edges_a = eval_result_a[b40, 1], eval_result_a[b40, 2]
        b65 = best_iters_b[dt_idx]
        lh_b, mean_edges_b = eval_result_b[b65, 1], eval_result_b[b65, 2]

        print("## dt: {}, a-b-delta, {:.2f}:{:.2f}, {:.2f}:{:.2f}, ratio: {:.2f}".format(
            dt_idx, lh_a, lh_b, mean_edges_a, mean_edges_b, mean_edges_b/mean_edges_a))


def main_test(data_id):
    # alarm_data, columns: alarm_id, device_id, start_timestamp, end_timestamp
    alarm_data, topology_matrix, true_causal_matrix = utils.load_data(data_id, data_basepath=DATASET_BASE_PATH)
    true_skeleton = utils.get_skeleton_from_dag(true_causal_matrix)

    skeleton = np.load(f"skeleton_{data_id}.npy")
    logger.info("Loaded skeleton: {}\n{}", skeleton.shape, skeleton)

    marked_skeleton = utils.markout_positive_graph(skeleton, true_skeleton)

    true_dag_text = utils.convert_graph_to_readable_text(true_causal_matrix)
    true_ske_text = utils.convert_graph_to_readable_text(true_skeleton)
    skeleton_text = utils.convert_graph_to_readable_text(skeleton)
    marked_ske_text = utils.convert_graph_to_readable_text(marked_skeleton)
    utils.print_graph_text(marked_ske_text, skeleton_text, true_ske_text, true_dag_text)


def analysis(dt_idx, best_iter=None, result_path="est_dag_d02_ep20", data_basepath=DATASET_BASE_PATH):
    _, _, true_dag = utils.load_data(dt_idx, data_basepath=data_basepath)

    effect_matrix, dags, (est_intial_dag, candidate_edges) = learn_effect(
        dt_idx,
        win_size=8,
        by_effe_std=1.6,
        by_effe_sort=0.24,
        by_time_avg_sort=0.20,
        by_time_std_sort=0.20,
        initial_dag_ratio=0.08,
        clip_stats=False,
        data_basepath=data_basepath,
        true_dag=true_dag,
    )
    est_dag_calibrated, est_dag_filtered, est_dag_no_loop, est_dag_by_sort, est_dag_by_std, dag_by_avg_effect_time, dag_by_std_effect_time = dags
    utils.plot_causal_graph(est_dag_by_sort, effect_matrix, savefig=f"phase1_dt{dt_idx}_est_dag_by_sort")
    utils.plot_causal_graph(est_dag_by_sort, effect_matrix, savefig=f"phase1_dt{dt_idx}_est_dag_calibrated")

    # est_dag_no_loop = utils.remove_loop_edges(np.ones_like(est_dag_by_sort) , effect_matrix)
    utils.plot_causal_graph(est_dag_no_loop, effect_matrix, savefig=f"phase1_dt{dt_idx}_est_dag_no_loop")

    def compare_dag(dag_ref, dag_check):
        print("total num, dag_check: {}/{}, ratio: {:.2f}, dag_ref: {}, lack: {}".format(
            np.sum(dag_check), len(dag_check)**2, np.sum(dag_check) / len(dag_ref)**2, np.sum(dag_ref), np.sum((dag_check - dag_ref)==-1)
        ))
        row_idxs, col_idxs = np.nonzero(dag_ref)
        true_edge_delta_effects = effect_matrix[row_idxs, col_idxs]
        indexs = np.argsort(true_edge_delta_effects)[::-1]
        print("#### selected out edges effect delta:")
        utils.print_vector(row_idxs[indexs], col_idxs[indexs], true_edge_delta_effects[indexs])

        row_idxs, col_idxs = np.nonzero(dag_check - dag_ref)
        extra_delta_effects = effect_matrix[row_idxs, col_idxs]
        indexs = np.argsort(extra_delta_effects)[::-1]
        print("#### extra edges delta effects:")
        utils.print_vector(row_idxs[indexs], col_idxs[indexs], extra_delta_effects[indexs])

    if best_iter is not None:
        est_dag_ttpm = utils.load_ttpm_result(result_path, dt_idx, best_iter)
    else:
        est_dag_ttpm = None

    if true_dag is not None:
        if est_dag_ttpm is not None:
            utils.print_graphs(true_dag, est_dag_by_std, est_dag_by_std - true_dag, est_dag_ttpm, est_dag_ttpm - true_dag)
        utils.print_graphs(true_dag, est_dag_by_std, est_dag_by_std - true_dag, est_dag_by_sort, est_dag_by_sort - true_dag)
        utils.print_graphs(true_dag, est_dag_no_loop, est_dag_no_loop - true_dag, est_dag_filtered, est_dag_filtered -true_dag)
        utils.print_graphs(true_dag, est_intial_dag, est_intial_dag - true_dag, est_dag_calibrated, est_dag_calibrated - true_dag)
        # utils.print_graphs(true_dag, dag_by_avg_effect_time, dag_by_avg_effect_time - true_dag, dag_by_std_effect_time, dag_by_std_effect_time - true_dag)
        # utils.print_graphs(est_dag_by_std, dag_by_avg_effect_time, dag_by_avg_effect_time - est_dag_by_std, dag_by_std_effect_time, dag_by_std_effect_time - est_dag_by_std)
        # utils.print_graphs(est_dag_by_sort, dag_by_avg_effect_time, dag_by_avg_effect_time - est_dag_by_sort, dag_by_std_effect_time, dag_by_std_effect_time - est_dag_by_sort)

        # inner_and_dag =  dag_by_avg_effect_time * est_dag_by_sort
        # union_or_dag = np.clip((est_dag_by_std + dag_by_avg_effect_time + est_dag_by_sort), 0, 1)
        # utils.print_graphs(true_dag, inner_and_dag, inner_and_dag - true_dag, union_or_dag, union_or_dag - true_dag)

        # utils.print_graphs(true_dag, dag_combine, dag_combine - true_dag)
    elif est_dag_ttpm is not None:
        print("different with ttpm, dt:", dt_idx)
        utils.print_graphs(est_dag_ttpm, est_dag_by_std, est_dag_by_std - est_dag_ttpm)
        utils.print_graphs(est_dag_ttpm, est_dag_by_sort, est_dag_by_sort - est_dag_ttpm)
        utils.print_graphs(est_dag_ttpm, est_intial_dag, est_intial_dag - est_dag_ttpm)
        compare_dag(est_dag_ttpm, est_dag_by_std)


def main_analysis(phase=1):
    if phase == 1:
        best_iter_submit5_d02_ep20 = {5: 11, 6: 8, 7: 34, 8: 21, 9: 10, 10: 36, 11: 23, 14: 35, 15: 26, 16: 39, 18: 24}
        for dt_idx, best_iter in best_iter_submit5_d02_ep20.items():
            analysis(dt_idx, best_iter, result_path="est_dag_d02_ep20", data_basepath=DATASET_BASE_PATH)
            break
    else:
        best_iters_phase2_m65 = { 1: 44, 2: 46, 3: 41, 4: 33, 5: 52, 6: 41, 7: 58, 8: 47, 9: 46, 10: 50}
        for dt_idx, best_iter in best_iters_phase2_m65.items():
            analysis(dt_idx, best_iter, "est_dag2_m65_d02_ep20", DATASET_PHASE2_PATH)


if __name__ == "__main__":

    # # check causal effection time
    # dt_idx = 3
    # alarm_data, topology_matrix, true_causal_matrix = utils.load_data(dt_idx, data_basepath=DATASET_BASE_PATH)
    # calculate_effection_time(dt_idx, alarm_data, true_causal_matrix)
    # utils.plot_causal_graph(true_causal_matrix, savefig=f"phase1_dt{dt_idx}_true_dag")

    # main_test(4)
    # check_difference()
    # try_explore(1)
    # learn_pc(4, win_size=16, clip_stats=False)
    # analysis(1, 10)
    # analysis(2, 17)
    # analysis(3, 16)
    # analysis(4, 21)
    # analysis(1)
    # analysis(2)
    # analysis(3)
    # analysis(4)
    # main_analysis(phase=2)
    learn_all_by_ttpm()
    # evalate_DAG(2)

