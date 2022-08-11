# coding=utf-8
# Copyright (C) 2021. Huawei Technologies Co., Ltd. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import numpy as np
import matplotlib.pyplot as plt


class GraphDAG(object):
    '''
    Visualization for causal discovery learning results.

    Parameters
    ----------
    est_dag: np.ndarray
        The DAG matrix to be estimated.
    true_dag: np.ndarray
        The true DAG matrix.
    save_name: str
        The file name of the image to be saved.
    '''

    def __init__(self, est_dag, *args, **kwargs):

        self.est_dag = est_dag
        self.true_dag = None
        self.save_name = None
        
        if len(args) == 2:
            self.true_dag = args[0]
            self.save_name = args[1]
        
        else:
            if len(args) == 1:
                self.true_dag = args[0]
            
            if 'save_name' in kwargs:
                self.save_name = kwargs['save_name']

        GraphDAG._plot_dag(self.est_dag, self.true_dag, self.save_name)

    @staticmethod
    def _plot_dag(est_dag, true_dag, save_name=None):
        """
        Plot the estimated DAG and the true DAG.

        Parameters
        ----------
        est_dag: np.ndarray
            The DAG matrix to be estimated.
        true_dag: np.ndarray
            The True DAG matrix.
        save_name: str
            The file name of the image to be saved.
        """
        if isinstance(true_dag, np.ndarray):
            
            # trans diagonal element into 0
            for i in range(len(true_dag)):
                if est_dag[i][i] == 1:
                    est_dag[i][i] = 0
                if true_dag[i][i] == 1:
                    true_dag[i][i] = 0

            # set plot size
            fig, (ax1, ax2) = plt.subplots(figsize=(8, 3), ncols=2)

            ax1.set_title('est_graph')
            map1 = ax1.imshow(est_dag, cmap='Greys', interpolation='none')
            fig.colorbar(map1, ax=ax1)

            ax2.set_title('true_graph')
            map2 = ax2.imshow(true_dag, cmap='Greys', interpolation='none')
            fig.colorbar(map2, ax=ax2)
            
            if save_name is not None:
                fig.savefig(save_name)
            # plt.show()

        elif isinstance(est_dag, np.ndarray):

            # trans diagonal element into 0
            for i in range(len(est_dag)):
                if est_dag[i][i] == 1:
                    est_dag[i][i] = 0

            # set plot size
            fig, ax1 = plt.subplots(figsize=(4, 3), ncols=1)

            ax1.set_title('est_graph')
            map1 = ax1.imshow(est_dag, cmap='Greys', interpolation='none')
            fig.colorbar(map1, ax=ax1)

            if save_name is not None:
                fig.savefig(save_name)
            # plt.show()

        else:
            raise TypeError("Input data is not numpy.ndarray!")
