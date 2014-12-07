
class EnvironmentNotDefined(Exception):
    environment = ""
    def __init__(self, environment):
        self.environment = environment

    def __str__(self):
        return "Environment %s not defined for this language" % self.environment

class Environment:
    """
    base class for all language environments
    """
    virtenv_path = ""
    repo_path = ""

    def __init__(self, virtenv_path, repo_path):
        self.virtenv_path = virtenv_path
        self.repo_path = repo_path
