"""
csv_helper: includes functions to read csv data file into dict type value
"""

from typing import List, Dict, Union
import csv

def csv_to_dict(directory, col_name:str = "")->List[Union[Dict, str]]:
    """
    Retruns the csv as a list of dict using csv columns as keys
    Parameters:
        directory (str): Path to the CSV file.
        col_name (str, optional): If provided, returns a list of values from this column only. If empty, returns a list of row dictionaries.
    Returns:
        List[Union[Dict, str]]: List of dictionaries (if col_name is empty) or list of strings (if col_name is specified).
    """
    data_list = []

    with open(directory, mode='r', encoding='utf-8', newline='') as file:
        csv_reader = csv.DictReader(file)

        for row in csv_reader:
            if col_name:
                item = str(row.get(col_name, ""))
                if item not in data_list:
                    data_list.append(item)
            else:
                data_list.append(row)

    return data_list

def get_columns_by_key(directory:str, search_key:str="", column:str="")->Union[Dict, str]:
    """
    Returns the csv as a dict using the first column as key and the rest as values

    Parameters:
        directory (str): Path to the CSV file.
        search_key (str, optional): If provided, returns values only for this key (first column value).
        column (str, optional): If provided with search_key, returns only the value for this column.

    Returns:
        Union[Dict, str]: Dictionary mapping keys to values, or a single value if both search_key and column are specified.
    """
    output = {}

    with open(directory, mode='r', encoding='utf-8', newline='') as file:
        csv_reader = csv.reader(file)
        if search_key:
            header = next(csv_reader)
            for row in csv_reader:    
                if search_key == row[0]:
                    output = dict(zip(header[1:], row[1:]))
                    if column:
                        return output.get(column, "")
                    else:
                        return output
        else:
            for row in csv_reader:    
                key = row[0]
                values = row[1:]
                output[key] = values
    return output
