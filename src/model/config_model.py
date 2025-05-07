import os
import logging
import yaml
from dataclasses import dataclass
from enum import Enum, auto

from pylightlib.msc.Singleton import Singleton  # type: ignore


class FieldType(Enum):
    """
    Enum providing the field types for the topics table.
    """
    STRING = auto()
    NUMBER = auto()
    SELECT = auto()
    DATE = auto()


@dataclass(slots=True, frozen=True)
class FieldDefinition:
    """
    Dataclass for a field definition for the topics table.

    Attributes:
        name: The internal name of the field.
        caption: The caption of the field displayed as table column header.
        type: The type of the field.
        lines: The number of lines for the field. If lines == 1, an Input will
            be created, otherwise a TextArea.
        options: The selectable items if the field type is `FieldType.LIST`.
        show_in_table: Whether to show the field in the table.
        column_width: The width of the column in the table.
        input_width: The width of the input field.
        read_only: Indicates whether the field is read only.
        computed: Name of the computed value the field gets if the topic is
            created or updated.
    """
    name: str
    caption: str
    type: FieldType
    lines: int
    options: list[str | int | float | bool] | None = None
    show_in_table: bool = True
    column_width: int | None = None
    input_width: int | None = None
    read_only: bool = False
    computed: str | None = None


class Config(metaclass=Singleton):
    """
    Singleton class for the main configuration of the app.
    The configuration is loaded from a YAML file.

    Attributes:
        fields: The fields for the topics (raw data from the YAML file).

            Structure: fields[<row>][<col>][<name|caption|...>]

            Row and column indices are 0-based and define the placement of the
            corresponding input in the form.
        columns: The columns of the topics table.
        columns_dict: A dictionary mapping field names to field definitions.
        task_column_names: The names of the columns in the tasks kanban.
        task_column_captions: A dictionary mapping column names to their
            captions.
    """
    fields: list[list[dict[str, str | int | float | bool]]] = []
    columns: list[FieldDefinition] = []
    columns_dict: dict[str, FieldDefinition] = {}
    task_column_names: list[str] = []
    task_column_captions: dict[str, str] = {}

    def __init__(self, yaml_path: str):
        """
        Loads the YAML configuration file and initializes the fields
        and columns.

        Args:
            yaml_path: The path to the YAML configuration file.

        Raises:
            FileNotFoundError: If the YAML file does not exist.
            ValueError: If the field type is unknown.
        """
        # TODO: Clean up this method and outsource code to helper methods

        # Check if yaml file exists
        if not os.path.exists(yaml_path):
            if not os.path.exists(f'../{yaml_path}'):
                raise FileNotFoundError(
                    f'Config file "{yaml_path}" not found.')
            else:
                yaml_path = f'../{yaml_path}'

        # Open yaml file and save data in config_data
        with open(yaml_path, 'r', encoding='utf-8') as file:
            config_data = yaml.safe_load(file)

        # Get fields for the topic form
        self.fields = config_data['fields']

        # Generate list of columns for the topics table
        # and a dictionary mapping field names to field definitions
        for row in config_data['fields']:
            for col in row:
                column = FieldDefinition(
                    name         =col['name'],
                    caption      =col['caption'],
                    type         =self.parse_field_type(col['type']),
                    lines        =col.get('lines', 1),
                    options      =col.get('options', []),
                    show_in_table=col.get('show_in_table', True),
                    column_width =col.get('column_width', None),
                    input_width  =col.get('input_width', None),
                    read_only    =col.get('read_only', False),
                    computed     =col.get('computed', None)
                )
                self.columns.append(column)
                self.columns_dict[col['name']] = column

        # Get columns for the tasks table
        task_columns = config_data['task_columns']

        for task_column in task_columns:
            column_name = task_column['name']
            column_caption = task_column['caption']
            self.task_column_names.append(column_name)
            self.task_column_captions[column_name] = column_caption

    def parse_field_type(self, type_str: str) -> FieldType:
        """
        Parses the field type from a string to a FieldType enum.

        Args:
            type_str: The field type as a string.

        Returns:
            FieldType: The field type as a FieldType enum.

        Raises:
            ValueError: If the field type is unknown.
        """
        type_str = type_str.upper()

        match type_str:
            case "STRING":
                return FieldType.STRING
            case "NUMBER":
                return FieldType.NUMBER
            case "SELECT":
                return FieldType.SELECT
            case "DATE":
                return FieldType.DATE
            case _:
                raise ValueError(f"Unknown field type: {type_str}")
