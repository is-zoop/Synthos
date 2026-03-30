import gc
import importlib.util
import os
import sys

from .plugin_interface import PluginInterface


class PluginManager:
    def __init__(self):
        self.plugins = []

    def _get_unique_module_name(self, plugin_path: str) -> str:
        dir_name = os.path.basename(os.path.dirname(plugin_path))
        file_name = os.path.splitext(os.path.basename(plugin_path))[0]
        return f"{dir_name}.{file_name}"

    def load_plugin(self, plugin_path: str) -> PluginInterface:
        unique_module_name = self._get_unique_module_name(plugin_path)
        plugin_dir = os.path.dirname(plugin_path)
        if plugin_dir not in sys.path:
            sys.path.insert(0, plugin_dir)

        try:
            spec = importlib.util.spec_from_file_location(unique_module_name, plugin_path)
            if spec is None or spec.loader is None:
                raise ImportError(f"Unable to load module: {plugin_path}")

            module = importlib.util.module_from_spec(spec)
            sys.modules[unique_module_name] = module
            spec.loader.exec_module(module)

            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if isinstance(attr, type) and issubclass(attr, PluginInterface) and attr != PluginInterface:
                    return attr()

            raise ImportError(f"PluginInterface implementation not found: {plugin_path}")
        except Exception:
            if unique_module_name in sys.modules:
                del sys.modules[unique_module_name]
            raise

    def unload_plugin(self, plugin_path: str):
        unique_module_name = self._get_unique_module_name(plugin_path)
        if unique_module_name in sys.modules:
            del sys.modules[unique_module_name]
            gc.collect()
        else:
            print(f"[WARN] Tried to unload missing plugin module: {unique_module_name}")


def get_plugin_display_name(plugin: PluginInterface, fallback_name: str = "") -> str:
    """Support both the new `get_name()` signature and legacy one-arg plugins."""
    try:
        return plugin.get_name()
    except TypeError:
        if fallback_name:
            return plugin.get_name(fallback_name)
        raise
