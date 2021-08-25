from project_fixer import project_fixer
from d4j import D4JReproducer
from dir_structure import DirStructure, DirId
from reproducer import Reproducer
import os
import sys
import pandas as pd
import json
import shutil
from jcov_parser import JcovParser
import xml.etree.cElementTree as et
et.register_namespace('', "http://maven.apache.org/POM/4.0.0")
et.register_namespace('xsi', "http://www.w3.org/2001/XMLSchema-instance")


class TestResult(object):
    def __init__(self, full_name, outcome):
        self.full_name = full_name
        self.outcome = outcome

    def __repr__(self):
        return "{full_name}: {outcome}".format(full_name=self.full_name, outcome=self.outcome)

    def is_passed(self):
        return self.outcome == 'pass'

    def get_observation(self):
        return 0 if self.is_passed() else 1

    def as_dict(self):
        return {'_test_name': self.full_name, '_outcome': self.outcome}


class D4JMining(D4JReproducer):
    REPO = r"https://github.com/apache/commons-lang.git"
    D4J_DIR = os.path.realpath(os.path.join(os.path.dirname(__file__), r"d4j_miner"))
    D4J_PREFIX = "bug-mining_"

    def __init__(self, id, fixed, failing_tests, dir_id, bug_mining_dir):
        super(D4JMining, self).__init__(id, fixed, failing_tests, dir_id)
        self.bug_mining_dir = bug_mining_dir
        self.matrix = os.path.join(self.bug_mining_dir, f"matrix_{id}.json")
        self.init_data()
        self.opt_traces = []
        with open(os.path.join(self.bug_mining_dir, 'test_details.json')) as f:
            self.opt_traces = json.loads(f.read())
        self.set_optimized_traces(self.get_optimized_traces())

    def init_data(self):
        traces = list(JcovParser(None, [os.path.join(self.bug_mining_dir, 'result.xml')], True, True).parse(False))[
                0].split_to_subtraces()
        self.set_traces(traces)
        tests_to_trace = []
        for t in traces:
            tests_to_trace.append(TestResult(t, 'failure' if t in self.failing_tests else 'pass'))
        self.set_tests_to_trace(tests_to_trace)
        self.set_surefire_tests(dict(map(lambda x: (x.full_name, x), tests_to_trace)))

    def save_tests_results(self):
        data = dict(map(lambda x: (x[0], x[2] == 'pass'), self.opt_traces))
        with open(self.get_dir_id().tests_results, "w") as f:
            json.dump(data, f)

    def get_repo(self):
        return D4JMining.REPO

    def get_patches_dir(self):
        return os.path.join(self.bug_mining_dir, "patches")

    def clean_execution(self):
        pass

    def extract_tests_to_trace(self):
        return True

    def extract_buggy_functions(self):
        with open(os.path.join(self.bug_mining_dir, 'bugs.json')) as f:
            return json.loads(f.read())

    def fix(self):
        fixer = project_fixer(self.get_dir_id().clones)

        # fixer.clear_test_in_files("void test", high_runtime)

    def trace(self, trace_failed=False):
        pass

    def get_optimized_traces(self):
        return dict(map(lambda x: (x[0], self.test_traces[x[0]]), self.opt_traces))

    def save_as_sfl_matrix(self):
        shutil.copyfile(self.matrix, self.get_dir_id().matrices)

    @staticmethod
    def read_data_dir(dir_path, ind):
        bug_mining = os.path.join(os.path.join(D4JMining.D4J_DIR, D4JMining.D4J_PREFIX + ind), 'framework', 'projects')
        bug_mining = os.path.abspath(os.path.join(bug_mining, os.listdir(bug_mining)[0]))
        active_bugs = os.path.join(bug_mining, "active-bugs.csv")
        trigger_tests = os.path.join(bug_mining, "trigger_tests")
        path_to_trigger_tests = os.path.join(trigger_tests, os.listdir(trigger_tests)[0])
        df = pd.read_csv(active_bugs)
        bug_row = df[df['bug.id'] == int(ind)]
        id, fixed = list(bug_row[["bug.id", "revision.id.fixed"]].iterrows())[0][1].to_list()
        failing_tests = []
        with open(path_to_trigger_tests) as f:
            failing_tests = list(
                map(lambda x: x[4:-1].replace('::', '.').lower(), filter(lambda l: l.startswith('---'), f.readlines())))
        return D4JMining(id, fixed, failing_tests, DirId(DirStructure(dir_path), str(id)), bug_mining)


if __name__ == "__main__":
    project = D4JMining.read_data_dir(sys.argv[1], sys.argv[2])
    if len(sys.argv) == 3:
        project.do_all()
    else:
        project.get_training_set()

