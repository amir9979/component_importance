from project_fixer import project_fixer
from d4j import D4JReproducer
import os
import sys


class D4JJoda(D4JReproducer):
    REPO = r"C:\temp\defects4j-joda"
    D4J_DIR = os.path.realpath(os.path.join(os.path.dirname(__file__), r"projects\time"))

    def __init__(self, id, buggy, fixed, bug_key, bug_url, json_data, dir_id):
        super(D4JJoda, self).__init__(id, buggy, fixed, bug_key, bug_url, json_data, dir_id)

    def get_repo(self):
        return D4JJoda.REPO

    def get_patches_dir(self):
        return os.path.join(D4JJoda.D4J_DIR, "patches")

    def fix(self):
        pass


if __name__ == "__main__":
    projects = D4J.read_commit_db(r"C:\amirelm\component_importnace\data\_math", 'Math')
    projects[16].do_all()