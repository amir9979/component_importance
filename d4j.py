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


class D4JReproducer(Reproducer):
    D4J_DIR = os.path.realpath(os.path.join(os.path.dirname(__file__), r"projects"))
    D4J_JSON = os.path.realpath(os.path.join(os.path.dirname(__file__), r"defects4j-bugs.json"))

    def __init__(self, id, fixed, failing_tests, dir_id):
        super(D4JReproducer, self).__init__(id, failing_tests, dir_id)
        self.fixed = fixed

    def apply_patch(self):
        repo = git.Repo(self.get_dir_id().clones)
        test_patch = os.path.join(self.get_patches_dir(), self.get_id()) + ".src.patch"
        if os.path.exists(test_patch):
            repo.git.apply(test_patch)

    def clone(self):
        Popen(['git', 'clone', self.get_repo(), self.get_dir_id().clones]).wait()
        Popen(['git', '-C', self.get_dir_id().clones, "checkout", self.fixed]).wait()

    def extract_buggy_functions(self):
        return map(lambda x: x.split("@")[1].lower().replace(',', ';'), javadiff.diff.get_modified_functions(self.get_dir_id().clones))

    @staticmethod
    def read_commit_db(dir_path, project='Lang'):
        d4j = json.load(open(D4JReproducer.D4J_JSON))
        project_data = dict(map(lambda x: (str(x['bugId']), x), filter(lambda x: x['project'].lower() == project.lower(), d4j)))
        projects = []
        with open(os.path.join(D4JReproducer.D4J_DIR, project, "commit-db")) as f:
            for id, buggy, fixed, bug_key, bug_url in csv.reader(f):
                failing_tests = map(lambda x: "{0}.{1}".format(x['className'], x['methodName']).strip().lower(),
                                    project_data[id]['failingTests'])
                projects.append(D4JReproducer.project_class(project)(id, fixed, failing_tests, DirId(DirStructure(dir_path), id)))
        return projects

    @staticmethod
    def project_class(project='Lang'):
        from d4j_lang import D4JLang
        from d4j_math import D4JMath
        project_dict = {'Lang': D4JLang, 'Math': D4JMath}
        return project_dict.get(project)


if __name__ == "__main__":
    projects = D4JReproducer.read_commit_db(sys.argv[1], sys.argv[2])
    projects[int(sys.argv[3])].do_all()
    # projects[int(sys.argv[1])].labels()
    # projects[int(sys.argv[1])].save_traces()
