import os
import glob

import matplotlib
matplotlib.use("agg")

import matplotlib.pyplot as plt
import numpy as np

import utils


DATA_IDS_WITH_TOPOLOGY = [2, 4, 5, 8, 12, 13, 17, 19]
DATA_IDS_WITHOUT_TOPOLOGY = [1, 3, 6, 7, 9, 10, 11, 14, 15, 16, 18, 20]
# DATA_IDS_WITH_TOPOLOGY = [1, 2, 6, 7, 8, 10]
# DATA_IDS_WITHOUT_TOPOLOGY = [3, 4, 5, 9]
NUM_DATA_IDS = 11


def plot_data_ext(est_dag_path):
    eval_results = list()
    eval_names = list()

    dt_list = list()
    filenames = glob.glob(os.path.join(est_dag_path, f"eval_result_*.npy"))
    filenames = sorted(filenames, key=lambda x: int(x[:-len(".npy")].split("_")[-1]))
    for filename in filenames:
        dt_idx = int(filename[:-len(".npy")].split("_")[-1])
        # print(filename, dt_idx)
        eval_results.append(np.load(filename))
        has_topo = "non" if dt_idx in DATA_IDS_WITHOUT_TOPOLOGY else "has"
        eval_names.append(f"dt{dt_idx}_{has_topo}_topo")
        dt_list.append(dt_idx)

    assert len(eval_results) == len(eval_names)

    items = est_dag_path.split("_")
    prefix = "{}_{}_{}".format(items[2], items[3], "_".join([str(dt_idx) for dt_idx in dt_list]))
    plot_likelihoods_ext(prefix, eval_results, eval_names)


def plot_likelihoods_ext(prefix, eval_results, dt_names):
    fig, axes = plt.subplots(nrows=len(eval_results), figsize=(8, len(eval_results)*4))
    fig.subplots_adjust(left=0.15, right=0.6)

    if len(eval_results) == 1:
        axes = [axes]

    # pair = [num_iter, likelihood, mean_edges, g_score]
    # pair = [num_iter, likelihood, mean_edges]
    for eval_result, name, ax in zip(eval_results, dt_names, axes):
        lh, mean_edges = eval_result[:, 1], eval_result[:, 2]
        if eval_result.shape[1] == 4:
            gs = eval_result[:, 3]
        else:
            gs = None
        plot_one_data(ax, lh, gs, name, mean_edges=mean_edges)

    fig.tight_layout()
    # filename = f"{prefix}_{['non', 'has'][int(has_topo)]}_topo.png"
    filename = f"{prefix}.png"
    fig.savefig(filename)
    print("Save file:", filename)


