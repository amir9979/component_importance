import os


class DirStructure(object):
    DIRS = ["clones", "mvn_outputs", "matrices", "traces", "traces_json", "call_graphs", "execution_graphs",
            "javadoc", "files_packages", "files_commits", "mark", "bugs", "experiments", "files_functions",
            "labels", "features", "labeled_data", "unlabeled_data", "training_set", "testing_set", "files_traces", "tests_results",
            "feature_importance", "classification_metrics", "training_describe", "testing_describe", "experiment_matrices"]
    RESULTS = ["experiment", "classification_evaluate"]

    def __init__(self, base_path):
        self.base_path = base_path
        for dir in DirStructure.DIRS:
            setattr(self, dir, DirStructure.mkdir(os.path.join(self.base_path, dir)))
        for dir in DirStructure.RESULTS:
            setattr(self, dir, os.path.join(self.base_path, dir))

    def get_marked_ids(self):
        ids = map(lambda d: DirId(self, d), os.listdir(self.mark))
        assert all(map(lambda x: x.is_marked(), ids))
        return map(lambda x: x.id, ids)

    @staticmethod
    def mkdir(path):
        if os.path.exists(path):
            return path
        for _ in range(10):
            if not os.path.exists(path):
                try:
                    os.mkdir(path)
                except:
                    pass
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