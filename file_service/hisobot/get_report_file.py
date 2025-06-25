from os.path import join, dirname


async def get_report_file_path(name: str):
    return join(dirname(__file__), name)