import numpy as np
import pandas as pd

from model import ConvLSTM
from processer import Processer

def main_strategy_1():
    raw_train_data = np.load('../../data/example/cityA/X.npy')
    raw_train_label = np.load('../../data/example/cityA/Y.npy')
    raw_test_data = np.load('../../data/example/cityB/X.npy')
    raw_test_label = np.load('../../data/example/cityB/Y.npy')

    processer = Processer()
    model_train_data, model_train_label = processer.fit(raw_train_data, raw_train_label)
    model_test_data, model_test_label = processer.transform(raw_test_data, raw_test_label)

    model = ConvLSTM(model_train_data.shape[1:])
    model.train(model_train_data, model_train_label,
                model_test_data, model_test_label)

    raw_test_data = np.load('../../data/example/cityB/X.npy')
    model_test_data = processer.transform(raw_test_data)
    pred_res = model.predict(model_test_data)
    pd.DataFrame(pred_res).to_csv('result/v1/submission.csv')

def main_strategy_2():
    from sklearn.model_selection import train_test_split

    # model_baseline
    raw_data = np.load('../../data/train/cityA/X.npy')
    raw_label = np.load('../../data/train/cityA/Y.npy')
    raw_train_data,raw_test_data, raw_train_label, raw_test_label = train_test_split(
      raw_data,
      raw_label,
      test_size=0.3,
      random_state=0
    )
    processer = Processer()
    model_train_data, model_train_label = processer.fit(raw_train_data, raw_train_label)
    model_test_data, model_test_label = processer.transform(raw_test_data, raw_test_label)

    model = ConvLSTM(model_train_data.shape[1:])
    model.train(model_train_data, model_train_label,
                model_test_data, model_test_label)

    # model_transfer
    raw_data = np.load('../../data/train/cityB/train/X.npy')
    raw_label = np.load('../../data/train/cityB/train/Y.npy')
    raw_train_data,raw_test_data, raw_train_label, raw_test_label = train_test_split(
      raw_data,
      raw_label,
      test_size=0.3,
      random_state=0
    )
    processer = Processer()
    model_train_data, model_train_label = processer.fit(raw_train_data, raw_train_label)
    model_test_data, model_test_label = processer.transform(raw_test_data, raw_test_label)

    model = ConvLSTM(model_train_data.shape[1:])
    model.transfer(model_train_data, model_train_label,
                   model_test_data, model_test_label)

    # use model_transfer to predict out_of_sample
    raw_test_data = np.load('../../data/test/X.npy')
    model_test_data = processer.transform(raw_test_data)
    pred_res = model.predict(model_test_data)
    pd.DataFrame(pred_res).to_csv('result/v2/submission.csv')

if __name__ == '__main__':
    main_strategy_2()