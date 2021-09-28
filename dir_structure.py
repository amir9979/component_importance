import os
import time
import shutil


class DirStructure(object):
    DIRS = ["clones", "mvn_outputs", "matrices", "traces", "traces_json", "call_graphs", "execution_graphs",
            "javadoc", "files_packages", "files_commits", "mark", "bugs", "experiments", "experiments_df", "files_functions",
            "labels", "features", "labeled_data", "unlabeled_data", "training_set", "testing_set", "files_traces", "tests_results",
            "feature_importance", "classification_metrics", "training_describe", "testing_describe", "experiment_matrices"]
    RESULTS = ["experiment", "classification_evaluate"]

    def __init__(self, base_path):
        self.base_path = os.path.abspath(base_path)
        for dir in DirStructure.DIRS:
            setattr(self, dir, DirStructure.mkdir(os.path.join(self.base_path, dir)))
        for dir in DirStructure.RESULTS:
            setattr(self, dir, os.path.join(self.base_path, dir))

    def get_marked_ids(self):
        ids = list(map(lambda d: DirId(self, d), os.listdir(self.mark)))
        assert all(list(map(lambda x: x.is_marked(), ids)))
        return list(map(lambda x: x.id, ids))

    @staticmethod
    def mkdir(path):
        if os.path.exists(path):
            return path
        for _ in range(10):
            if not os.path.exists(path):
                try:
                    os.makedirs(path)
                    if not os.path.exists(path):
                        time.sleep(1)
                except Exception as e:
                    time.sleep(1)
        return path


class DirId(object):
    def __init__(self, dir_structure, id):
        self.dir_structure = dir_structure
        self.id = id
        for dir in DirStructure.DIRS:
            setattr(self, dir, os.path.join(DirStructure.mkdir(getattr(dir_structure, dir)), id))

    def read_file(self, attr):
        with open(getattr(self, attr)) as f:
            return f.read()

    def is_marked(self):
        return os.path.exists(self.mark)

    def cleanup(self):
        shutil.rmtree(self.clones, ignore_errors=True)

    def full_cleanup(self):
        shutil.rmtree(self.clones, ignore_errors=True)
        shutil.rmtree(self.javadoc, ignore_errors=True)
        shutil.rmtree(self.files_commits, ignore_errors=True)
        shutil.rmtree(self.files_functions, ignore_errors=True)
        shutil.rmtree(self.execution_graphs, ignore_errors=True)
        shutil.rmtree(self.unlabeled_data, ignore_errors=True)
        shutil.rmtree(self.call_graphs, ignore_errors=True)
        shutil.rmtree(self.files_packages, ignore_errors=True)
