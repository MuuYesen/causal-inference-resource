import numpy as np
import pandas as pd

from model import ConvLSTM
from processer import Processer

def main():
    raw_train_data = np.load('../../data/example/cityA/X.npy')
    raw_train_label = np.load('../../data/example/cityA/Y.npy')
    raw_test_data = np.load('../../data/example/cityB/X.npy')
    raw_test_label = np.load('../../data/example/cityB/Y.npy')

    processer = Processer()
    model_train_data, model_train_label = processer.fit(raw_train_data, raw_train_label)
    model_test_data, model_test_label = processer.fit(raw_test_data, raw_test_label)

    model = ConvLSTM(model_train_data.shape[1:])
    model.train(model_train_data, model_train_label,
                model_test_data, model_test_label)

    raw_test_data = np.load('../../data/example/cityB/X.npy')
    model_test_data = processer.transform(raw_test_data)
    pred_res = model.predict(model_test_data)
    pd.DataFrame(pred_res).to_csv('./submission.csv')

if __name__ == '__main__':
    main()