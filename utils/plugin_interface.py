from abc import ABC, abstractmethod

from PyQt5.QtWidgets import QWidget


class PluginInterface(ABC):
    """Base interface that all runtime-loaded plugins should implement."""

    @abstractmethod
    def get_widget(self, app_id: str, user_id: str, app_path: str, plugin_full_name: str) -> QWidget:
        """Return the QWidget instance to mount into the main application."""

    @abstractmethod
    def get_name(self) -> str:
        """Return the plugin display name using the normalized zero-argument signature."""
