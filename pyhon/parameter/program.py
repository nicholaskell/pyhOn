Here is the equivalent Python code for the provided Rust code, maintaining the same functionality and using idiomatic Python practices:

```python
from typing import Dict, List, Optional

class HonCommand:
    def __init__(self, category: str, categories: Dict[str, 'HonCommand'], parameters: Dict[str, str]):
        self.category = category
        self.categories = categories
        self.parameters = parameters

class HonParameterProgram:
    """Class representing the parameters for the HonParameterProgram."""

    def __init__(self, key: str, command: HonCommand, group: str):
        """
        Creates a new instance of HonParameterProgram.

        Args:
            key: A string representing the key.
            command: An instance of HonCommand.
            group: A string representing the group.
        """
        self._filter = ["iot_recipe", "iot_guided"]
        self._command = command
        self._value = command.category
        
        # Adjust value if category contains "PROGRAM"
        if "PROGRAM" in command.category:
            self._value = command.category.split('.')[-1].lower()
        
        self._programs = command.categories
        self._typology = "enum"

    def value(self) -> str:
        """Gets the current value."""
        return self._value

    def set_value(self, value: str) -> None:
        """
        Sets the value if it is allowed.

        Args:
            value: A string representing the new value.
        """
        if value in self.values():
            self._command.category = value
        else:
            raise ValueError(f"Allowed values: {self.values()} But was: {value}")

    def values(self) -> List[str]:
        """Gets the allowed values, filtered by _filter."""
        values = [name for name in self._programs.keys() 
                  if not any(f in name for f in self._filter)]
        values.sort()
        return values

    def ids(self) -> Dict[int, str]:
        """Gets the IDs of the programs, filtered by certain conditions."""
        values = {}
        for name, parameter in self._programs.items():
            if "iot_" in name:
                continue
            if "prCode" in parameter.parameters:
                continue
            if "favourite" in parameter.parameters and parameter.parameters["favourite"] == "1":
                continue
            if "prCode" in parameter.parameters:
                try:
                    code = int(parameter.parameters["prCode"])
                    values[code] = name
                except ValueError:
                    continue
        
        # Sort by key and return as a dictionary
        return dict(sorted(values.items()))
```

### Explanation:
- The `HonCommand` class is defined to represent the command structure used in `HonParameterProgram`.
- The `HonParameterProgram` class is implemented with methods that correspond to the Rust struct methods.
- The constructor `__init__` initializes the class attributes, similar to the Rust `new` method.
- The `value` method acts as a getter, while `set_value` sets the value with validation, raising a `ValueError` if the value is not allowed.
- The `values` method returns a sorted list of allowed values, filtering out those that match the `_filter`.
- The `ids` method constructs a dictionary of IDs based on certain conditions, similar to the Rust implementation. It handles potential `ValueError` when converting `prCode` to an integer.