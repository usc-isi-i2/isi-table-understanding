"""
Experimental code. Subject to change
"""

from layout_detector.crf.featurizer import Featurize
from typing import List
from pystruct.models import EdgeFeatureGraphCRF
from pystruct.learners import OneSlackSSVM
from sklearn.metrics import confusion_matrix, f1_score, accuracy_score, precision_recall_fscore_support
from type.layout.basic_edge_type import BasicEdgeType
import numpy as np
from sklearn.model_selection import train_test_split


class CRFLayoutEstimator:
    def __init__(self, max_iter=50, C_range=[0.03], tol=0.01, eval_against_test=False):
        self.max_iter = max_iter
        self.C_range = C_range
        self.tol = tol
        self.eval_against_test = eval_against_test

    def prepare_data(self, sheetList: List, tagsList: List, blocksList: List, layoutList: List):
        featurizer = Featurize(sheetList, tagsList, blocksList)

        print("Preparing data...")
        print(len(sheetList), len(tagsList), len(blocksList), len(layoutList))
        X_graph, _ = np.array(featurizer.get_input_features())
        y_graph = np.array(featurizer.get_label_map(layoutList))

        ## Remove tables with only one link (Base case)
        X_g = []
        y_g = []
        for i in range(len(X_graph)):
            if len(X_graph[i][1]) != 0:
                X_g.append(X_graph[i])
                y_g.append(y_graph[i])

        X_graph = np.array(X_g)
        y_graph = np.array(y_g)

        return X_graph, y_graph

    def set_input(self, sheetList: List, tagsList: List, blocksList: List, layoutList: List):
        X_graph, y_graph = self.prepare_data(sheetList, tagsList, blocksList, layoutList)
        # 60, 20, 20 split
        X_train, X_dev_test, y_train, y_dev_test = train_test_split(X_graph, y_graph, train_size=0.6, random_state=21)
        X_dev, X_test, y_dev, y_test = train_test_split(X_dev_test, y_dev_test, train_size=0.5, random_state=21)

        self.X_train = X_train
        self.X_dev = X_dev
        self.X_test = X_test
        self.y_train = y_train
        self.y_dev = y_dev
        self.y_test = y_test

        print("Train size: ", len(X_train))
        print("Dev size: ", len(X_dev))
        print("Test size: ", len(X_test))

    def evaluate_predictions(self, predictions, actuals):

        full_list_of_predictions = []
        full_list_of_ytrue = []
        total_score = 0.0

        for (prediction, actual) in zip(predictions, actuals):

            dataset_score = accuracy_score(actual, prediction)
            print(dataset_score)

            full_list_of_predictions.extend(prediction)
            full_list_of_ytrue.extend(actual)

            total_score += dataset_score

            if dataset_score != 1.0:
                # cnf_matrix = confusion_matrix(actual, prediction, labels=range(len(label_list)))
                # plot_confusion_matrix(cnf_matrix, classes=label_list)

                print(prediction)
                print(actual)

        print("Precision, Recall, F-Score, Support")
        print(precision_recall_fscore_support(full_list_of_ytrue, full_list_of_predictions))
        print("F1 Score: ", f1_score(full_list_of_ytrue, full_list_of_predictions, average=None, labels=BasicEdgeType.label_keys))

    def fit_crf(self):
        for C in self.C_range:
            print("Testing C value: {}".format(C))
            model = EdgeFeatureGraphCRF(inference_method="ad3")
            ssvm = OneSlackSSVM(model, inference_cache=50, C=C, tol=self.tol, max_iter=self.max_iter, n_jobs=4, verbose=False)
            ssvm.fit(self.X_train, self.y_train)
            predictions = [x for x in ssvm.predict(self.X_dev)]
            self.evaluate_predictions(predictions, self.y_dev)

        # Fit against the whole dataset except test
        # Is this approach correct?
        model = EdgeFeatureGraphCRF(inference_method="ad3")
        ssvm = OneSlackSSVM(model, inference_cache=50, C=0.03, tol=self.tol, max_iter=self.max_iter, n_jobs=4,
                            verbose=False)
        X_train_dev = np.concatenate([self.X_train, self.X_dev])
        y_train_dev = np.concatenate([self.y_train, self.y_dev])
        ssvm.fit(X_train_dev, y_train_dev)

        if self.eval_against_test:
            predictions = [x for x in ssvm.predict(self.X_test)]
            print("Test set evaluation")
            self.evaluate_predictions(predictions, self.y_test)

        self.model = ssvm
        return ssvm

    def evaluate_test_set(self, sheetList: List, tagsList: List, blocksList: List, layoutList: List):
        X_test, y_test = self.prepare_data(sheetList, tagsList, blocksList, layoutList)

        predictions = [x for x in self.model.predict(X_test)]
        self.evaluate_predictions(predictions, y_test)
