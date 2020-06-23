import sys
from run_process import main
from experiment import Experiment
from multiprocessing import Pool, Manager
from subprocess import Popen
from dir_structure import DirStructure

def full_experiment(reproducer_cmds_path, reproducer_training_cmds_path, experiment_path, dir_path):
    main(10, reproducer_cmds_path)
    main(10, reproducer_training_cmds_path)
    main(10, experiment_path)
    Experiment(DirStructure(dir_path)).experiment()


if __name__ == "__main__":
    full_experiment(*sys.argv[1:])