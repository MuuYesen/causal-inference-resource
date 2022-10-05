import numpy as np
from model import ConvLSTM
from processer import Processer

def main():
    raw_train_data = np.load('../../data/example/cityA/X.npy')
    processer = Processer()
    model_train_data = processer.fit(raw_train_data)
    model = ConvLSTM(model_train_data.shape[1:])
    model.train(model_train_data)

    raw_test_data = np.load('../../data/example/cityB/X.npy')
    model_test_data = processer.transform(raw_test_data)
    model.predict(model_test_data)

if __name__ == '__main__':
    main()