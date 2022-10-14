import os
import numpy as np
import pandas as pd

np.set_printoptions(threshold = np.inf)
# 不以科学计数显示:
np.set_printoptions(suppress = True)

# 显示所有列
pd.set_option('display.max_columns', None)
# 显示所有行
pd.set_option('display.max_rows', None)

import warnings
warnings.filterwarnings("ignore")


class Processer:

    def __init__(self):
        self.raw_samples = None
        self.raw_rows = None
        self.raw_cols = None
        self.mode = None

    def reshape(self, raw_data, mode):

        if len(raw_data.shape) == 2:
            # n, m
            if mode == 0:
                res = raw_data.reshape(-1, self.raw_rows, self.raw_cols)
            else:
                res = raw_data.reshape(self.samples, self.raw_rows, -1)
            self.raw_samples = res.shape[0]
            self.raw_rows = res.shape[1]
            self.raw_cols = res.shape[2]
            return res

        if len(raw_data.shape) == 3:
            # n, m, w
            self.raw_samples = raw_data.shape[0]
            self.raw_rows = raw_data.shape[1]
            self.raw_cols = raw_data.shape[2]
            if mode == 0:  # n, m*w
                samples = self.raw_samples
                cols = self.raw_rows * self.raw_cols
            else:  # n*m, w
                samples = self.raw_samples * self.raw_rows
                cols = self.raw_cols
            return raw_data.reshape(samples, cols)


def clean_label(raw_data, raw_label):
    from sklearn.linear_model import LogisticRegression
    from sklearn.neighbors import KNeighborsClassifier
    from doubtlab.ensemble import DoubtEnsemble
    from doubtlab.reason import (
        ProbaReason, WrongPredictionReason, ShortConfidenceReason, LongConfidenceReason, MarginConfidenceReason, DisagreeReason,  CleanlabReason
    )

    model1 = KNeighborsClassifier()
    model1.fit(raw_data, raw_label)

    # model2 = LogisticRegression(max_iter=1_000)
    # model2.fit(raw_data, raw_label)

    reasons = {
        'proba': ProbaReason(model=model1),
        'wrong_pred': WrongPredictionReason(model=model1),
        'short_confident': ShortConfidenceReason(model=model1, threshold=0.4),
        'long_confident': LongConfidenceReason(model=model1),
        'margin_confident': MarginConfidenceReason(model=model1),
        # 'disagree': DisagreeReason(model1, model2),
        # 'cleanlab': CleanlabReason(model1)
    }
    doubt = DoubtEnsemble(**reasons)

    indices = doubt.get_indices(raw_data, raw_label)
    print(len(indices))
    print(indices)
    # print(doubt.get_predicates(raw_data, raw_label))

    return raw_data[indices], raw_label[indices]


def clean_sample_outlier(raw_data, raw_label):
    from pyod.models.ecod import ECOD

    clf = ECOD()
    clf.fit(raw_data)

    y_train_scores = clf.decision_scores_
    print(y_train_scores)
    print(clf.labels_)

    indices = np.argwhere(clf.labels_ == 0).reshape(-1)
    return raw_data[indices], raw_label[indices]


