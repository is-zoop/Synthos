from enum import Enum

from qfluentwidgets import StyleSheetBase, Theme, qconfig


class StyleSheet(StyleSheetBase, Enum):
    """ Style sheet  """

    LINK_CARD = "link_card"
    SAMPLE_CARD = "sample_card"
    HOME_INTERFACE = "home_interface"
    ICON_INTERFACE = "icon_interface"
    VIEW_INTERFACE = "view_interface"
    SETTING_INTERFACE = "setting_interface"
    GALLERY_INTERFACE = "gallery_interface"
    NAVIGATION_VIEW_INTERFACE = "navigation_view_interface"
    LOGIN_WINDOWS = "login"
    USER_SETTING = "userSetting"

    def path(self, theme=Theme.AUTO):
        # theme = qconfig.theme if theme == Theme.AUTO else theme
        path = r'E:\AutoTool\static\qss\{value}.qss'.format(value=self.value)
        return path

