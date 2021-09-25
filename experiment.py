from dir_structure import DirStructure, DirId
import tempfile
import json
import os
import csv
import copy
import sys
from sfl.sfl.Diagnoser.diagnoserUtils import write_json_planning_file, read_json_planning_instance, read_json_planning_file
from sfl.sfl.Diagnoser.Experiment_Data import Experiment_Data
from sfl.sfl.Diagnoser.Diagnosis_Results import Diagnosis_Results
from operator import itemgetter
from numpy import mean
from functools import reduce

class Experiment(object):
    def __init__(self, dir_structure):
        self.dir_structure = dir_structure
        self.matrices = []
        for x in os.listdir(self.dir_structure.matrices):
            try:
                e = ExperimentMatrix(DirId(self.dir_structure, x))
                if e.is_ok():
                    self.matrices.append(e)
            except:
                pass

    def experiment(self, skip_if_not_exists=False):
        sanity_results = dict(list(map(lambda s: (s.matrix_id, s.experiment()), filter(lambda x: x.is_exists() or not skip_if_not_exists, self.matrices))))
        results_header = ["id", "matrix_name", "alpha"]
        metrics_header_added = False
        results = []
        for id in sanity_results:
            for matrix_name in sanity_results[id]:
                for alpha in sanity_results[id][matrix_name]:
                    metrics = sanity_results[id][matrix_name][alpha]
                    header = sorted(metrics)
                    if not metrics_header_added:
                        results_header.extend(header)
                        results.append(results_header)
                        metrics_header_added = True
                    results_row = [id, matrix_name, alpha] + list(map(lambda h: metrics[h], header))
                    results.append(results_row)
        with open(self.dir_structure.experiment, "w") as f:
            csv.writer(f).writerows(results)
        self.classification_evaluate()

    def classification_evaluate(self):
        def dir_classifiers(dir_name):
            return dict(list(map(lambda x: (x, json.load(open(os.path.join(dir_name, x)))), os.listdir(dir_name))))
        dirs = list(map(lambda x: os.path.join(self.dir_structure.classification_metrics, x), os.listdir(self.dir_structure.classification_metrics)))
        a = list(map(dir_classifiers, dirs))
        try:
            metrics = sorted(a[0].values()[0].keys())
            classifiers_data = dict(
                list(map(lambda k: (k, reduce(list.__add__, list(map(lambda res: res.get(k, {}).items(), a)), [])), a[0].keys())))
            classifiers_evaluation = dict(list(map(lambda d: (d, dict(list(map(lambda metric: (metric, mean(list(map(itemgetter(1), filter(lambda x: metric==x[0], classifiers_data[d]))))), metrics)))), classifiers_data)))
            results = [["classifier_name"] + metrics]
            for classifier_name in classifiers_evaluation:
                results_row = [classifier_name] + list(map(lambda h: classifiers_evaluation[classifier_name][h], metrics))
                results.append(results_row)
            with open(self.dir_structure.classification_evaluate, "w") as f:
                csv.writer(f).writerows(results)
        except:
            pass


class ExperimentMatrix(object):
    ALPHA_RANGE = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]

    def __init__(self, dir_id):
        self.dir_id = dir_id
        self.matrix_id = dir_id.id
        if not os.path.exists(self.dir_id.matrices):
            return
        read_json_planning_file(self.dir_id.matrices)
        self.classifiers = []
        self.components_names = copy.deepcopy(Experiment_Data().COMPONENTS_NAMES)
        self.bugs = copy.deepcopy(Experiment_Data().BUGS)

    def add_classifer(self, classifier):
        self.classifiers.append(classifier)

    def generate_influence_data(self, alpha):
        for name, influence_matrix in self.generate_influence_data_by_classifiers():
            yield name, {"experiment_type": "influence", "influence_alpha": alpha, "influence_matrix": influence_matrix}

    def generate_influence_data_by_classifiers(self):
        for classifier in self.classifiers:
            yield classifier.get_name(), classifier.get_influence()

    def is_ok(self):
        return self.bugs

    def is_exists(self):
        return os.path.exists(self.dir_id.experiments)

    def experiment(self):
        DirStructure.mkdir(self.dir_id.experiment_matrices)
        if not os.path.exists(self.dir_id.matrices):
            print('no matrix')
            return
        if not self.bugs:
            print('no bugs')
            return
        results = dict()
        with open(self.dir_id.matrices) as f:
            json_matrix = json.loads(f.read())
        for alpha in ExperimentMatrix.ALPHA_RANGE:
            for matrix_name, influence_data in self.generate_influence_data(alpha):
                matrix = copy.deepcopy(json_matrix)
                matrix.update(influence_data)
                with open(os.path.join(self.dir_id.experiment_matrices, matrix_name + str(alpha)), "w") as f:
                    json.dump(matrix, f)
                ei = read_json_planning_instance(matrix)
                ei.diagnose()
                results.setdefault(matrix_name, dict())[alpha] = Diagnosis_Results(ei.diagnoses, ei.initial_tests, ei.error).metrics
        with open(self.dir_id.experiments, "w") as f:
            json.dump(results, f)

    @staticmethod
    def experiment_classifiers(dir_id):
        from sanity_classify import SanityClassify, StaticClassify, RandomClassify, DoubleSanityClassify
        from learning_classify import LearningClassify
        experiment_matrix = ExperimentMatrix(dir_id)
        list(map(experiment_matrix.add_classifer, SanityClassify.get_all_sanity_classifers(dir_id)))
        list(map(experiment_matrix.add_classifer, StaticClassify.get_all_static_classifers(dir_id)))
        list(map(experiment_matrix.add_classifer, RandomClassify.get_all_random_classifers(dir_id)))
        # list(map(experiment_matrix.add_classifer, DoubleSanityClassify.get_all_double_classifers(dir_id)))
        list(map(experiment_matrix.add_classifer, LearningClassify.get_all_classifers(dir_id)))
        experiment_matrix.experiment()


if __name__ == "__main__":
    # ExperimentMatrix.experiment_classifiers(DirId(DirStructure(r"C:\amirelm\component_importnace\data\maven_3"), sys.argv[1]))
    # exit()
    # ExperimentMatrix.experiment_classifiers(DirId(DirStructure(sys.argv[1]), sys.argv[2]))
    DIR_BASE_PATH = r"component_importance_data"
    Experiment(DirStructure(DIR_BASE_PATH)).experiment()
    # Experiment(DirStructure(r"Z:\component_importance\TIKA")).experiment()
    # pass