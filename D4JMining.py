from project_fixer import project_fixer
from d4j import D4JReproducer
import os
import sys


class D4JMining(D4JReproducer):
    REPO = r"C:\temp\defects4j-math"
    D4J_DIR = os.path.realpath(os.path.join(os.path.dirname(__file__), r"projects\math"))

    def __init__(self, id, fixed, failing_tests, dir_id):
        super(D4JMining, self).__init__(id, fixed, failing_tests, dir_id)

    def get_repo(self):
        return D4JMining.REPO

    def get_patches_dir(self):
        return os.path.join(D4JMath.D4J_DIR, "patches")

    def fix(self):
        fixer = project_fixer(self.get_dir_id().clones)

        fixer.clear_test_in_files("void test", high_runtime)


if __name__ == "__main__":
    projects = D4JReproducer.read_commit_db(r"C:\amirelm\component_importnace\data\_math6", 'Math')
    projects[18].do_all()