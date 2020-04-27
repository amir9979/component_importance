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

    def __init__(self, id, failing_tests, dir_id, repo_path, **kwargs):
        super(BugMinerReproducer, self).__init__(id, [failing_tests.replace("#", ".")], dir_id)
        self.repo_path = repo_path
        for k in kwargs:
            setattr(self, k, kwargs[k])

    def get_repo(self):
        return self.repo_path

    def clone(self):
        Popen(['git', 'clone', self.get_repo(), self.get_dir_id().clones]).wait()
        Popen(['git', '-C', self.get_dir_id().clones, "checkout", self.parent]).wait()

    def apply_patch(self):
        f, path_to_diff = tempfile.mkstemp()
        os.close(f)
        with open(path_to_diff, "w") as f:
            f.write(literal_eval(self.diff) + "\n")
            f.flush()
        repo = git.Repo(self.dir_id.clones)
        repo.git.apply("--whitespace=nowarn", f.name)
        os.remove(path_to_diff)

    def fix(self):
        pass

    def extract_buggy_functions(self):
        return self.blamed_components.split("@")

    def get_non_pass_outcomes(self):
        return ['failure']


    def clear(self):
        git.Repo(self.get_dir_id().clones).git.checkout('--', '.')

    @staticmethod
    def read_bug_miner_csv(dir_path, project_name):
        l = list(csv.reader(open(os.path.join(BugMinerReproducer.BUG_MINER_DIR, project_name + ".csv"))))
        header = l[0]
        ans = []
        for bug_data in map(lambda x: dict(zip(header, x)), l[1:]):
            ans.append(BugMinerReproducer(bug_data['issue'], bug_data['testcase'],
                                      DirId(DirStructure(dir_path), bug_data['issue']),
                                     os.path.join(BugMinerReproducer.BUG_MINER_REPOS_DIR, project_name), **bug_data))
        return ans


if __name__ == "__main__":
    projects = BugMinerReproducer.read_bug_miner_csv(sys.argv[1], sys.argv[2])
    projects[int(sys.argv[3])].do_all()
