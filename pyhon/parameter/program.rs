Here is the equivalent Rust code for the provided Python code, maintaining the same functionality and using idiomatic Rust practices:

```rust
use std::collections::HashMap;

/// Enum representing the parameters for the HonParameterProgram.
#[derive(Debug)]
pub struct HonParameterProgram<'a> {
    _filter: [&'static str; 2],
    _command: &'a HonCommand,
    _value: String,
    _programs: HashMap<String, &'a HonCommand>,
    _typology: String,
}

impl<'a> HonParameterProgram<'a> {
    /// Creates a new instance of HonParameterProgram.
    ///
    /// # Arguments
    ///
    /// * `key` - A string representing the key.
    /// * `command` - A reference to a HonCommand instance.
    /// * `group` - A string representing the group.
    pub fn new(key: &str, command: &'a HonCommand, group: &str) -> Self {
        let mut _value = command.category.clone();
        if command.category.contains("PROGRAM") {
            _value = command.category.split('.').last().unwrap_or("").to_lowercase();
        }
        
        let _programs = command.categories.clone();
        let _typology = "enum".to_string();
        
        Self {
            _filter: ["iot_recipe", "iot_guided"],
            _command: command,
            _value,
            _programs,
            _typology,
        }
    }

    /// Gets the current value.
    pub fn value(&self) -> &str {
        &self._value
    }

    /// Sets the value if it is allowed.
    ///
    /// # Arguments
    ///
    /// * `value` - A string representing the new value.
    pub fn set_value(&mut self, value: &str) {
        if self.values().contains(&value.to_string()) {
            self._command.category = value.to_string();
        } else {
            panic!("Allowed values: {:?} But was: {}", self.values(), value);
        }
    }

    /// Gets the allowed values, filtered by _filter.
    pub fn values(&self) -> Vec<String> {
        let mut values: Vec<String> = self._programs
            .keys()
            .filter(|&v| !self._filter.iter().any(|&f| v.contains(f)))
            .cloned()
            .collect();
        values.sort();
        values
    }

    /// Gets the IDs of the programs, filtered by certain conditions.
    pub fn ids(&self) -> HashMap<i32, String> {
        let mut values: HashMap<i32, String> = HashMap::new();
        for (name, parameter) in &self._programs {
            if name.contains("iot_") {
                continue;
            }
            if parameter.parameters.get("prCode").is_some() {
                continue;
            }
            if let Some(fav) = parameter.parameters.get("favourite") {
                if fav.value == "1" {
                    continue;
                }
            }
            if let Some(pr_code) = parameter.parameters.get("prCode") {
                if let Ok(code) = pr_code.value.parse::<i32>() {
                    values.insert(code, name.clone());
                }
            }
        }
        let mut sorted_values: Vec<_> = values.into_iter().collect();
        sorted_values.sort_by_key(|&(k, _)| k);
        sorted_values.into_iter().collect()
    }
}
```

### Explanation:
- The `HonParameterProgram` struct is defined with fields corresponding to the Python class attributes.
- The constructor `new` initializes the struct, similar to the `__init__` method in Python.
- The `value` method is implemented as a getter, and `set_value` is a method to set the value with validation.
- The `values` method returns a sorted list of allowed values, filtering out those that match the `_filter`.
- The `ids` method constructs a HashMap of IDs based on certain conditions, similar to the Python implementation.
- Rust's ownership and borrowing rules are respected, and error handling is done using `panic!` for simplicity, but in a production scenario, you might want to use `Result` for better error handling.