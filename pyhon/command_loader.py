```python
import json
from collections import defaultdict
from typing import Dict, List, Optional, Any

class HonCommandLoader:
    """Represents a command loader for hOn command data."""

    def __init__(self, api, appliance):
        """
        Creates a new `HonCommandLoader`.

        Args:
            api: The API connection object.
            appliance: The appliance object.
        """
        self.api = api
        self.appliance = appliance
        self.api_commands: Dict[str, Any] = {}
        self.favourites: List[Dict[str, Any]] = []
        self.command_history: List[Dict[str, Any]] = []
        self.commands: Dict[str, 'HonCommand'] = {}
        self.appliance_data: Dict[str, Any] = {}
        self.additional_data: Dict[str, Any] = {}

    def load_commands(self):
        """Trigger loading of command data."""
        self._load_data()
        self.appliance_data = self.api_commands.get("applianceModel", {})
        self._get_commands()
        self._add_favourites()
        self._recover_last_command_states()

    async def _load_commands(self):
        """Load commands from the API."""
        self.api_commands = await self.api.load_commands(self.appliance)

    async def _load_favourites(self):
        """Load favourites from the API."""
        self.favourites = await self.api.load_favourites(self.appliance)

    async def _load_command_history(self):
        """Load command history from the API."""
        self.command_history = await self.api.load_command_history(self.appliance)

    async def _load_data(self):
        """Load all relevant data in parallel."""
        await asyncio.gather(
            self._load_commands(),
            self._load_favourites(),
            self._load_command_history()
        )

    @staticmethod
    def _is_command(data: Dict[str, Any]) -> bool:
        """Check if the given data can be parsed as a command."""
        return "description" in data and "protocolType" in data

    @staticmethod
    def _clean_name(category: str) -> str:
        """Clean up the category name."""
        if "PROGRAM" in category:
            return category.split('.')[-1].lower()
        return category

    def _get_commands(self):
        """Generates HonCommand from API data."""
        for name, data in self.api_commands.items():
            command = self._parse_command(data, name)
            if command:
                self.commands[command.name] = command

    def _parse_command(self, data: Any, command_name: str) -> Optional['HonCommand']:
        """Try to create a HonCommand object."""
        if not isinstance(data, dict):
            self.additional_data[command_name] = data
            return None

        if self._is_command(data):
            return HonCommand(command_name, data, self.appliance)

        return None

    def _get_last_command_index(self, name: str) -> Optional[int]:
        """Get index of last command execution."""
        for index, d in enumerate(self.command_history):
            if d.get("command", {}).get("commandName") == name:
                return index
        return None

    def _set_last_category(self, command: 'HonCommand', name: str, parameters: Dict[str, Any]) -> 'HonCommand':
        """Set category to last state."""
        if "program" in parameters:
            command.category = self._clean_name(parameters["program"])
        elif "category" in parameters:
            command.category = parameters["category"]
        return command

    def _recover_last_command_states(self):
        """Set commands to last state."""
        for name, command in self.commands.items():
            last_index = self._get_last_command_index(name)
            if last_index is not None:
                last_command = self.command_history[last_index]
                parameters = last_command.get("command", {}).get("parameters", {})
                command = self._set_last_category(command, name, parameters)
                for key, data in command.settings.items():
                    if key in parameters:
                        data.value = int(parameters[key])  # Assuming parameters are convertible to int

    def _add_favourites(self):
        """Patch program categories with favourites."""
        for favourite in self.favourites:
            name, command_name, base = self._get_favourite_info(favourite)
            if base is None:
                continue
            base_command = base
            self._update_base_command_with_data(base_command, favourite)
            self._update_base_command_with_favourite(base_command)
            self._update_program_categories(command_name, name, base_command)

    def _get_favourite_info(self, favourite: Dict[str, Any]) -> (str, str, Optional['HonCommand']):
        """Get favourite information."""
        name = favourite.get("favouriteName", "")
        command = favourite.get("command", {})
        command_name = command.get("commandName", "")
        program_name = self._clean_name(command.get("programName", ""))
        base_command = self.commands.get(command_name)
        return name, command_name, base_command

    def _update_base_command_with_data(self, base_command: 'HonCommand', command: Dict[str, Any]):
        """Update base command with data from the command."""
        for key, value in command.items():
            if isinstance(value, dict):
                if key in base_command.parameters:
                    base_command.parameters[key].value = int(value)  # Assuming value is convertible to int

    def _update_base_command_with_favourite(self, base_command: 'HonCommand'):
        """Update base command with favourite information."""
        base_command.parameters["favourite"] = HonParameterFixed("favourite", {"fixedValue": "1"}, "custom")

    def _update_program_categories(self, command_name: str, name: str, base_command: 'HonCommand'):
        """Update program categories with the base command."""
        if "program" in base_command.parameters:
            base_command.parameters["program"].set_value(name)
        self.commands[command_name].categories[name] = base_command
```

In this Python code, I've translated the Rust struct `HonCommandLoader` into an idiomatic Python class with methods. The code maintains the same functionality as the original Rust code while adhering to Python's conventions, such as using dictionaries for key-value pairs and lists for collections. The use of `async` and `await` allows for asynchronous operations similar to Rust's async features.