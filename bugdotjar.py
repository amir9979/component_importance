import json
import os
import git
import sys
from reproducer import Reproducer
from subprocess import Popen
from tempfile import mktemp
from dir_structure import DirStructure, DirId
import javadiff.diff


class BugDotJar(Reproducer):
    BugDotJar_repo = r"https://github.com/bugs-dot-jar/{0}.git"
    BugDotJar_JSON = os.path.realpath(os.path.join(os.path.dirname(__file__), r"bugdotjar-bugs.json"))

    def __init__(self, id, failing_tests, dir_id, commit, project=None):
        super(BugDotJar, self).__init__(id, failing_tests, dir_id)
        self.commit = commit
        self.project = project

    def apply_patch(self):
        # the checkout itself is buggy
        pass

    def extract_buggy_functions(self):
        repo = git.Repo(self.get_dir_id().clones)
        repo.git.apply(os.path.join(self.get_dir_id().clones, ".bugs-dot-jar", "developer-patch.diff"))
        buggy = map(lambda x: x.split("@")[1].lower().replace(',', ';'),
                   javadiff.diff.get_modified_functions(self.get_dir_id().clones))
        repo.git.checkout('-f', '--', '.', )
        return buggy

    def clone(self):
        Popen(['git', 'clone', self.get_repo(), self.get_dir_id().clones]).wait()
        git_repo = git.Repo(self.get_dir_id().clones)
        branches = filter(lambda x: self.commit in x, map(lambda x: x.split('/')[-1], git_repo.git.branch('-a').split('\n')))
        assert len(branches) == 1
        Popen(['git', '-C', self.get_dir_id().clones, "checkout", branches[0]]).wait()

    def fix(self):
        for root, dirs, files in os.walk(self.get_repo()):
            for file_name in filter(lambda x: x.endswith('.sh'), files):
                with open(file_name) as f:
                    lines = map(lambda x: x.replace('\r', ''), f.readlines())
                with open(file_name, "wb") as f:
                    f.writelines(lines)

    def get_repo(self):
        return BugDotJar.BugDotJar_repo.format(self.project)

    @staticmethod
    def read_bugs_json(project, dir_path=None):
        if dir_path is None:
            dir_path = os.path.join(r"C:\amirelm\component_importnace\data", project+"_1")
            if not os.path.exists(dir_path):
                os.mkdir(dir_path)
        assert dir_path
        bugs = filter(lambda b: b['project'].lower() == project.lower(), json.load(open(BugDotJar.BugDotJar_JSON)))
        projects = []
        for bug in bugs:
            commit = bug['commit']
            failing_tests = map(lambda f: ".".join(list(reversed(f.split()[0].split(':')[0].replace(')', '').replace('#', '.').split('(')))).lower(), bug['failing_tests'])
            projects.append(BugDotJar(id, failing_tests, DirId(DirStructure(dir_path), bug['jira_id'] + "_" + commit), commit, project))
        return projects

    @staticmethod
    def project_class(project):
        project_dict = {}
        return project_dict.get(project)


if __name__ == "__main__":
    projects = BugDotJar.read_bugs_json(sys.argv[1])
    projects[int(sys.argv[2])].save_traces()