def clean_feature_outlier(raw_data, raw_label):  #
    temp_data = raw_data.copy()

    file_name = './result/train/model_feature_outlier.csv'
    if not os.path.exists(file_name):
        model = pd.DataFrame()
        for i in range(temp_data.shape[1]):
            print('i=', i)
            cur_data = temp_data[:, i]

            fare_q3 = np.quantile(cur_data, q=0.75)
            fare_q1 = np.quantile(cur_data, q=0.25)
            fare_iqr = fare_q3 - fare_q1
            fare_up_limit = fare_q3 + 1.5 * fare_iqr
            fare_low_limit = fare_q1 - 1.5 * fare_iqr

            model_dict = {}
            model_dict['fare_up_limit'], model_dict['fare_low_limit'] = fare_up_limit, fare_low_limit
            model = model.append(model_dict, ignore_index=True)

            up_outlier = cur_data > fare_up_limit
            low_outlier = cur_data < fare_low_limit
            temp_data[up_outlier, i] = fare_up_limit
            temp_data[low_outlier, i] = fare_low_limit

        model.to_csv(file_name, index=False)
    else:
        model = pd.read_csv(file_name)
        for i in range(temp_data.shape[1]):
            print('i=', i)
            fare_up_limit, fare_low_limit = model.loc[i, 'fare_up_limit'], model.loc[i, 'fare_low_limit']
            cur_data = temp_data[:, i]

            up_outlier = cur_data > fare_up_limit
            low_outlier = cur_data < fare_low_limit
            temp_data[up_outlier, i] = fare_up_limit
            temp_data[low_outlier, i] = fare_low_limit

    return temp_data, raw_label


def set_discrete(raw_data, raw_label):  #
    from discreter import cont_var_bin, cont_var_bin_map

    temp_raw_data = pd.DataFrame(raw_data, columns=[str(i) for i in range(raw_data.shape[1])])
    temp_raw_label = pd.Series(raw_label)

    result = []
    for i in range(temp_raw_data.shape[1]):
        print('i=', i)
        data_test1, gain_value_save1, gain_rate_save1 = cont_var_bin(temp_raw_data.iloc[:, i], temp_raw_label,
                                                                     method=1, mmin=4, mmax=20, bin_rate=0.01, stop_limit=0.1,
                                                                     bin_min_num=20)
        temp = cont_var_bin_map(temp_raw_data.iloc[:, i], data_test1).to_list()
        result.append(temp)

    return np.array(result).T, raw_label


def set_normalized(raw_data, raw_label):  #
    import pickle
    from sklearn.preprocessing import MinMaxScaler

    file_name = './result/train/model_set_normalized.sav'
    if not os.path.exists(file_name):
        min_max_scaler = MinMaxScaler(feature_range=[0, 1])
        min_max_scaler.fit(raw_data)
        pickle.dump(min_max_scaler, open(file_name, 'wb'))
    else:
        min_max_scaler = pickle.load(open(file_name, 'rb'))

    temp_data = min_max_scaler.transform(raw_data)

    return temp_data, raw_label


def under_sampling(raw_data, raw_label):
    from collections import Counter
    from imblearn.under_sampling import CondensedNearestNeighbour

    print('Original dataset shape %s' % Counter(raw_label))
    cnn = CondensedNearestNeighbour(random_state=42)
    temp_data, temp_label = cnn.fit_resample(raw_data, raw_label)
    print('Resampled dataset shape %s' % Counter(temp_label))

    return temp_data, temp_label



def extract_feature(raw_data):
    pass


