import datetime
import os
from abc import ABC, abstractmethod
from typing import List

import pandas as pd

WORK_DIR = os.environ.get("WORK_DIR")


class File(ABC):

    @abstractmethod
    def read_file(self, file_path: str) -> pd.DataFrame:
        pass

    @abstractmethod
    def filter_data(self, filters: dict, condition: str) -> pd.DataFrame:
        pass

    @abstractmethod
    def get_columns(self) -> list:
        pass

    @abstractmethod
    def get_options(self, column: str) -> list:
        pass


class CSVFile(File):
    def __init__(
        self, file_name: str, file_path: str, file_size: int, last_modified: int
    ):
        self.file_name = file_name
        self.file_path = file_path
        self.file_size = file_size
        self.last_modified = last_modified

    def read_file(self, file_path: str) -> pd.DataFrame:
        return pd.read_csv(file_path).values.tolist()

    def filter_data(self, filters: dict, condition: str) -> pd.DataFrame:
        df = pd.read_csv(self.file_path)
        filter_expr = None
        has_filters = False
        for column, values in filters.items():
            if values:
                has_filters = True
                condition_expr = df[column].isin(values)
                if filter_expr is None:
                    filter_expr = condition_expr
                else:
                    if condition == "OR":
                        filter_expr = filter_expr | condition_expr
                    else:
                        filter_expr = filter_expr & condition_expr
        return df if not has_filters else df[filter_expr]

    def get_columns(self) -> list:
        df = pd.read_csv(self.file_path)
        columns_list = df.columns.tolist()
        return columns_list

    def get_options(self, column: str) -> list:
        df = pd.read_csv(self.file_path)
        return list(set(df[column].values.tolist()))


class FileFactory:
    @staticmethod
    def create_reader(
        file_type: str,
        file_name: str,
        file_path: str,
        file_size: int,
        last_modified: int,
    ):
        if file_type.lower() == ".csv":
            return CSVFile(
                file_name=file_name,
                file_path=file_path,
                file_size=file_size,
                last_modified=last_modified,
            )
        else:

            raise ValueError(
                f"Unsupported file type {file_name}, {file_type}, {file_path}"
            )


class FileManager:
    files: List[File]
    root_dir: str

    def __init__(self, root_dir: str):
        self.files = []
        for root, dirs, files in os.walk(root_dir):
            for file in files:
                file_path = os.path.join(root, file)
                file_stat = os.stat(file_path)
                # Extract file name and extension
                file_name, file_extension = os.path.splitext(file)
                self.files.append(
                    FileFactory().create_reader(
                        file_type=file_extension,
                        file_name=file_name,
                        file_path=file_path,
                        file_size=os.path.getsize(file_path),
                        last_modified=file_stat.st_mtime,
                    )
                )

    def get_nb_size_files_by_directories(self) -> dict:
        results = {}
        for file in self.files:
            directory = os.path.dirname(file.file_path)
            if results.get(directory):
                results[directory]["size"] += os.path.getsize(file.file_path)
                results[directory]["count"] += 1
            else:
                results[directory] = {"size": file.file_size, "count": 1}
        output = {
            "directory": [],
            "size": [],
            "count": [],
        }
        for result in results:
            output["directory"].append(result.replace(WORK_DIR, "", 1))
            output["size"].append(results[result]["size"] / (1024 * 1024))
            output["count"].append(results[result]["count"])
        return output

    def get_data_by_date(self) -> tuple:
        results = {}
        directories = []
        for file in self.files:
            directory = os.path.dirname(file.file_path)
            directory = directory.replace(WORK_DIR, "", 1)
            directories.append(directory)
        directories = list(set(directories))
        for file in self.files:
            dt_object = datetime.datetime.fromtimestamp(file.last_modified)
            date_string = dt_object.strftime("%Y-%m-%d")
            directory = os.path.dirname(file.file_path)
            directory = directory.replace(WORK_DIR, "", 1)
            if not results.get(date_string):
                results[date_string] = {}
                for d in directories:
                    results[date_string].update({d: {"size": 0, "count": 0}})
            results[date_string][directory]["size"] += round(
                file.file_size / (1024 * 1024), 2
            )
            results[date_string][directory]["count"] += 1
        output = {
            "dates": [],
            "directories": {},
        }
        for directory in directories:
            directory = directory.replace(WORK_DIR, "", 1)
            output["directories"].update({directory: {"size": [], "count": []}})
        for result in results:
            output["dates"].append(result)
            for directory in directories:
                directory = directory.replace(WORK_DIR, "", 1)
                output["directories"][directory]["size"].append(
                    results[result][directory]["size"]
                )
                output["directories"][directory]["count"].append(
                    results[result][directory]["count"]
                )
        return output, directories

    def get_sunburst_data(self) -> list:
        results = {}
        for file in self.files:
            directory = os.path.dirname(file.file_path)
            directory = directory.replace(WORK_DIR, "", 1)
            if results.get(directory):
                results[directory] += 1
            else:
                results.update({directory: 1})
        return [
            {
                "name": result,
                "value": results[result],
            }
            for result in results
        ]

    def generate_hierarchy(self) -> dict:
        hierarchy = {}

        for file in self.files:
            path = os.path.dirname(file.file_path)
            path = path.replace(WORK_DIR, "", 1)
            components = path.strip("/").split("/")  # Split path into components
            current_level = hierarchy

            for component in components:
                if component not in current_level:
                    current_level[component] = {"name": component}
                current_level = current_level[component]

            # Add a "value" key to the leaf node
            current_level["value"] = current_level.get("value", 0) + 1

        return hierarchy

    def convert_hierarchy_to_list(self, hierarchy: dict) -> list:
        result = []
        for key, value in hierarchy.items():
            node = {"name": key}
            if isinstance(value, dict):
                node["children"] = self.convert_hierarchy_to_list(value)
            else:
                node["value"] = value
            result.append(node)

        return result

    def build_tree_node(self, path: str) -> dict:
        if os.path.isdir(path):
            return {
                "value": path,
                "title": os.path.basename(path),
                "children": [
                    self.build_tree_node(os.path.join(path, child))
                    for child in os.listdir(path)
                ],
            }
        else:
            return {
                "value": path,
                "title": os.path.basename(path),
            }

    def get_tree_node_files_structure(self) -> list:
        tree_data = []
        for file in self.files:
            file_path = os.path.dirname(file.file_path)
            path_parts = file_path.split(os.sep)
            current_node = tree_data
            for part in path_parts:
                existing_node = next(
                    (node for node in current_node if node["title"] == part), None
                )
                if existing_node:
                    current_node = existing_node["children"]
                else:
                    new_node = {"value": part, "title": part, "children": []}
                    current_node.append(new_node)
                    current_node = new_node["children"]

            current_node.append(self.build_tree_node(file_path))
        return tree_data

    def get_file_from_path(self, path: str) -> File:
        for file in self.files:
            if file.file_path == path:
                return file
