from dir_structure import DirStructure, DirId
import tempfile
import json
import os
import csv
import copy
import sys
from sfl_diagnoser.Diagnoser.diagnoserUtils import write_json_planning_file, read_json_planning_instance, read_json_planning_file
from sfl_diagnoser.Diagnoser.Experiment_Data import Experiment_Data
from sfl_diagnoser.Diagnoser.Diagnosis_Results import Diagnosis_Results


class Experiment(object):
    def __init__(self, dir_structure):
        self.dir_structure = dir_structure
        self.matrices = filter(lambda x: x.is_ok(), map(lambda x: ExperimentMatrix(DirId(self.dir_structure, x)), os.listdir(self.dir_structure.matrices)))

    def experiment(self):
        sanity_results = dict(map(lambda s: (s.matrix_id, s.experiment()), self.matrices))
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
                    results_row = [id, matrix_name, alpha] + map(lambda h: metrics[h], header)
                    results.append(results_row)
        with open(self.dir_structure.experiment, "wb") as f:
            csv.writer(f).writerows(results)


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

    def experiment(self):
        DirStructure.mkdir(self.dir_id.experiment_matrices)
        if not os.path.exists(self.dir_id.matrices):
            return
        if not self.bugs:
            return
        if not os.path.exists(self.dir_id.experiments):
            results = dict()
            with open(self.dir_id.matrices) as f:
                json_matrix = json.loads(f.read())
            for alpha in ExperimentMatrix.ALPHA_RANGE:
                for matrix_name, influence_data in self.generate_influence_data(alpha):
                    print(matrix_name)
                    matrix = copy.deepcopy(json_matrix)
                    matrix.update(influence_data)
                    with open(os.path.join(self.dir_id.experiment_matrices, matrix_name + str(alpha)), "wb") as f:
                        json.dump(matrix, f)
                    ei = read_json_planning_instance(matrix)
                    ei.diagnose()
                    results.setdefault(matrix_name, dict())[alpha] = Diagnosis_Results(ei.diagnoses, ei.initial_tests, ei.error).metrics
            with open(self.dir_id.experiments, "wb") as f:
                json.dump(results, f)
        with open(self.dir_id.experiments) as f:
            return json.loads(f.read())

    @staticmethod
    def experiment_classifiers(dir_id):
        from sanity_classify import SanityClassify
        from learning_classify import LearningClassify
        experiment_matrix = ExperimentMatrix(dir_id)
        map(experiment_matrix.add_classifer, SanityClassify.get_all_sanity_classifers(dir_id))
        # map(experiment_matrix.add_classifer, LearningClassify.get_all_classifers(dir_id))
        experiment_matrix.experiment()


if __name__ == "__main__":
    ExperimentMatrix.experiment_classifiers(DirId(DirStructure(r"C:\amirelm\component_importnace\data\maven_1"), sys.argv[1]))
    exit()
    Experiment(DirStructure(r"C:\amirelm\component_importnace\data\d4j_lang12")).experiment()
    # pass