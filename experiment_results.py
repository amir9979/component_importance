from run_process import main_cmds
from tempfile import mktemp
from experiment import Experiment
from dir_structure import DirStructure, DirId
import sys
from  feature_extraction import  FeatureExtraction


class ExperimentResults(object):
    def __init__(self, dir_name):
        self.dir_name = dir_name
        self.dir_structure = DirStructure(dir_name)
        self.ids = self.dir_structure.get_marked_ids()

    def results(self, num_procesess=10):
        # map(lambda id: FeatureExtraction(DirId(self.dir_structure, id)).get_training_set(), self.ids)
        main_cmds(num_procesess, map(lambda x: [sys.executable, "experiment.py", self.dir_name, x], self.ids))
        Experiment(self.dir_structure).experiment()


if __name__ == "__main__":
    ExperimentResults(r"C:\amirelm\component_importnace\data\maven_3").results()