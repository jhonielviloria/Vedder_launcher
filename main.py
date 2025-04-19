import flet as ft
import os
import subprocess
import configparser
from tkinter import Tk
from tkinter.filedialog import askdirectory
from git_manager import GitManager

CONFIG_PATH = "config.ini"
# Define the file path and content
config_file_path = "config.txt"
config_content = """[DEFAULT]
project_directory = C:\\Vedder_app\\Vedder_async
venv_python = C:\\
auto_update = False
"""

# Check if the file exists, and create it if it doesn't
if not os.path.exists(CONFIG_PATH):
    with open(CONFIG_PATH, "w") as config_file:
        config_file.write(config_content)

class Launcher(ft.Tabs):
    def __init__(self):
        super().__init__()
        self.config = configparser.ConfigParser()
        self.config.read(CONFIG_PATH)
        self.file_picker = ft.FilePicker(on_result=self.on_path_selected)

        self.project_dir = self.config["DEFAULT"]["project_directory"]
        self.venv_python = self.config["DEFAULT"]["venv_python"]
        self.auto_update = self.config["DEFAULT"].getboolean("auto_update", fallback=False)

        self.git = GitManager(self.project_dir)

        # UI Components
        self.status_text = ft.Text()
        self.current_version_text = ft.Text("Current Version: Unknown", size=14)
        self.commit_dropdown = ft.Dropdown(label="Select Git Commit", width=400)
        self.commit_count_dropdown = ft.Dropdown(
            label="Number of Commits",
            options=[ft.dropdown.Option(str(i)) for i in [5, 10, 20, 50]],
            value="20",
            width=150
        )
        self.load_commits_btn = ft.ElevatedButton(text="Load Commits", on_click=self.load_commits)
        self.checkout_commit_btn = ft.ElevatedButton(text="Reset to Version", on_click=self.reset_commit, bgcolor="lightblue", color="black")
        self.update_btn = ft.ElevatedButton(text="Update to Latest", on_click=self.update_repo, bgcolor="lightblue", color="black")
        # self.btn_launch = ft.ElevatedButton(text="Launch App", on_click=self.launch_app, bgcolor="lightgreen", color="black")
        self.btn_launch = ft.ElevatedButton(
            content=ft.Container(
                content=ft.Row(
                    controls=[
                        ft.Icon(ft.Icons.ROCKET_LAUNCH_SHARP, size=40, color='black'),
                        ft.Text('Launch \nVedder Admin', text_align='center', color='black', weight=ft.FontWeight.BOLD),
                    ],
                ),
                height=100,
                width=150,
                alignment=ft.alignment.center,
            ),
            on_click=self.launch_app,
            bgcolor='lightgreen',
        )
        self.auto_update_cb = ft.Checkbox(
            label="Auto Update",
            value=self.auto_update,
            on_change=self.update_config_auto_update
        )

        # Tab 1: Launcher
        tab_1 = ft.Tab(
            text="Launcher",
            content=ft.Container(
                padding=20,
                content=ft.Column([
                    self.btn_launch,
                    self.auto_update_cb,
                    ft.Divider(),
                    ft.ExpansionTile(
                        title=ft.Text("Version Control"),
                        subtitle=self.current_version_text,
                        controls=[
                            ft.Container(
                                content=self.update_btn,
                                alignment=ft.alignment.center_left,
                                padding=15,
                            ),
                            ft.Row([self.commit_count_dropdown, self.load_commits_btn]),
                            ft.Row([self.commit_dropdown, ]),

                            ft.Container(
                                content=self.checkout_commit_btn,
                                alignment=ft.alignment.center_left,
                                padding=15,
                            ),
                            self.status_text
                        ]
                    )
                ])
            )
        )

        # Tab 2: Settings
        self.project_dir_tf = ft.TextField(label="Project Directory", value=self.project_dir, expand=True)
        self.venv_python_tf = ft.TextField(label="Virtual Env Python", value=self.venv_python, expand=True)

        self.project_dir_btn = ft.IconButton(
            icon=ft.Icons.FOLDER,
            tooltip="Browse Project Directory",
            on_click=lambda e: self.select_path("project_directory")
        )
        self.venv_python_btn = ft.IconButton(
            icon=ft.Icons.FOLDER,
            tooltip="Browse Python Executable",
            on_click=lambda e: self.select_path("venv_python")
        )
        self.auto_find_python_btn = ft.IconButton(
            icon=ft.Icons.AUTORENEW,
            tooltip="Auto-find Python Executable",
            on_click=self.auto_find_python
        )

        tab_2 = ft.Tab(
            text="Settings",
            content=ft.Container(
                padding=20,
                content=ft.Column([
                    ft.Row([self.project_dir_tf, self.project_dir_btn]),
                    ft.Row([self.venv_python_tf, self.venv_python_btn, self.auto_find_python_btn])
                ])
            )
        )

        self.tabs = [tab_1, tab_2]

    def update_config_auto_update(self, e):
        self.config["DEFAULT"]["auto_update"] = str(e.control.value)
        with open(CONFIG_PATH, "w") as configfile:
            self.config.write(configfile)

    def launch_app(self, e):
        if self.auto_update_cb.value:
            self.update_repo()
        command = f'cd "{self.project_dir}" && "{self.venv_python}" main.py'
        subprocess.run(command, shell=True)

    def load_commits(self, e=None):
        if not self.git.is_git_repo():
            self.status_text.value = "❌ Not a Git repo"
            self.status_text.update()
            return

        try:
            self.git.fetch()
            count = int(self.commit_count_dropdown.value)
            commits = self.git.get_commits(count)
            self.commit_dropdown.options = [ft.dropdown.Option(commit) for commit in commits]
            self.commit_dropdown.update()
            self.status_text.value = f"✅ Loaded {len(commits)} commits"
        except Exception as ex:
            self.status_text.value = f"❌ Failed to load commits: {str(ex)}"
        self.status_text.update()
        self.update_version_display()

    def reset_commit(self, e):
        selected = self.commit_dropdown.value
        if not selected:
            self.status_text.value = "❗ Select a commit"
        else:
            try:
                commit_hash = selected.split()[0]
                self.git.reset_hard(commit_hash)
                self.status_text.value = f"✅ Reset to {commit_hash}"
            except Exception as ex:
                self.status_text.value = f"❌ Reset failed: {str(ex)}"
        self.status_text.update()
        self.update_version_display()

    def update_repo(self, e=None):
        try:
            result = self.git.update()
            self.status_text.value = f"✅ Updated:\n{result.stdout}"
        except Exception as ex:
            self.status_text.value = f"❌ Update failed: {str(ex)}"
        self.status_text.update()
        self.update_version_display()

    def update_version_display(self):
        try:
            current = self.git.get_current_commit()
            self.current_version_text.value = f"Current Version: {current[:7]}"
        except:
            self.current_version_text.value = "Current Version: Unknown"
        self.current_version_text.update()

    def on_path_selected(self, e: ft.FilePickerResultEvent):
        if not e.path:
            return  # Cancelled

        if self.pending_config_key == "venv_python":
            full_path = os.path.join(e.path, "python.exe")
        else:
            full_path = e.path.replace("/", "\\")

        self.config["DEFAULT"][self.pending_config_key] = full_path
        with open(CONFIG_PATH, "w") as f:
            self.config.write(f)

        if self.pending_config_key == "project_directory":
            self.project_dir = full_path
            self.git.project_dir = full_path
            self.project_dir_tf.value = full_path
        else:
            self.venv_python = full_path
            self.venv_python_tf.value = full_path

        self.project_dir_tf.update()
        self.venv_python_tf.update()

    def select_path(self, config_key):
        self.pending_config_key = config_key
        self.file_picker.get_directory_path()

    # def select_path(self, config_key):
    #     root = Tk()
    #     root.withdraw()
    #     path = askdirectory()
    #     if path:
    #         if config_key == "venv_python":
    #             full_path = os.path.join(path, "python.exe")
    #         else:
    #             full_path = path.replace("/", "\\")
    #
    #         # Update config + UI field
    #         self.config["DEFAULT"][config_key] = full_path
    #         with open(CONFIG_PATH, "w") as configfile:
    #             self.config.write(configfile)
    #
    #         if config_key == "project_directory":
    #             self.project_dir_tf.value = full_path
    #             self.project_dir = full_path
    #             self.git.project_dir = full_path  # Update Git manager
    #         elif config_key == "venv_python":
    #             self.venv_python_tf.value = full_path
    #             self.venv_python = full_path
    #
    #         self.project_dir_tf.update()
    #         self.venv_python_tf.update()

    def auto_find_python(self, e):
        root_dir = self.project_dir_tf.value
        for root, dirs, files in os.walk(root_dir):
            if "python.exe" in files:
                python_path = os.path.join(root, "python.exe")
                self.config["DEFAULT"]["venv_python"] = python_path
                with open(CONFIG_PATH, "w") as f:
                    self.config.write(f)
                self.venv_python_tf.value = python_path
                self.venv_python_tf.update()
                break


def main(page: ft.Page):
    page.title = "Vedder Admin Launcher"
    page.window_width = 700
    page.window_height = 500

    def close_app(e=None):
        print("Closing app...")
        page.window.destroy()

    launcher = Launcher()
    page.overlay.append(launcher.file_picker)
    page.add(launcher)
    launcher.load_commits()

ft.app(target=main)