def plot_one_data(ax, lh, gs=None, name="", mean_edges=None):
    xs = np.arange(len(lh))
    lh_g1 = lh[1:] - lh[:-1]
    lh_g2 = lh_g1[1:] - lh_g1[:-1]

    p0, = ax.plot(xs, lh, "b-", label="likelihood")

    xticks = np.arange(0, len(lh) + 4, 4)
    minor_xticks = np.arange(0, len(lh) + 2, 2)
    ax.set_xticks(xticks)
    ax.set_xticks(minor_xticks, minor = True)

    ax.xaxis.grid(True, which='both', linestyle="--", linewidth=0.5)
    ax.yaxis.label.set_color(p0.get_color())
    ax.scatter(xs, lh, s=4)
    ax.set_xlabel("iteration")
    ax.set_ylabel("likelihood")
    ax.set_title(name)

    # Adding Twin Axes to plot using dataset_2
    ax_g1 = ax.twinx() 
    ax_g1.set_ylabel("gradient-1")
    p1, = ax_g1.plot(xs[1:], lh_g1, "r-", label="lh_gradient1")
    ax_g1.yaxis.label.set_color(p1.get_color())

    y_pos = 1.3
    ax_g2 = ax.twinx() 
    ax_g2.spines.right.set_position(("axes", y_pos))
    ax_g2.set_ylabel("gradient-2")
    p2, = ax_g2.plot(xs[2:], lh_g2, "g-", label="lh_gradient2")
    ax_g2.yaxis.label.set_color(p2.get_color())

    handles = [p0, p1, p2]

    if mean_edges is not None:
        # Add ploting mean edges
        y_pos += 0.3
        ax_ne = ax.twinx() 
        yticks = np.arange(0, (np.max(mean_edges) // 0.01 + 2) * 0.01, 0.01)
        ax_ne.set_yticks(yticks)
        ax_ne.yaxis.grid(True, which='both', linestyle="--", linewidth=0.5)
        ax_ne.set_ylabel("mean_edges")
        ax_ne.spines.right.set_position(("axes", y_pos))
        p_ne, = ax_ne.plot(mean_edges, "c-", linewidth=0.5, label="mean_edges")
        ax_ne.scatter(np.arange(len(mean_edges)), mean_edges, s=4)
        ax_ne.yaxis.label.set_color(p_ne.get_color())
        handles.append(p_ne)

    if gs is not None:
        y_pos += 0.3
        ax_gs = ax.twinx() 
        ax_gs.spines.right.set_position(("axes", y_pos))
        ax_gs.set_ylabel("g-score")
        p_gs, = ax_gs.plot(xs, gs, "k", label="g-score")
        ax_gs.yaxis.label.set_color(p_gs.get_color())
        ax_gs.scatter(xs, gs, s=4)

    ax.legend(handles=handles)


def get_est_dags(est_dag_path="est_dag"):
    filenames = os.listdir(est_dag_path)
    dag_dict = dict()
    # name example: est_dag_data_16_iter_9.npy
    for name in filenames:
        if not name.startswith("est_dag_data"):
            continue
        est_dag = np.load(os.path.join(est_dag_path, name)).astype(np.int32)
        items = name[:-len(".npy")].split("_")
        dt_idx, iter_num = int(items[3]), int(items[5])
        if dt_idx not in dag_dict:
            dag_dict[dt_idx] = list()
        dag_dict[dt_idx].append((iter_num, est_dag))

    for dt_idx in range(1, 21):
        pairs = dag_dict[dt_idx]
        # print("dt: {}, pairs: {}".format(dt_idx, [(iter_num, dag.shape) for iter_num, dag in pairs]))
        dag_dict[dt_idx] = sorted(pairs)
        iter_nums = [pair[0] for pair in dag_dict[dt_idx]]
        mean_edges = [np.mean(pair[1]) for pair in dag_dict[dt_idx]]
        # print("dt-{}, num_iters: {}, iter_nums: {}, mean_edges: {}".format(dt_idx, len(iter_nums), iter_nums, mean_edges))
        print("\"dt-{}\": {},".format(dt_idx, mean_edges))

    return dag_dict


def load_and_print_est_dag(est_dag_path, best_iter_dict):
    ## this is used for constructing dags with right shapes
    # mat_shapes_phase1 = [10, 11, 12, 13, 13, 14, 15, 16, 17, 18, 13, 20, 21, 16, 18, 24, 25, 26, 27, 29]
    est_dag_dict = dict()
    max_alarm_ids = [23, 24, 14, 16, 16, 18, 19, 19, 21, 21]
    mat_shapes_phase1 = [n+1 for n in max_alarm_ids]
    for dt_idx in range(NUM_DATA_IDS):
        if dt_idx not in best_iter_dict:
            continue
        best_iter = best_iter_dict.get(dt_idx)

        dag_file = os.path.join(est_dag_path, f"est_dag_data_{dt_idx}_iter_{best_iter}.npy")
        est_dag_org = np.load(dag_file).astype(np.int32)
        est_dag = utils.remove_diagnal_entries(est_dag_org)
        true_shape = mat_shapes_phase1[dt_idx - 1]
        # has_topo = "has_topo" if dt_idx in DATA_IDS_WITH_TOPOLOGY else "non_topo"
        # print("dt-{:02d}".format(dt_idx), "iter: {:02d}".format(best_iter), has_topo, true_shape, est_dag.shape, np.mean(est_dag))
        assert est_dag.shape[0] == true_shape, f"shape not equal, dt: {dt_idx}, should: {true_shape}, got: {est_dag.shape[0]}"
        print(f"dt_{dt_idx} = {est_dag.reshape(-1).tolist()}")
        est_dag_dict[dt_idx] = est_dag_org
    return est_dag_dict


def create_submit(est_dag_path):
    best_iters_phase2_m65_d01 = {3:41, 4: 31, 5: 52, 9:46, 10: 51}
    load_and_print_est_dag(est_dag_path, best_iters_phase2_m65_d01)


def print_dag_list(est_dag_path):
    # phase 2
    best_iters_phase2_m40 = { 1: 38, 2: 38, 3: 39, 4: 33, 5: 39, 6: 39, 7: 39, 8: 39, 9: 39, 10: 39 }
    best_iters_phase2_m65_t0 = { 1: 44, 2: 46, 3: 41, 4: 33, 5: 52, 6: 33, 7: 58, 8: 47, 9: 46, 10: 50 }
    best_iters_phase2_m65_t2 = {
        # 1: 64,
        # 2: 58,
        # 8: 48,
        # 10: 54
        6: 41 # -- highest, 0.80
        # 6: 46 --> bad, drop to 0.7965
    }

    best_iters_phase2_m65_d01_t0 = {3:41, 4: 31, 5: 52, 9:46, 10: 51}
    best_iters_phase2_m65_d01_t1 = {1: 50, 2: 57, 8: 48, 10: 51}

    best_iters_phase2_m65_d02_ep40 = {1: 48, 2: 49}

    load_and_print_est_dag(est_dag_path, best_iters_phase2_m65_d02_ep40)


if __name__ == "__main__":

    # create_submit("est_dag")
    # create_submit("est_dag_try3")
    # get_est_dags()
    # plot_data_ext("est_dag_try3")
    # plot_data_ext("est_dag_try4")
    # plot_data_ext("est_dag_d02_ep20")
    # create_submit("est_dag_d02_ep20")
    # plot_data_ext("est_dag2_try0_d02_ep20")
    # plot_data_ext("est_dag2_m65_d02_ep20")
    # plot_data_ext("est_dag2_m65_d01_ep20")
    # plot_data_ext("est_dag2_m65_d02_ep40")
    plot_data_ext("presentation_m40_d10_ep10")
    # plot_data_ext("presentation_m40_d02_ep10")
    # plot_data_ext("presentation_m40_d10_ep40")
    # plot_data_ext("presentation_m40_d02_ep40")
    # plot_data_ext("presentation_m40_d02_ep20")
    # plot_data_ext("presentation_m40_d01_ep10")
    # plot_data_ext("presentation_m40_d02_ep10")

    # create_submit("est_dag2_try0_d02_ep20")
    # create_submit("est_dag2_m65_d02_ep20")
    # create_submit("est_dag2_m65_d01_ep20")
    # print_dag_list("est_dag2_m65_d02_ep20")
    # print_dag_list("est_dag2_m65_d01_ep20")
    # print_dag_list("est_dag2_m65_d02_ep40")
