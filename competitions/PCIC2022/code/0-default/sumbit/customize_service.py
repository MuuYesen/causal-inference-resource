# coding = utf-8

import os
import pandas as pd
from model_service.pytorch_model_service import PTServingBaseService


class TransferLearning(PTServingBaseService):
    def __init__(self, model_name, model_path):
        self.model_name = model_name
        self.model_path = model_path

        # ====================================================================
        # Get the abs path of your submission file named like `submission.csv
        # ====================================================================
        dir_path = os.path.dirname(os.path.realpath(self.model_path))
        csv_file = os.path.join(dir_path, 'submission.csv')
        self.submission_array = pd.read_csv(csv_file, header=None).values.tolist()


    def _preprocess(self, data):
        pass

    def _inference(self, data):
        if self.submission_array is not None:
            result = {'result': str(self.submission_array)}
        else:
            result = {'result': 'predict score is None'}
        return result

    def _postprocess(self, data):
        return data
