import os

def find_project_root():
    """
    找到项目的根目录。包含requirements.txt或config.json的视为根目录
    """

    current_file_path = os.path.abspath(os.getcwd())

    root_folder = current_file_path

    while True:

        if (
            os.path.isfile(os.path.join(root_folder, "requirements.txt"))
            or os.path.isfile(os.path.join(root_folder, "pandasai.json"))
        ):
            break

        parent_folder = os.path.dirname(root_folder)
        if parent_folder == root_folder:
            return os.getcwd()

        root_folder = parent_folder

    return root_folder

def concat_path(filename):
    return os.path.join(find_project_root(), filename)