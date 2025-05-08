import enum
import logging
import json
import os
from datetime import datetime
from dataclasses import dataclass
from typing import Any

from pylightlib.msc.DateTime import DateTime    # type: ignore
from pylightlib.msc.Singleton import Singleton  # type: ignore

from model.config_model import Config  # type: ignore



class TaskPriority(enum.Enum):
    """
    Enum for task priority levels.
    """
    HIGH = 1
    MEDIUM = 2
    LOW = 3


@dataclass(slots=True)
class Task:
    """
    Model for a task.

    Attributes:
        column_name: The name of the column the task belongs to.
        description: The description of the task.
        priority: The priority of the task.
        start_date: The start date of the task in "YYYY-MM-DD" format.
        end_date: The end date of the task in "YYYY-MM-DD" format.
        days_to_start: The number of days until the start date.
        days_to_end: The number of days until the end date.
    """
    column_name: str
    description: str
    priority: TaskPriority
    start_date: str
    end_date: str
    days_to_start: int | None
    days_to_end: int | None


class Tasks(metaclass=Singleton):
    """
    Model for the tasks.

    The tasks are loaded from the JSON file specified by json_path.
    The JSON file is created if it does not exist.

    Attributes:
        json_path: The path to the JSON file containing the tasks data.
        column_names: A list of column names.
        column_captions: A dictionary mapping column names to their captions.
        tasks: A dictionary mapping column names to lists of Task objects.
    """
    json_path: str
    column_names: list[str]
    column_captions: dict[str, str]
    tasks: dict[str, list[Task]] = {}


    def __init__(self, json_path: str):
        """
        Initializes the Tasks model.

        Args:
            json_path: The path to the JSON file containing the tasks data.
        """
        self.json_path = json_path

        # Get column names (as list) and column captions (as dict)
        # (List + dict because the list items are in a specific order
        # and the dict items are not.)
        config = Config.instance
        self.column_names = config.task_column_names
        self.column_captions = config.task_column_captions

        self.load_from_file()

    def load_from_file(self) -> None:
        """
        Loads the tasks from the JSON file.
        """
        # Create the file if it does not exist
        if not os.path.exists(self.json_path):
            with open(self.json_path, 'w', encoding='utf-8') as file:
                file.write('')

        # Load the tasks from the file
        with open(self.json_path, 'r', encoding='utf-8') as file:
            tasks_raw = json.load(file)

        self.generate_tasks_dict(tasks_raw)

    def generate_tasks_dict(self, tasks_raw: dict) -> None:
        """
        Generates a dictionary of tasks from the raw data.

        Args:
            tasks_raw: The raw data loaded from the JSON file.
        """
        for column_name, tasks_list in tasks_raw.items():
            self.tasks[column_name] = []
            for task_dict in tasks_list:
                task = self.create_task_object_from_raw_data(
                    column_name, task_dict
                )
                self.tasks[column_name].append(task)

        self.sort_tasks()

    def sort_tasks(self) -> None:
        """
        Sorts the tasks in each column by priority, start date (missing goes
        to end), end date (missing goes to end) and description.
        and description.
        """
        MAX_DATE = datetime(3000, 1, 1).timestamp()

        for _, tasks_list in self.tasks.items():
            tasks_list.sort(key=lambda task: (
                task.priority.value,
                DateTime.date_to_timestamp(task.start_date, english_format=True)
                    or MAX_DATE,
                DateTime.date_to_timestamp(task.end_date, english_format=True)
                    or MAX_DATE,
                task.description.lower()
            ))

    def create_task_object_from_raw_data(self, column_name: str,
                                         task_dict: dict[str, str]) -> Task:
        """
        Creates a Task object from raw data.

        Args:
            column_name: The name of the column the task belongs to.
            task_dict: The raw data dictionary containing task information.

        Returns:
            A Task object created from the raw data.
        """
        return Task(
            column_name=column_name,
            description=task_dict['description'],
            priority=self.num_to_priority(int(task_dict['priority'])),
            start_date=task_dict['start_date'],
            end_date=task_dict['end_date'],
            days_to_start=self.days_to(task_dict['start_date']),
            days_to_end=self.days_to(task_dict['end_date'])
        )

    def add_task_to_dict_from_raw_data(self, column_name: str,
                                       task_dict: dict[str, str]) -> None:
        """
        Adds a task to the tasks dictionary from raw data.

        Args:
            column_name: The name of the column the task belongs to.
            task_dict: The raw data dictionary containing task information.
        """
        # Create task object and add it to the tasks dictionary
        task = self.create_task_object_from_raw_data(
            column_name, task_dict
        )
        self.tasks[column_name].append(task)

        # Sort the tasks for the column_name by priority
        self.tasks[column_name].sort(key=lambda task: task.priority.value)

    def delete_task(self, column_name: str, task_index: int) -> None:
        """
        Deletes a task from the tasks dictionary.

        Args:
            column_name: The name of the column the task belongs to.
            task_index: The index of the task to be deleted.
        """
        if column_name in self.tasks and 0 <= task_index < len(self.tasks[column_name]):
            del self.tasks[column_name][task_index]


    def num_to_priority(self, priority_number: int) -> TaskPriority:
        """
        Converts a number to a TaskPriority enum.

        Args:
            num: The number to convert.

        Returns:
            The corresponding TaskPriority enum.
        """
        match priority_number:
            case 1:
                return TaskPriority.HIGH
            case 2:
                return TaskPriority.MEDIUM
            case _:
                return TaskPriority.LOW

    def priority_str_to_num(self, priority_string: str) -> int:
        """
        Converts a number to a TaskPriority enum.

        Args:
            num: The number to convert.

        Returns:
            The corresponding TaskPriority enum.
        """
        match str(priority_string).upper():
            case 'HIGH':
                return 1
            case 'MEDIUM':
                return 2
            case _:
                return 3

    def days_to(self, date_str: str) -> int | None:
        """
        Calculates the number of days to a given date.

        Args:
            date_str: The date string in the format "YYYY-MM-DD".

        Returns:
            The number of days to the given date.
        """
        timestamp = DateTime.date_to_timestamp(date_str, english_format=True)

        if timestamp:
            return DateTime.date_diff(timestamp, DateTime.today_timestamp())
        else:
            return None

    def save_to_file(self) -> None:
        """
        Saves the tasks to the JSON file.
        """
        self.sort_tasks()
        cleaned_tasks_dict = self.get_cleaned_tasks_dict()

        with open(self.json_path, 'w', encoding='utf-8') as file:
            json.dump(cleaned_tasks_dict, file, indent=4)

        logging.info(f'Saved tasks to {self.json_path}.')

    def get_cleaned_tasks_dict(self) -> dict[str, list[dict[str, str | int]]]:
        """
        Returns a cleaned version of the tasks dictionary.

        The cleaned version contains only the not computed fields for each task.
        """
        cleaned_tasks_dict = {}
        for column_name, tasks_list in self.tasks.items():
            cleaned_tasks_dict[column_name] = [
                {
                    'description': task.description,
                    'priority':    task.priority.value,
                    'start_date':  task.start_date,
                    'end_date':    task.end_date
                }
                for task in tasks_list
            ]
        return cleaned_tasks_dict
