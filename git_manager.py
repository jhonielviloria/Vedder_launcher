import subprocess

class GitManager:
    def __init__(self, project_dir):
        self.project_dir = project_dir

    def is_git_repo(self):
        return subprocess.run(
            ["git", "rev-parse", "--is-inside-work-tree"],
            cwd=self.project_dir,
            capture_output=True,
            text=True
        ).returncode == 0

    def fetch(self):
        subprocess.run(["git", "fetch"], cwd=self.project_dir, check=True)

    def get_commits(self, count=20):
        result = subprocess.check_output(
            ["git", "log", f"-n{count}", "--pretty=format:%h %cd - %s", "--date=format:%d-%m-%Y"],
            cwd=self.project_dir,
            text=True
        )
        return result.strip().splitlines()

    def reset_hard(self, commit_hash):
        subprocess.run(["git", "reset", "--hard", commit_hash], cwd=self.project_dir, check=True)

    def get_current_commit(self):
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=self.project_dir, text=True).strip()

    def update(self):
        return subprocess.run(["git", "pull"], cwd=self.project_dir, capture_output=True, text=True, check=True)
