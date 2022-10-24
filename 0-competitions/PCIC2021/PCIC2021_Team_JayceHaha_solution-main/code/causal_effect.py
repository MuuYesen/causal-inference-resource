import pandas as pd
import numpy as np

from loguru import logger
from custom_independence_tests import CI_Test
import utils


DATASET_BASE_PATH = "./datasets_phase1_update/datasets_release/"
DATASET_PHASE2_PATH = "datasets_phase2/"


def learn_effect(
    data_id: int,
    win_size=12,
    by_effe_std=1.0,
    by_effe_sort=0.20,
    by_time_avg_sort=0.20,
    by_time_std_sort=0.20,
    initial_dag_ratio=0.10,
    clip_stats=True,
    data_basepath=DATASET_BASE_PATH,
    true_dag=None   # for debug
):
    # alarm_data, columns: alarm_id, device_id, start_timestamp, end_timestamp
    alarm_data, topology_matrix, true_causal_matrix = utils.load_data(data_id, data_basepath=data_basepath)
    logger.info("Load data done, columns: {}, shape: {}", alarm_data.columns.values, alarm_data.shape)

    event_ids = sorted(alarm_data["alarm_id"].unique())
    num_events = len(event_ids)
    # print("event_ids:", event_ids, "num_events:", num_events)

    # Get duration
    alarm_data["duration"] = alarm_data["end_timestamp"] - alarm_data["start_timestamp"]
    data_times = alarm_data[["alarm_id", "start_timestamp", "end_timestamp", "duration"]].values

    # alarm_id onehot
    alarm_onehot_df = pd.get_dummies(alarm_data["alarm_id"], prefix="e", columns=["alarm_id"])
    logger.info("alarm_onehot_df, columns: {}", alarm_onehot_df.columns.values)
    # print(alarm_onehot_df[:10])

    delta_index = win_size
    data_onehot = alarm_onehot_df.values
    # print(data_onehot.shape)
    # print(data_onehot[:10])

    # apply sliding window, [N, num_events] --> [N, num_events, win_size]
    data_view = np.lib.stride_tricks.sliding_window_view(data_onehot, delta_index, axis=0)
    print("data_view:", data_view.shape)
    # print(data_view[1])

    data_pos = np.copy(data_view)
    data_pos[data_view == 0] = win_size
    # print(data_pos[1])
    happen_times = np.argmin(data_pos, axis=-1)
    # print(happen_times[1])

    data_counts = np.sum(data_view, axis=-1)
    happen_times[data_counts == 0] = 13
    event_happen_times = happen_times.T
    # print(happen_times[0])
    # print(happen_times[1])

    # sum countings over window, [N, num_events, win_size] -> [N, num_events]
    data_counts = np.sum(data_view, axis=-1)

    # [N, 3] --> [N, 4, win_size]
    times_view = np.lib.stride_tricks.sliding_window_view(data_times, delta_index, axis=0)
    times_alarms = times_view[:, 0, 1:]
    times_deltas = times_view[:, 1:, 1:] - times_view[:, 1:, 0:1]
    # times_deltas = np.log(times_deltas)
    print("times_view.shape: {}, times_alarms.shape: {}, times_deltas.shape: {}".format(
        times_view.shape, times_alarms.shape, times_deltas.shape)
    )

    # sum over the sliding window, [N, num_events, win_size-1] --> [N, num_events]
    data_final = np.sum(data_view[:, :, 1:], axis=-1)
    # clip values
    data_final_clipped = np.clip(data_final, a_min=0, a_max=1)

    if clip_stats:
        data_final_clipped = np.clip(data_final, a_min=0, a_max=1)
    else:
        data_final_clipped = data_final

    effect_matrix_pos = np.zeros((num_events, num_events), dtype=np.float32)
    effect_matrix_neg = np.zeros((num_events, num_events), dtype=np.float32)
    avg_effect_times_pos = np.zeros((num_events, num_events), dtype=np.float32)
    avg_effect_times_neg = np.zeros((num_events, num_events), dtype=np.float32)
    std_effect_times_pos = np.zeros((num_events, num_events), dtype=np.float32)
    std_effect_times_neg = np.zeros((num_events, num_events), dtype=np.float32)

    for i in range(num_events):
        for j in range(num_events):
            if i == j:
                continue
            # samples started with i
            selected_rows = event_happen_times[i] == 0
            selected_data = data_final_clipped[selected_rows]
            effect_matrix_pos[i, j] = np.mean(selected_data[:, j])
            # samples started with not i
            remained_rows = event_happen_times[i] != 0
            remained_data = data_final_clipped[remained_rows]
            effect_matrix_neg[i, j] = np.mean(remained_data[:, j])

            # time stats
            selected_time_deltas = times_deltas[selected_rows]
            window_mask = (times_alarms[selected_rows] == j).astype(np.float32)
            time_stats_sum = np.sum(selected_time_deltas * window_mask[:, np.newaxis, :], axis=-1)
            # print(selected_time_deltas.shape, time_stats_sum.shape)
            effected_times = time_stats_sum[time_stats_sum[:, 0] > 0, 0]
            avg_effect_times_pos[i, j] = np.mean(effected_times)
            std_effect_times_pos[i, j] = np.std(effected_times)

            # time stats
            selected_time_deltas = times_deltas[remained_rows]
            window_mask = (times_alarms[remained_rows] == j).astype(np.float32)
            time_stats_sum = np.sum(selected_time_deltas * window_mask[:, np.newaxis, :], axis=-1)
            effected_times = time_stats_sum[time_stats_sum[:, 0] > 0, 0]
            avg_effect_times_neg[i, j] = np.mean(effected_times)
            std_effect_times_neg[i, j] = np.std(effected_times)

    effect_matrix = effect_matrix_pos - effect_matrix_neg
    avg_effect_times = avg_effect_times_pos - avg_effect_times_neg
    std_effect_times = std_effect_times_pos - std_effect_times_neg

    print("#### avg_effect_times:")
    # dlt_avg_effect_times, avg_avg_effect_times, std_avg_effect_times = utils.get_matrix_avg_std(avg_effect_times) 
    utils.print_matrix(avg_effect_times, ff="{:6.1f}")
    # utils.print_matrix(dlt_avg_effect_times, ff="{:6.1f}")
    dag_by_avg_effect_time = utils.get_dag_by_sort(
        avg_effect_times, ratio=by_time_avg_sort, larger_better=False
    )

    print("#### std_effect_times:")
    # dlt_std_effect_times, avg_std_effect_times, std_std_effect_times = utils.get_matrix_avg_std(std_effect_times) 
    # utils.print_matrix(std_effect_times_pos, ff="{:6.1f}")
    # utils.print_matrix(dlt_std_effect_times, ff="{:6.1f}")
    # utils.print_matrix(std_effect_times, ff="{:6.1f}")
    dag_by_std_effect_time = utils.get_dag_by_sort(
        std_effect_times, ratio=by_time_std_sort, larger_better=False
    )

    print("#### effect_matrix:")
    utils.print_matrix(effect_matrix)
    delta_effect, avg_effect_vec, std_effect_vec = utils.get_matrix_avg_std(effect_matrix) 
    # utils.print_matrix(avg_effect_vec)
    # utils.print_matrix(std_effect_vec)
    # utils.print_matrix(delta_effect)
    est_dag_by_std = (delta_effect > std_effect_vec * by_effe_std).astype(np.int32)
    est_dag_by_sort = utils.get_dag_by_sort(
        effect_matrix, ratio=by_effe_sort, larger_better=True
    )

    est_dag_by_sort_temp = utils.get_dag_by_sort(
        effect_matrix, ratio=0.5, larger_better=True
    )
    est_dag_no_loop = utils.remove_loop_edges(est_dag_by_sort_temp , effect_matrix)
    # est_dag_no_loop = utils.remove_loop_edges(np.ones_like(est_dag_by_sort), effect_matrix)
    est_dag_filtered = est_dag_no_loop * est_dag_by_sort
    # utils.print_graphs(est_dag_no_loop, est_dag_filtered, est_dag_filtered, - est_dag_no_loop)

    # use 'est_dag_filtered' to get candidate edges
    row_idxs, col_idxs = np.nonzero(est_dag_filtered)
    selected_effects = effect_matrix[row_idxs, col_idxs]
    indexs = np.argsort(selected_effects)[::-1]
    # utils.print_vector(row_idxs[indexs], col_idxs[indexs], selected_effects[indexs])
    candidate_edges = list(zip(row_idxs[indexs], col_idxs[indexs]))

    est_intial_dag = np.zeros_like(est_dag_filtered)
    num_intial_edges = min(int(num_events * num_events * initial_dag_ratio), len(candidate_edges))
    for i, j in candidate_edges[:num_intial_edges]:
        est_intial_dag[i, j] = 1

    # conditional independence test
    est_dag_calibrated= np.copy(est_dag_filtered)
    for i, j in candidate_edges:
        common_parent = utils.get_common_parent(est_dag_filtered, (i, j))
        for c in common_parent:
            if (c == i) or (c == j):
                continue
            effect = effect_matrix[i, j]

            #### when c == N
            num_neg = 0
            # y(j|i==1, c==0)
            selected_rows = np.logical_and(event_happen_times[c] != 0, event_happen_times[i] < win_size)
            selected_data = data_final_clipped[selected_rows]
            yji1_cN = np.mean(selected_data[:, j])
            num_i1_cN = len(selected_data)
            # y(j|i==0, c==0)
            selected_rows = np.logical_and(event_happen_times[c] != 0, event_happen_times[i] >= win_size)
            selected_data = data_final_clipped[selected_rows]
            yji0_cN = np.mean(selected_data[:, j])
            num_i0_cN = len(selected_data)
            num_neg += num_i1_cN + num_i0_cN
            print("#### effect: {:.2f}, i: {:2d}, j: {:2d}, c{:02d}=N, yji1_cN: {:.2f}, yji0_cN: {:.2f}, delta: {:5.2f}, num_neg: {} + {} = {}".format(
                    effect, i, j, c, yji1_cN, yji0_cN, yji1_cN - yji0_cN,
                    num_i1_cN, num_i0_cN, num_neg
                )
            )

            #### when c == Y
            # y(j|i==1, c==1)
            selected_rows = np.logical_and(event_happen_times[c] == 0, event_happen_times[i] < win_size)
            selected_data = data_final_clipped[selected_rows]
            yji1_cY = np.mean(selected_data[:, j])
            num_i1_cY = len(selected_data)
            # print("==1:", len(selected_data[:, j]), np.std(selected_data[:, j]))
            # y(j|i==0, c==1)
            selected_rows = np.logical_and(event_happen_times[c] == 0, event_happen_times[i] >= win_size)
            selected_data = data_final_clipped[selected_rows]
            yji0_cY = np.mean(selected_data[:, j])
            num_i0_cY = len(selected_data)
            num_pos = num_i1_cY + num_i0_cY
            # print("==0:", len(selected_data[:, j]), np.std(selected_data[:, j]))
            print("#### effect: {:.2f}, i: {:2d}, j: {:2d}, c{:02d}=Y, yji1_cY: {:.2f}, yji0_cY: {:.2f}, delta: {:5.2f}, num_pos: {} + {} = {}".format(
                    effect, i, j, c, yji1_cY, yji0_cY, yji1_cY - yji0_cY,
                    num_i1_cY, num_i0_cY, num_pos
                )
            )
            avg_effect = ((yji1_cN - yji0_cN) * num_neg + (yji1_cY - yji0_cY) * num_pos) / (num_neg + num_pos)

            hited = ""
            if -0.10 < avg_effect < 0.08:
                est_dag_calibrated[i, j] = 0
                hited = "-" * 10
            mark = ""
            if true_dag is not None:
                mark = "+" * 10 if true_dag[i, j] else "-" * 10
            print("############ {} avg_effect: {:.2f}, effect_time: {:5.2f} {}\n".format(mark, avg_effect, avg_effect_times[i, j], hited))

    dags = (est_dag_calibrated, est_dag_filtered, est_dag_no_loop, est_dag_by_sort, est_dag_by_std, dag_by_avg_effect_time, dag_by_std_effect_time)
    return delta_effect, dags, (est_intial_dag, candidate_edges)
