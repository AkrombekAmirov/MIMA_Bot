from os.path import join, dirname


async def get_file_path(name: str):
    return join(dirname(__file__), name)

async def join_file(file_name):
    return join('file_service', file_name)
