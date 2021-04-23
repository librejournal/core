import os

def read_env_vars(file):
    vars_dict = {}
    for line in file.readlines():
        if line.startswith("#"):
            # pass comment line
            continue
        splitted = line.split("=")
        vars_dict[splitted[0]] = splitted[1]
    return vars_dict

def open_env_file(filepath):
    file = open(filepath, "r")
    return file

def update_environ(env_dict):
    os.environ.update(env_dict)

def read_from_path_and_update(filepath):
    file = open_env_file(filepath)
    vars_dict = read_env_vars(file)
    update_environ(vars_dict)
