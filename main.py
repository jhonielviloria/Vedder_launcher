import flet as ft
import subprocess


class Launcher(ft.Tabs):
    def __init__(self):
        super().__init__()
        # Properties
        self.selected_index = 1
        self.animation_duration = 300
        self.expand = 1

        self.btn_launch = ft.ElevatedButton(
            content=ft.Container(
                content=ft.Text('Launch \nVedder Admin', text_align='center', color='black', weight=ft.FontWeight.BOLD),
                height=100,
                width=120,
                alignment=ft.alignment.center,
            ),
            on_click=self.launch_clicked,
            bgcolor='lightgreen',
        )
        self.btn_update = ft.ElevatedButton(
            content=ft.Container(
                content=ft.Text('Update', text_align='center', color='black', weight=ft.FontWeight.BOLD),
                height=50,
                width=60,
                alignment=ft.alignment.center,
            ),
            on_click=self.update_clicked,
            bgcolor='lightblue',
        )
        tab_1 = ft.Tab(
            text='Launcher',
            content=ft.Container(
                bgcolor=ft.Colors.BLUE_GREY_200,
                height=200,
                content=ft.Row(
                    [
                        self.btn_launch,
                        self.btn_update,
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=20
                )
            )
        )

        self.project_dir_tf = ft.TextField(
            label='Project Directory',
            value=r'D:\FX\Python\Vedder_async',
            # on_change=self.on_change_project_dir,
        )
        self.venv_python_tf = ft.TextField(
            # prefix_text=self.project_dir_tf.value,
            label='Virtual Environment Python',
            value=r'.venv3_12_2\Scripts\python.exe',
        )

        tab_2 = ft.Tab(
            text='Settings',
            content=ft.Container(
                padding=20,
                bgcolor=ft.Colors.BLUE_GREY_100,
                content=ft.Column(
                    [
                        self.project_dir_tf,
                        self.venv_python_tf,
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                )
            )
        )
        self.tabs = [tab_1, tab_2]

    def launch_clicked(self, e):
        print("launch_clicked clicked!")
        dir_path = self.project_dir_tf.value
        venv_python = self.venv_python_tf.value
        script_path = r'main.py'
        #
        command = f'cd "{dir_path}" && "{venv_python}" "{script_path}"'
        subprocess.run(command, shell=True)

    def update_clicked(self, e):
        print("update_clicked clicked!")

    def on_change_project_dir(self, e):
        self.venv_python_tf.prefix_text = self.project_dir_tf.value
        self.venv_python_tf.update()

def main(page: ft.Page):
    page.title = "Flet App with Two Buttons"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.window.height = 300
    page.window.width = 400
    page.theme_mode = 'light'
    page.theme = ft.Theme(
        use_material3=True,
        font_family='Roboto',

    )

    page.add(Launcher())


ft.app(target=main, view=ft.AppView.FLET_APP)