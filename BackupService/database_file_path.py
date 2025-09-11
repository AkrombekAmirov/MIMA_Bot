from os.path import join, dirname


def get_file_path(name: str):
    return join(dirname(__file__), name)