def generate_train(raw_train_data, raw_train_label):
    pro_train = Processer()

    tmp_train_data, tmp_train_label = raw_train_data, raw_train_label

    tmp_train_data = pro_train.reshape(tmp_train_data, 0)
    tmp_train_data, tmp_train_label = clean_label(tmp_train_data, tmp_train_label)
    tmp_train_data = pro_train.reshape(tmp_train_data, 0)
    # np.save('./result/train/0-clean_label.npy', tmp_train_data)

    # tmp_train_data = np.load('./result/train/0-clean_label.npy')
    tmp_train_data = pro_train.reshape(tmp_train_data, 0)
    tmp_train_data, tmp_train_label = clean_sample_outlier(tmp_train_data, tmp_train_label)
    tmp_train_data = pro_train.reshape(tmp_train_data, 0)
    # np.save('./result/train/1-clean_sample_outlier.npy', tmp_train_data)

    # tmp_train_data = np.load('./result/train/1-clean_sample_outlier.npy')  #
    tmp_train_data = pro_train.reshape(tmp_train_data, 0)
    tmp_train_data, tmp_train_label = clean_feature_outlier(tmp_train_data, tmp_train_label)
    tmp_train_data = pro_train.reshape(tmp_train_data, 0)
    # np.save('./result/train/2-clean_feature_outlier.npy', tmp_train_data)

    # tmp_train_data = np.load('./result/train/2-clean_feature_outlier.npy')  #
    tmp_train_data = pro_train.reshape(tmp_train_data, 0)
    tmp_train_data, tmp_train_label = set_normalized(tmp_train_data, tmp_train_label)
    tmp_train_data = pro_train.reshape(tmp_train_data, 0)
    # np.save('./result/train/3-set_normalized.npy', tmp_train_data)

    # tmp_train_data = np.load('./result/train/3-set_normalized.npy')
    tmp_train_data = pro_train.reshape(tmp_train_data, 0)
    tmp_train_data, tmp_train_label = under_sampling(tmp_train_data, tmp_train_label)
    tmp_train_data = pro_train.reshape(tmp_train_data, 0)
    np.save('./result/train/4-under_sampling.npy', tmp_train_data)
    np.save('./result/train/4-label.npy', tmp_train_label)

    # tmp_train_data = np.load('./result/train/4-under_sampling.npy')
    # tmp_train_data = pro_train.reshape(tmp_train_data, 0)
    # tmp_train_data = extract_feature(tmp_train_data)
    # tmp_train_data = pro_train.reshape(tmp_train_data, 0)
    # np.save('./result/train/5-extract_feature.npy', tmp_train_data)

    # tmp_train_data = np.load('./result/train/5-extract_feature.npy')  #
    # tmp_train_data = pro_train.reshape(tmp_train_data, 0)
    # tmp_train_data, tmp_train_label = set_discrete(tmp_train_data, tmp_train_label)
    # tmp_train_data = pro_train.reshape(tmp_train_data, 0)
    # np.save('./result/train/6-set_discrete.npy', tmp_train_data)

def generate_test(raw_test_data, dirname):
    pro_test = Processer()

    tmp_test_data = raw_test_data

    tmp_test_data = pro_test.reshape(tmp_test_data, 0)
    tmp_test_data, _ = clean_feature_outlier(tmp_test_data, None)
    tmp_test_data = pro_test.reshape(tmp_test_data, 0)
    # np.save(f'./result/test/{dirname}/0-clean_feature_outlier.npy', tmp_test_data)

    # tmp_test_data = np.load(f'./result/test/{dirname}/0-clean_feature_outlier.npy',)
    tmp_test_data = pro_test.reshape(tmp_test_data, 0)
    tmp_test_data, _ = set_normalized(tmp_test_data, None)
    tmp_test_data = pro_test.reshape(tmp_test_data, 0)
    np.save(f'./result/test/{dirname}/1-set_normalized.npy', tmp_test_data)

    # tmp_test_data = np.load(f'./result/test/{dirname}/1-set_normalized.npy',)
    # tmp_test_data = pro_test.reshape(tmp_test_data, 0)
    # tmp_test_data, _ = set_discrete(tmp_test_data, None)
    # tmp_test_data = pro_test.reshape(tmp_test_data, 0)
    # np.save(f'./result/test/{dirname}/2-set_discrete.npy', tmp_test_data)

if __name__ == '__main__':

    raw_data = np.load('../../data/train/cityA/X.npy')
    raw_label = np.load('../../data/train/cityA/Y.npy')

    from sklearn.model_selection import train_test_split
    raw_train_data, raw_test_data, raw_train_label, raw_test_label = train_test_split(
      raw_data,
      raw_label,
      test_size=0.3,
      random_state=0
    )

    generate_train(raw_train_data, raw_train_label)
    generate_test(raw_test_data, dirname='cityA')

    city_b_data = np.load('../../data/train/cityB/train/X.npy')
    city_b_label = np.load('../../data/train/cityB/train/Y.npy')

    generate_test(city_b_data, dirname='cityB')
