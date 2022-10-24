
class Processer:

    def __init__(self):
        pass

    def fit(self, raw_train_data, raw_train_label):
        self.samples = -1
        self.time = 7
        self.rows = 96
        self.cols = 10
        self.channels = 1

        model_train_data = raw_train_data.reshape(self.samples, self.time, self.rows, self.cols, self.channels)
        model_train_label = raw_train_label
        return model_train_data, model_train_label

    def transform(self, raw_test_data, raw_test_label=None):
        model_test_data = raw_test_data.reshape(self.samples, self.time, self.rows, self.cols, self.channels)
        model_test_label = raw_test_label
        
        if raw_test_label is None:
          return model_test_data
        else:
          return model_test_data, model_test_label
