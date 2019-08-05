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
from itertools import product


class SanityExperiment(object):
    def __init__(self, dir_structure):
        self.dir_structure = dir_structure
        self.matrices = map(lambda x: SanityMatrix(DirId(self.dir_structure, x)), os.listdir(self.dir_structure.matrices))

    def sanity(self):
        sanity_results = dict(map(lambda s: (s.matrix_id, s.sanity()), self.matrices))
        results_header = ["id", "buggy_value", "non_buggy_value", "alpha"]
        metrics_header_added = False
        results = []
        for id in sanity_results:
            for buggy_value in sanity_results[id]:
                for non_buggy_value in sanity_results[id][buggy_value]:
                    for alpha in sanity_results[id][buggy_value][non_buggy_value]:
                        metrics = sanity_results[id][buggy_value][non_buggy_value][alpha].metrics
                        header = sorted(metrics)
                        if not metrics_header_added:
                            results_header.extend(header)
                            results.append(results_header)
                        results.append([id, buggy_value, non_buggy_value, alpha] + map(lambda h: metrics[h], header))
        with open(self.dir_structure.sanity, "wb") as f:
            csv.writer(f).writerows(results)


class SanityMatrix(object):
    BUGGY_RANGE = [0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
    NON_BUGGY_RANGE = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6]
    ALPHA_RANGE = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]

    def __init__(self, dir_id):
        self.dir_id = dir_id
        self.matrix_id = dir_id.id
        if not os.path.exists(self.dir_id.matrices):
            return
        ei = read_json_planning_file(self.dir_id.matrices)
        self.components_names = copy.deepcopy(Experiment_Data().COMPONENTS_NAMES)
        self.bugs = copy.deepcopy(Experiment_Data().BUGS)
        self.pool = copy.deepcopy(Experiment_Data().POOL)

    def generate_influence_data(self, buggy_value, non_buggy_value, alpha):
        data = {"experiment_type": "influence", "influence_alpha": alpha}
        influence_matrix = dict()
        for test in self.pool:
            influence_matrix[test] = dict()
            for component in self.pool[test]:
                if component in self.bugs:
                    influence_matrix[test][self.components_names[component]] = buggy_value
                else:
                    influence_matrix[test][self.components_names[component]] = non_buggy_value
        data["influence_matrix"] = influence_matrix
        return data

    def sanity(self):
        if not os.path.exists(self.dir_id.matrices):
            return
        if not os.path.exists(self.dir_id.sanity_experiments):
            results = dict()
            with open(self.dir_id.matrices) as f:
                json_matrix = json.loads(f.read())
            for buggy_value, non_buggy_value, alpha in product(SanityMatrix.BUGGY_RANGE, SanityMatrix.NON_BUGGY_RANGE, SanityMatrix.ALPHA_RANGE):
                print buggy_value, non_buggy_value, alpha
                influence_data = self.generate_influence_data(buggy_value, non_buggy_value, alpha)
                matrix = copy.deepcopy(json_matrix)
                matrix.update(influence_data)
                ei = read_json_planning_instance(matrix)
                ei.diagnose()
                results.setdefault(buggy_value, dict()).setdefault(non_buggy_value, dict())[alpha] = Diagnosis_Results(ei.diagnoses, ei.initial_tests, ei.error)
            with open(self.dir_id.sanity_experiments, "wb") as f:
                json.dump(results, f)
        with open(self.dir_id.sanity_experiments) as f:
            return json.loads(f.read())


if __name__ == "__main__":
    SanityMatrix(DirId(DirStructure(r"C:\amirelm\component_importnace\data\d4j_lang8"), sys.argv[1])).sanity()
    # exit()
    # SanityExperiment(DirStructure(r"C:\amirelm\component_importnace\data\d4j_lang8")).sanity()
    # pass