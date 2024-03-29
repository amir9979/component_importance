from influence_classify import InfluenceClassify
import pandas as pd
import numpy as np
from operator import itemgetter
from copy import deepcopy
from sklearn.feature_selection import VarianceThreshold
from sklearn.model_selection import cross_val_score
from sklearn import metrics
from sklearn import preprocessing
from dir_structure import DirStructure
from sklearn.model_selection import cross_validate
from sklearn.pipeline import make_pipeline
from sklearn.feature_selection import SelectKBest
from sklearn.feature_selection import chi2
import json
import traceback
from itertools import product


class AbstractLearningClassify(InfluenceClassify):
    def __init__(self, dir_id):
        super(AbstractLearningClassify, self).__init__(dir_id)

    def get_training_features(self):
        pass

    def get_testing_features(self):
        pass

    def get_training_labels(self):
        pass

    def get_classifier(self):
        pass

    def get_test_ids(self):
        pass


class LearningClassify(InfluenceClassify):
    PROBABILITY = {True: {True: 0, False: 1}, False: {True: 1, False: 0}}

    def __init__(self, dir_id, classifier, additional_name=''):
        super(LearningClassify, self).__init__(dir_id)
        self.classifier = classifier
        self.additional_name = additional_name
        self.influence_dict = {}
        # self.init_model()

    def init_model(self):
        self.describe()
        model = self.get_classifier().fit(self.get_training_featues(), self.get_training_labels())
        prediction_probabilities = self.get_classifier().predict_proba(self.get_testing_featues())
        prediction = self.get_classifier().predict(self.get_testing_featues())
        probabilities_index = LearningClassify.PROBABILITY[prediction_probabilities[0][0] >= 0.5][prediction[0]]
        for test_id, probability in zip(self.get_test_ids(),
                                        list(map(itemgetter(probabilities_index), prediction_probabilities))):
            test_name, function_name = test_id
            self.influence_dict.setdefault(test_name, dict()).setdefault(function_name, probability)

    def get_name(self):
        # params = repr(map(lambda x: str(x[1]).replace("\n",'').replace('(','').replace(')','').replace(',','').replace(']','').replace('[','').replace('',''),
        #                       sorted(filter(lambda x: x[1], self.classifier.get_params(False).items()), key=lambda x:x[1]))).replace(']','').replace('[','')
        # params = "_".join(repr(self.classifier.get_params()).replace('(','').replace(')','').replace(',','').replace(']','').replace('[','').replace('','').split())
        return "learning_{0}_{1}".format(self.classifier.__class__.__name__, self.additional_name)

    def get_training_featues(self):
        train = pd.read_csv(self.get_dir_id().training_set)
        train = LearningClassify.drop(train)
        train = train.drop('label', axis=1)
        train_features = np.array(train)
        return train_features

    def get_testing_featues(self):
        test = pd.read_csv(self.get_dir_id().testing_set)
        test_features = np.array(LearningClassify.drop(test))
        return test_features

    def get_training_labels(self):
        train = pd.read_csv(self.get_dir_id().training_set)
        return np.array(train['label'])

    def get_classifier(self):
        return self.classifier

    def get_test_ids(self):
        test = pd.read_csv(self.get_dir_id().testing_set)
        return zip(test['test_name'], test['function_name'])

    def get_influence(self):
        return self.influence_dict

    def check_feature_importance(self):
        if not hasattr(self.get_classifier(), "feature_importances_"):
            return
        importances = self.get_classifier().feature_importances_
        std = np.std([tree.feature_importances_ for tree in self.get_classifier().estimators_], axis=0)
        indices = np.argsort(importances)[::-1]
        print("Feature ranking:")
        for f in range(X.shape[1]):
            print("%d. feature %d (%f)" % (f + 1, indices[f], importances[indices[f]]))

    @staticmethod
    def get_all_classifers(dir_id):
        from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
        from sklearn.tree import DecisionTreeClassifier
        from sklearn.neural_network import MLPClassifier
        from sklearn.linear_model import LogisticRegression
        from sklearn.neighbors import KNeighborsClassifier
        from sklearn.svm import SVC
        from sklearn.naive_bayes import GaussianNB
        from sklearn.ensemble import ExtraTreesClassifier
        from sklearn.feature_selection import VarianceThreshold
        ans = [LearningClassify(dir_id, RandomForestClassifier(n_estimators=10, random_state=42)),
                LearningClassify(dir_id, GradientBoostingClassifier()),
                LearningClassify(dir_id, DecisionTreeClassifier()),
                LearningClassify(dir_id, MLPClassifier(solver='adam', alpha=1e-5, activation='relu', max_iter=3000, hidden_layer_sizes=(30, 30, 30, 30, 30), random_state=13)),
                LearningClassify(dir_id, LogisticRegression()),
                LearningClassify(dir_id, KNeighborsClassifier()),
                LearningClassify(dir_id, SVC(probability=True)),
                LearningClassify(dir_id, GaussianNB()),
                LearningClassify(dir_id, ExtraTreesClassifier(n_estimators=100, random_state=0))
                # LearningClassify(dir_id, make_pipeline(VarianceThreshold(threshold=(.8 * (1 - .8))), DecisionTreeClassifier()), "VarianceThreshold"),
                # LearningClassify(dir_id, make_pipeline(SelectKBest(chi2, k=10), DecisionTreeClassifier()), "SelectKBest_chi"),
                # LearningClassify(dir_id, make_pipeline(SelectKBest(k=10), DecisionTreeClassifier()), "SelectKBest_f_classif")
                ]
        lcs = []
        for lc in ans:
            try:
                lc.init_model()
                lcs.append(lc)
            except Exception as e:
                traceback.print_exc()
                print(e)
        pd.concat(map(lambda x: x.cross_validation(), lcs)).to_csv(dir_id.classification_metrics, index=False)
        return ans

    @staticmethod
    def drop(features):
        return features.drop('test_name', axis=1).drop('function_name', axis=1)

    def cross_validation(self):
        import sklearn.metrics as metrics
        from sklearn.metrics import get_scorer
        scores_names = ['accuracy', 'adjusted_mutual_info_score', 'adjusted_rand_score', 'average_precision', 'completeness_score',
         'f1', 'f1_macro', 'f1_micro', 'f1_weighted', 'fowlkes_mallows_score',
         'homogeneity_score', 'mutual_info_score', 'neg_log_loss', 'normalized_mutual_info_score', 'precision',
         'precision_macro', 'precision_micro', 'precision_weighted', 'recall',
         'recall_macro', 'recall_micro', 'recall_weighted', 'roc_auc', 'v_measure_score']
        metrics_functions = [metrics.cohen_kappa_score, metrics.hinge_loss,
                             metrics.matthews_corrcoef, metrics.accuracy_score,
                             metrics.f1_score, metrics.hamming_loss,
                             metrics.log_loss, metrics.precision_score, metrics.recall_score,
                             metrics.zero_one_loss, metrics.average_precision_score, metrics.roc_auc_score]

        def pr_auc_score(y_true, y_score):
            """
            Generates the Area Under the Curve for precision and recall.
            """
            precision, recall, thresholds = \
                metrics.precision_recall_curve(y_true, y_score[:, 1])
            return metrics.auc(recall, precision, reorder=True)

        pr_auc_scorer = metrics.make_scorer(pr_auc_score, greater_is_better=True,
                                    needs_proba=True)
        scoring = {x: get_scorer(x) for x in scores_names}
        scoring.update({x.__name__: metrics.make_scorer(x) for x in metrics_functions})
        # scoring["pr_auc"] = pr_auc_scorer

        def tn(y_true, y_pred): return metrics.confusion_matrix(y_true, y_pred)[0, 0]

        def fp(y_true, y_pred): return metrics.confusion_matrix(y_true, y_pred)[0, 1]

        def fn(y_true, y_pred): return metrics.confusion_matrix(y_true, y_pred)[1, 0]

        def tp(y_true, y_pred): return metrics.confusion_matrix(y_true, y_pred)[1, 1]

        def cost(y_true, y_pred, fp_cost=1, fn_cost=1): return fp(y_true, y_pred) * fp_cost + fn(y_true, y_pred)*fn_cost

        def mean_squared_error_cost(true_value, pred_value, fp_cost=1, fn_cost=1):
            # fp is true_value=true and pred_value>0.5
            # fn is true_value=false and pred_value<0.5
            from numpy import mean
            squares = []
            for t,p in zip(true_value, pred_value):
                diff = (t-p) ** 2
                if t:
                    diff *= fp_cost
                else:
                    diff *= fn_cost
                squares.append(diff)
            return mean(squares)

        def mse(y_true, y_pred):
            return min(metrics.mean_squared_error([1 if x else 0 for x in y_true], list(map(lambda x: x[0][1 if x[1] else 0], zip(y_pred, y_true)))), metrics.mean_squared_error([1 if x else 0 for x in y_true], list(map(lambda x: x[0][0 if x[1] else 1], zip(y_pred, y_true)))))

        def mse_cost(y_true, y_pred, fp_cost=1, fn_cost=1):
            return min(mean_squared_error_cost([1 if x else 0 for x in y_true], list(map(lambda x: x[0][1 if x[1] else 0], zip(y_pred, y_true))), fp_cost=fp_cost, fn_cost=fn_cost),
                       mean_squared_error_cost([1 if x else 0 for x in y_true], list(map(lambda x: x[0][0 if x[1] else 1], zip(y_pred, y_true))), fp_cost=fp_cost, fn_cost=fn_cost))

        def mse1(y_true, y_pred):
            return max(metrics.mean_squared_error([1 if x else 0 for x in y_true], list(map(lambda x: x[0][1 if x[1] else 0], zip(y_pred, y_true)))), metrics.mean_squared_error([1 if x else 0 for x in y_true], list(map(lambda x: x[0][0 if x[1] else 1], zip(y_pred, y_true)))))

        def mse_cost1(y_true, y_pred, fp_cost=1, fn_cost=1):
            return max(mean_squared_error_cost([1 if x else 0 for x in y_true], list(map(lambda x: x[0][1 if x[1] else 0], zip(y_pred, y_true))), fp_cost=fp_cost, fn_cost=fn_cost),
                       mean_squared_error_cost([1 if x else 0 for x in y_true], list(map(lambda x: x[0][0 if x[1] else 1], zip(y_pred, y_true))), fp_cost=fp_cost, fn_cost=fn_cost))

        scoring.update({'tp': metrics.make_scorer(tp), 'tn': metrics.make_scorer(tn),
                        'fp': metrics.make_scorer(fp), 'fn': metrics.make_scorer(fn)})

        scoring.update({"cost_{0}_{1}".format(*x): metrics.make_scorer(cost, fp_cost=x[0], fn_cost=x[1]) for x in product(range(1,4), range(1,4))})
        # scoring.update({"mse_cost_{0}_{1}".format(*x): metrics.make_scorer(mse_cost, fp_cost=x[0], fn_cost=x[1], needs_proba=True) for x in
        #                 product(range(1, 4), range(1, 4))})

        # scoring.update({"mse1_cost_{0}_{1}".format(*x): metrics.make_scorer(mse_cost1, fp_cost=x[0], fn_cost=x[1], needs_proba=True) for x in
        #                 product(range(1, 4), range(1, 4))})
        #
        # scoring["mse"] = metrics.make_scorer(mse, needs_proba=True)
        # scoring["mse1"] = metrics.make_scorer(mse1, needs_proba=True)
        self.get_classifier().fit(self.get_training_featues(), self.get_training_labels())
        scores = cross_validate(self.get_classifier(), self.get_training_featues(), self.get_training_labels(), cv=3, scoring=scoring, return_train_score=True)
        all_scores = {'classifier_name' : self.get_name(), 'id': self.dir_id.id}
        for score in scores:
            all_scores["{0}_mean".format(score)] = scores[score].mean()
            all_scores["{0}_std".format(score)] = scores[score].std()
        return pd.DataFrame([all_scores])

    def _describe_helper(self, dir_name, array):
        pd.DataFrame(array).describe().to_csv(getattr(self.get_dir_id(), dir_name))

    def describe(self):
        self._describe_helper("training_describe", self.get_training_featues())
        self._describe_helper("testing_describe", self.get_testing_featues())
