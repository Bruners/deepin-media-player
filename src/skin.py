from dtk.ui.theme import Theme, ui_theme
from dtk.ui.skin_config import skin_config
import os
from dtk.ui.utils import get_parent_dir

# Init skin config.
skin_config.init_skin(
    "03",
    os.path.join(get_parent_dir(__file__, 2), "skin"),
    os.path.expanduser("~/.config/deepin-media-player/skin"),
    os.path.expanduser("~/.config/deepin-media-player/skin_config.ini"),
    )

# Create application theme.
app_theme = Theme(
    os.path.join(get_parent_dir(__file__, 2), "app_theme"),
    os.path.expanduser("~/.config/deepin-media-player/theme")
    )

# Set theme.
skin_config.load_themes(ui_theme, app_theme)
