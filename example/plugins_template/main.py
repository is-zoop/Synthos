from step_ui import PyToPydWidget
from utils.plugin_interface import PluginInterface


class CountdownPlugin(PluginInterface):
    def __init__(self):
        pass

    def get_name(self, plugin_full_name):
        return plugin_full_name

    def get_version(self):
        return  self.version

    def get_widget(self, app_id, user_id, app_path, plugin_full_name):
        return PyToPydWidget(app_id, user_id, app_path, plugin_full_name)
