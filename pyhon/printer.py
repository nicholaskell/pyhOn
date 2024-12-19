```python
from typing import Any, Dict, List, Union

def key_print(data: Any, key: str = '', start: bool = True) -> str:
    """
    Recursively prints the keys and values of a nested data structure.

    Args:
        data: The data to print, which can be a list, dictionary, or any other type.
        key: The current key in the nested structure, default is an empty string.
        start: A boolean indicating if this is the start of the print, default is True.

    Returns:
        A formatted string representation of the data.
    """
    result = ""

    if isinstance(data, list):
        for i, value in enumerate(data):
            result += key_print(value, f"{key}.{i}" if key else str(i), False)
    elif isinstance(data, dict):
        for k in sorted(data.keys()):
            value = data[k]
            result += key_print(value, k if start else f"{key}.{k}", False)
    else:
        result += f"{key}: {data}\n"

    return result


def pretty_print(data: Any, key: str = '', intend: int = 0, is_list: bool = False, whitespace: str = '  ') -> str:
    """
    Pretty prints a nested data structure with indentation.

    Args:
        data: The data to print, which can be a list, dictionary, or any other type.
        key: The current key in the nested structure, default is an empty string.
        intend: The current indentation level, default is 0.
        is_list: A boolean indicating if the current data is a list, default is False.
        whitespace: The string used for indentation, default is two spaces.

    Returns:
        A formatted string representation of the data.
    """
    result = ""
    space = whitespace * intend

    if isinstance(data, (dict, list)) and key:
        result += f"{space}{'- ' if is_list else ''}{key}:\n"

    if isinstance(data, list):
        for value in data:
            result += pretty_print(value, '', intend + 1, True, whitespace)
    elif isinstance(data, dict):
        for i, list_key in enumerate(sorted(data.keys())):
            value = data[list_key]
            result += pretty_print(value, list_key, intend + (1 if is_list else 0), is_list and i == 0, whitespace)
    else:
        result += f"{space}{'- ' if is_list else ''}{key}{data}\n"

    return result


def create_commands(commands: Dict[str, 'HonCommand'], concat: bool = False) -> Dict[str, Any]:
    """
    Creates a dictionary of commands and their parameters.

    Args:
        commands: A dictionary of command names to their respective command objects.
        concat: A boolean indicating if the keys should be concatenated, default is False.

    Returns:
        A dictionary mapping command names and parameters to their values.
    """
    result = {}

    for name, command in commands.items():
        for parameter, data in command.available_settings.items():
            if isinstance(data, HonParameterEnum):
                value = data.values
            elif isinstance(data, HonParameterRange):
                value = {
                    "min": data.min,
                    "max": data.max,
                    "step": data.step
                }
            else:
                continue

            if not concat:
                result.setdefault(name, {})[parameter] = value
            else:
                result[f"{name}.{parameter}"] = value

    return result


def create_rules(commands: Dict[str, 'HonCommand'], concat: bool = False) -> Dict[str, Any]:
    """
    Creates a dictionary of rules based on command triggers.

    Args:
        commands: A dictionary of command names to their respective command objects.
        concat: A boolean indicating if the keys should be concatenated, default is False.

    Returns:
        A dictionary mapping command names and parameters to their triggers.
    """
    result = {}

    for name, command in commands.items():
        for parameter, data in command.available_settings.items():
            value = data.triggers
            if not value:
                continue
            if not concat:
                result.setdefault(name, {})[parameter] = value
            else:
                result[f"{name}.{parameter}"] = value

    return result
```