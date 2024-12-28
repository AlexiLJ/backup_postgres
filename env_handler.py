import json
from pathlib import Path

def get_git_parent_dir(path):
    return Path(path) / '.git'

def get_active_branch_name(path) -> str:
    """
    :return: str
    """
    hidden_dir = get_git_parent_dir(path) / "HEAD"
    hidden_dir.chmod(0o444)
    with open(hidden_dir) as f:
        content = f.read().splitlines()
    for line in content:
        if line[0:4] == "ref:":
            return line.partition("refs/heads/")[2]


def var_getter(name: str, path):
    '''
    Getting sys. variables based on the git branch
    :param name: str name of the sys. variable
    :param storage: str|None
    :return: Any
    '''
    branch = get_active_branch_name(path)
    pathes = Path(__file__).parent.resolve() / "pathes.json"
    with open(pathes, "r") as p:
        storage = json.load(p).get(branch)  # environment variables
    with open(Path(storage)) as st:
        var = json.load(st).get(name)
    return var

