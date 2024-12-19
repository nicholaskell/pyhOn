```python
from typing import Dict, List, Optional, Tuple, Union, Callable

class Either:
    """Represents a value that can be either a string or a float."""
    
    def __init__(self, value: Union[str, float]):
        if isinstance(value, str):
            self.value = ('left', value)
        else:
            self.value = ('right', value)

    def __str__(self) -> str:
        """Convert the Either value to a string."""
        return str(self.value[1])

class HonRule:
    """Placeholder for the HonRule class."""
    
    def __init__(self, extras: Optional[Dict[str, str]], param_data: Dict[str, str], param_key: str):
        self.extras = extras
        self.param_data = param_data
        self.param_key = param_key

class HonParameter:
    """Represents a parameter with various attributes and triggers."""
    
    def __init__(self, key: str, attributes: Dict[str, str], group: str):
        self.key = key
        self.attributes = attributes
        self.category = ""
        self.typology = ""
        self.mandatory = 0
        self.value: Optional[Either] = None
        self.group = group
        self.triggers: Dict[str, List[Tuple[Callable[[HonRule], None], HonRule]]] = {}
        self.set_attributes()

    def set_attributes(self):
        """Sets the attributes from the provided dictionary."""
        self.category = self.attributes.get("category", "")
        self.typology = self.attributes.get("typology", "")
        self.mandatory = int(self.attributes.get("mandatory", "0"))

    def key(self) -> str:
        """Returns the key of the parameter."""
        return self.key

    def value(self) -> Either:
        """Returns the value of the parameter."""
        return self.value if self.value is not None else Either("0")

    def set_value(self, value: Either):
        """Sets the value of the parameter and checks for triggers."""
        self.value = value
        self.check_trigger(value)

    def intern_value(self) -> str:
        """Returns the internal value as a string."""
        return str(self.value) if self.value else "0"

    def values(self) -> List[str]:
        """Returns a list of values as strings."""
        return [self.intern_value()]

    def category(self) -> str:
        """Returns the category of the parameter."""
        return self.category

    def typology(self) -> str:
        """Returns the typology of the parameter."""
        return self.typology

    def mandatory(self) -> int:
        """Returns the mandatory status of the parameter."""
        return self.mandatory

    def group(self) -> str:
        """Returns the group of the parameter."""
        return self.group

    def add_trigger(self, value: str, func: Callable[[HonRule], None], data: HonRule):
        """Adds a trigger for the parameter."""
        if self.value and str(self.value) == value:
            func(data)
        self.triggers.setdefault(value, []).append((func, data))

    def check_trigger(self, value: Either):
        """Checks if any triggers should be activated based on the current value."""
        value_str = str(value).lower()
        if value_str in self.triggers:
            for func, args in self.triggers[value_str]:
                func(args)

    def triggers(self) -> Dict[str, Dict[str, Dict[str, str]]]:
        """Returns the triggers associated with the parameter."""
        result = {}
        for value, rules in self.triggers.items():
            for _, rule in rules:
                param = result.setdefault(value, {})
                if rule.extras:
                    for extra_key, extra_value in rule.extras.items():
                        nested_param = param.setdefault(extra_key, {})
                        nested_param[extra_value] = {}
                fixed_value = rule.param_data.get("fixedValue")
                if fixed_value:
                    param[rule.param_key] = fixed_value
                else:
                    param[rule.param_key] = rule.param_data.get("defaultValue", "")

        return result

    def reset(self):
        """Resets the parameter to its initial state."""
        self.set_attributes()
``` 

This Python code maintains the same functionality as the provided Rust code, using idiomatic Python constructs. The `Either` class is used to represent a value that can be either a string or a float, and the `HonParameter` class encapsulates the logic and attributes of the parameter. The `HonRule` class is included as a placeholder, similar to the original Rust code.