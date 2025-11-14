import logging
import importlib
import os
import json
from dataclasses import dataclass
from pathlib import Path
from textual.app import App
from textual.theme import Theme


@dataclass(frozen=False, slots=True)
class ThemeData:
    name: str
    textual_theme: Theme
    css_files: list[str] | None = None


class ThemeLoader:
    """
    A class to load and manage themes for applications using the Textual.

    The themes are expected to be in subfolder of the `themes` directory,
    each containing a `theme.py` file defining a `TEXTUAL_THEME` variable.
    Additionally, any number of `.css` files can be included in the
    theme folder.

    This class dynamically imports the theme modules, registers them and makes
    them available for use in the application.

    Attributes:
        THEME_NAMES: A list of available theme names.
        THEME_DATA: A dictionary mapping theme names to their data
    """
    THEME_NAMES: list[str] = []
    THEME_DATA: dict[str, ThemeData] = {}


    def __init__(self) -> None:
        """
        Initialize the ThemeLoader and load themes from the themes directory.
        """
        self._load_themes()
        self.THEME_NAMES.sort()

    def _load_themes(self) -> None:
        """
        Load themes from the "themes" directory.
        """
        # Loop all items in folder "themes"
        themes_parent_folder = __import__('themes').__path__[0]

        for item in os.listdir(themes_parent_folder):
            full_path = os.path.join(themes_parent_folder, item)

            # Skip if name begins with "." or "_"; skip non-folders
            if item.startswith('.') or item.startswith('_') \
            or not os.path.isdir(full_path):
                continue

            # Dynamically import the theme module
            module_name = f'themes.{item}.theme'
            self._import_and_register_theme(item, module_name, full_path)

        logging.info(
            f'Found {len(self.THEME_NAMES)} themes in "{themes_parent_folder}"'
        )

    def _get_css_files_for_theme(self, theme_folder_path: str) -> list[str]:
        """
        Generate a list of CSS files in the given folder.

        Args:
            theme_folder_path : The path to the theme folder.

        Returns:
            A list of CSS file paths.
        """
        css_files = []
        for file_name in os.listdir(theme_folder_path):
            if file_name.endswith('.css'):
                css_files.append(os.path.join(theme_folder_path, file_name))
        return css_files

    def _import_and_register_theme(
        self, theme_name: str, module_name: str, full_path: str
    ) -> None:
        """
        Import a theme module and register its theme.

        Args:
            theme_name: The name of the theme.
            module_name: The module name to import.
            full_path: The full path to the theme folder.
        """
        try:
            # Import the theme module (theme.py)
            theme_module = importlib.import_module(module_name)
            textual_theme = getattr(theme_module, 'TEXTUAL_THEME', None)
            css_files = self._get_css_files_for_theme(full_path)

            # Abort if no TEXTUAL_THEME variable is defined
            if textual_theme is None:
                logging.warning(
                    f'Skipping theme "{theme_name}" (no TEXTUAL_THEME defined)'
                )
                return

            # Register the theme
            self._save_theme_data(theme_name, textual_theme, css_files)
            logging.info(f'Registered theme: {theme_name}')
        except ModuleNotFoundError:
            logging.warning(f'Skipping theme "{theme_name}" (no theme.py)')
        except Exception as e:
            logging.error(f'Error loading theme "{theme_name}": {e}')

    def _save_theme_data(
        self, name: str,
        theme_instance: Theme,
        css_files: list[str] | None = None
    ) -> None:
        """
        Saves the theme data into the THEME_DATA dictionary and add the
        theme name to the list of all names (THEME_NAMES).
        """
        self.THEME_NAMES.append(name)
        self.THEME_DATA[name] = ThemeData(
            name=name, textual_theme=theme_instance, css_files=css_files
        )

    def get_previously_used_theme(
        self, theme_config_file: Path, default_theme_name: str
    ) -> str:
        """
        Return the name of the previously used theme from the
        config file.

        Args:
            theme_config_file: Path to the config file.
            default_theme_name: The default theme name to return if no
                previous theme is found.

        Returns:
            str: The theme name.
        """
        if theme_config_file.exists():
            try:
                with open(theme_config_file, 'r') as f:
                    config = json.load(f)
                    return config.get('theme', theme_config_file)
            except (json.JSONDecodeError, IOError):
                return default_theme_name
        return default_theme_name

    def register_themes_in_textual_app(self, app: App) -> None:
        """
        Register all loaded themes in the given Textual application.

        Args:
            app: The instance of the Textual application.
        """
        # Loop through name list instead of dict to keep alphabetic order
        for theme_name in self.THEME_NAMES:
            theme_data = self.THEME_DATA[theme_name]
            theme_data.textual_theme.name = f'aaa_{theme_data.textual_theme.name}'
            app.register_theme(theme_data.textual_theme)

    def set_previous_theme_in_textual_app(
        self, app: App, default_theme_name: str, theme_config_file: Path
    ) -> None:
        """
        Set the previously used theme in the given Textual application.

        Args:
            app: The instance of the Textual application.
            default_theme_name: The default theme name to use if no previous
                theme is found.
            theme_config_file: Path to the config file containing the
                previous theme.
        """
        theme_name = self.get_previously_used_theme(
            theme_config_file, default_theme_name
        )
        if theme_name in app.available_themes:
            app.theme = theme_name

        logging.info(f'Set previous theme: {theme_name}')
        logging.info(f'Available themes: {app.available_themes}')

    def save_theme_to_config(
        self, theme_name: str, theme_config_file: Path
    ) -> None:
        """
        Saves the name of the active theme to the config file.

        Args:
            theme_name: The name of the theme to save.
            theme_config_file: The path to the config file where the theme name
                will be saved.
        """
        try:
            with open(theme_config_file, 'w') as f:
                json.dump({'theme': theme_name}, f)
        except IOError as e:
            logging.error(f"Could not save theme config: {e}")

    def load_theme_css(self, theme_name: str, app: App) -> None:
        """
        Loads the CSS files for the current theme.

        Args:
            theme_name: The name of the theme to load.
            app: The instance of the Textual application.
        """
        # Remove CSS from previous theme
        self._remove_all_theme_css(app)

        # Remove 'aaa_' prefix if present
        if theme_name.startswith('aaa_'):
            theme_name = theme_name[4:]

        # Load all CSS files that are in folder themes/{theme_name}/
        css_folder = Path(f'themes/{theme_name}')
        for css_file in css_folder.glob('*.css'):
            app.stylesheet.read(str(css_file))

        # Re-parse and apply to make sure changes take effect
        app.stylesheet.reparse()
        try:
            app.stylesheet.update(app.screen)
        except:
            pass

    def _remove_all_theme_css(self, app: App) -> None:
        """
        Removes all CSS files that were loaded from the /themes/ folder.

        This is necessary when switching themes to avoid conflicts
        between styles from different themes.

        Args:
            app: The instance of the Textual application.
        """
        themes_dir = Path('themes').resolve()

        for key in list(app.stylesheet.source.keys()):
            path_str, _ = key
            try:
                css_path = Path(path_str).resolve()
            except Exception:
                continue

            # Check if the CSS file is inside the themes directory
            if themes_dir in css_path.parents:
                del app.stylesheet.source[key]