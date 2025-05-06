from os.path import join, dirname


async def get_test_file_path(name: str):
    return join(dirname(__file__), name)


async def join_test_file(file_name):
    return join('file_service/test_file', file_name)
