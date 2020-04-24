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


class BugMinerReproducer(Reproducer):
    BUG_MINER_DIR = os.path.realpath(os.path.join(os.path.dirname(__file__), r"bug_miner"))

    def __init__(self, id, failing_tests, dir_id):
        super(BugMinerReproducer, self).__init__(id, failing_tests, dir_id)

    def get_repo(self):
        pass

    def clone(self):
        pass

    def get_patches_dir(self):
        pass

    def apply_patch(self):
        pass

    def fix(self):
        pass

    def extract_buggy_functions(self):
        pass

    def clear(self):
        # git.Repo(self.get_dir_id().clones).git.checkout('--', '.')
        pass


    @staticmethod
    def read_bug_miner_csv(dir_path, project_name):
        pass

if __name__ == "__main__":
    projects = BugMinerReproducer.read_commit_db(sys.argv[1], sys.argv[2])
    projects[int(sys.argv[3])].do_all()
