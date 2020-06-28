import sys
from run_process import main
from experiment import Experiment, ExperimentMatrix
from multiprocessing import Pool, Manager
from subprocess import Popen
from dir_structure import DirStructure
from bug_miner_reproducer import BugMinerReproducer
import os
from multiprocessing import Pool, Manager
from subprocess import Popen
from functools import partial

DIR_BASE_PATH = r"Z:\component_importance"
NUM_PROCCESSES = 1

def run_process(cmd_args):
    print "Running", cmd_args
    proc = Popen([sys.executable] + cmd_args)
    proc.communicate()

def exec_file(file_name, cmds):
    run_process([file_name] + cmds)

def exec_do_all(commit, dir_path, project_name):
    exec_file("bug_miner_reproducer.py", [dir_path, project_name, commit])

def exec_training_set(commit, dir_path, project_name):
    exec_file("bug_miner_reproducer.py", [dir_path, project_name, commit, 'training'])

def exec_experiment(commit, dir_path):
    exec_file("experiment.py", [dir_path, commit])


def experiment_execute(project, dir_path):
    ExperimentMatrix.experiment_classifiers(DirId(DirStructure(dir_path), project))


def execute(func, iter, num_processes=NUM_PROCCESSES):
    p = Pool(num_processes)
    p.map(func, iter)
    p.join()
    p.close()


def full_experiment(bug_miner_project_name, dir_base_path=DIR_BASE_PATH, num_processes=NUM_PROCCESSES):
    dir_path = os.path.join(dir_base_path, bug_miner_project_name)
    projects = BugMinerReproducer.read_bug_miner_csv(dir_path, bug_miner_project_name)
    execute(partial(exec_do_all, dir_path=dir_path, project_name=bug_miner_project_name), projects.keys(), num_processes)
    execute(partial(exec_training_set, dir_path=dir_path, project_name=bug_miner_project_name), projects.keys(), num_processes)
    execute(partial(exec_experiment, dir_path=dir_path), projects.keys(), num_processes)
    Experiment(DirStructure(dir_path)).experiment()


if __name__ == "__main__":
    full_experiment(*sys.argv[1:])