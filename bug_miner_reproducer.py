import csv
import json
import git
import os
from subprocess import Popen
from dir_structure import DirStructure, DirId
import javadiff.diff
import sys
from reproducer import Reproducer
from subprocess import Popen
import tempfile
from ast import literal_eval


class BugMinerReproducer(Reproducer):
    BUG_MINER_DIR = os.path.realpath(os.path.join(os.path.dirname(__file__), r"bug_miner"))
    BUG_MINER_REPOS_DIR = os.path.realpath(r"Z:\ev_repos")

    def __init__(self, id, failing_tests, dir_id, repo_path, diffs, blamed_components, fix):
        super(BugMinerReproducer, self).__init__(id, map(lambda t: t.replace("#", "."), failing_tests), dir_id)
        self.repo_path = repo_path
        self.parent = id
        self.diffs = diffs
        self.blamed_components = reduce(list.__add__, map(lambda x: x.split("@"), blamed_components), [])
        self.fix_commit = fix

    def get_repo(self):
        return self.repo_path

    def clone(self):
        Popen(['git', 'clone', self.get_repo(), self.get_dir_id().clones]).wait()
        Popen(['git', '-C', self.get_dir_id().clones, "checkout", self.parent]).wait()

    def apply_patch(self):
        for diff in self.diffs:
            if literal_eval(diff):
                f, path_to_diff = tempfile.mkstemp()
                os.close(f)
                with open(path_to_diff, "w") as f:
                    f.write(literal_eval(diff) + "\n")
                    f.flush()
                repo = git.Repo(self.dir_id.clones)
                repo.git.apply("--whitespace=nowarn", path_to_diff)
                os.remove(path_to_diff)

    def fix(self):
        # Popen(['git', '-C', self.get_dir_id().clones, "checkout", self.fix_commit]).wait()
        pass

    def extract_buggy_functions(self):
        return self.blamed_components

    def get_non_pass_outcomes(self):
        return ['failure']

    # def clear(self):
    #     git.Repo(self.get_dir_id().clones).git.checkout('--', '.')

    @staticmethod
    def read_bug_miner_csv(dir_path, project_name):
        l = list(csv.reader(open(os.path.join(BugMinerReproducer.BUG_MINER_DIR, project_name + ".csv"))))
        header = l[0]
        ans = dict()
        commits = dict()
        map(lambda x: commits.setdefault(x['parent'], []).append(x), map(lambda x: dict(zip(header, x)), l[1:]))
        for bug_data in commits:
            ans[bug_data] = BugMinerReproducer(bug_data, list(set(map(lambda x: x['testcase'], commits[bug_data]))),
                               DirId(DirStructure(dir_path), bug_data),
                               os.path.join(BugMinerReproducer.BUG_MINER_REPOS_DIR, project_name), list(set(map(lambda x: x['diff'], commits[bug_data]))), list(set(map(lambda x: x['blamed_components'], commits[bug_data]))), list(set(map(lambda x: x['commit'], commits[bug_data]))))
        return ans


if __name__ == "__main__":
    projects = BugMinerReproducer.read_bug_miner_csv(sys.argv[1], sys.argv[2])
    if len(sys.argv) == 4:
        sorted(projects.items(), key=lambda x: x[0])[int(sys.argv[3])][1].do_all()
    else:
        sorted(projects.items(), key=lambda x: x[0])[int(sys.argv[3])][1].get_training_set()
