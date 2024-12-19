```rust
use std::collections::HashMap;

/// Recursively prints the keys and values of a nested data structure.
/// 
/// # Arguments
/// 
/// * `data` - The data to print, which can be a list, dictionary, or any other type.
/// * `key` - The current key in the nested structure, default is an empty string.
/// * `start` - A boolean indicating if this is the start of the print, default is true.
/// 
/// # Returns
/// 
/// A formatted string representation of the data.
fn key_print(data: &dyn std::any::Any, key: &str, start: bool) -> String {
    let mut result = String::new();
    
    if let Some(list) = data.downcast_ref::<Vec<Box<dyn std::any::Any>>>() {
        for (i, value) in list.iter().enumerate() {
            result.push_str(&key_print(value.as_ref(), &format!("{}.{}", key, i), false));
        }
    } else if let Some(map) = data.downcast_ref::<HashMap<String, Box<dyn std::any::Any>>>() {
        let mut keys: Vec<_> = map.keys().collect();
        keys.sort();
        for k in keys {
            let value = map.get(k).unwrap();
            result.push_str(&key_print(value.as_ref(), if start { k } else { &format!("{}.{}", key, k) }, false));
        }
    } else {
        result.push_str(&format!("{}: {:?}\n", key, data));
    }
    
    result
}

/// Pretty prints a nested data structure with indentation.
/// 
/// # Arguments
/// 
/// * `data` - The data to print, which can be a list, dictionary, or any other type.
/// * `key` - The current key in the nested structure, default is an empty string.
/// * `intend` - The current indentation level, default is 0.
/// * `is_list` - A boolean indicating if the current data is a list, default is false.
/// * `whitespace` - The string used for indentation, default is two spaces.
/// 
/// # Returns
/// 
/// A formatted string representation of the data.
fn pretty_print(
    data: &dyn std::any::Any,
    key: &str,
    intend: usize,
    is_list: bool,
    whitespace: &str,
) -> String {
    let mut result = String::new();
    let space = whitespace.repeat(intend);
    
    if let Some(_) = data.downcast_ref::<HashMap<String, Box<dyn std::any::Any>>>() {
        if !key.is_empty() {
            result.push_str(&format!("{}{}{}:\n", space, if is_list { "- " } else { "" }, key));
        }
    } else if let Some(_) = data.downcast_ref::<Vec<Box<dyn std::any::Any>>>() {
        if !key.is_empty() {
            result.push_str(&format!("{}{}{}:\n", space, if is_list { "- " } else { "" }, key));
        }
    }
    
    if let Some(list) = data.downcast_ref::<Vec<Box<dyn std::any::Any>>>() {
        for value in list.iter() {
            result.push_str(&pretty_print(value.as_ref(), "", intend + 1, true, whitespace));
        }
    } else if let Some(map) = data.downcast_ref::<HashMap<String, Box<dyn std::any::Any>>>() {
        let mut keys: Vec<_> = map.keys().collect();
        keys.sort();
        for (i, list_key) in keys.iter().enumerate() {
            let value = map.get(*list_key).unwrap();
            result.push_str(&pretty_print(
                value.as_ref(),
                list_key,
                intend + (if is_list { 1 } else { 0 }),
                is_list && i == 0,
                whitespace,
            ));
        }
    } else {
        result.push_str(&format!("{}{}{}{:?}\n", space, if is_list { "- " } else { "" }, key, data));
    }
    
    result
}

/// Creates a dictionary of commands and their parameters.
/// 
/// # Arguments
/// 
/// * `commands` - A dictionary of command names to their respective command objects.
/// * `concat` - A boolean indicating if the keys should be concatenated, default is false.
/// 
/// # Returns
/// 
/// A dictionary mapping command names and parameters to their values.
fn create_commands(
    commands: &HashMap<String, HonCommand>,
    concat: bool,
) -> HashMap<String, Box<dyn std::any::Any>> {
    let mut result: HashMap<String, Box<dyn std::any::Any>> = HashMap::new();
    
    for (name, command) in commands {
        for (parameter, data) in &command.available_settings {
            let value: Box<dyn std::any::Any> = if let Some(enum_data) = data.downcast_ref::<HonParameterEnum>() {
                Box::new(enum_data.values.clone())
            } else if let Some(range_data) = data.downcast_ref::<HonParameterRange>() {
                Box::new(HashMap::from([
                    ("min".to_string(), Box::new(range_data.min)),
                    ("max".to_string(), Box::new(range_data.max)),
                    ("step".to_string(), Box::new(range_data.step)),
                ]))
            } else {
                continue;
            };
            
            if !concat {
                result.entry(name.clone()).or_insert_with(HashMap::new).insert(parameter.clone(), value);
            } else {
                result.insert(format!("{}.{}", name, parameter), value);
            }
        }
    }
    
    result
}

/// Creates a dictionary of rules based on command triggers.
/// 
/// # Arguments
/// 
/// * `commands` - A dictionary of command names to their respective command objects.
/// * `concat` - A boolean indicating if the keys should be concatenated, default is false.
/// 
/// # Returns
/// 
/// A dictionary mapping command names and parameters to their triggers.
fn create_rules(
    commands: &HashMap<String, HonCommand>,
    concat: bool,
) -> HashMap<String, Box<dyn std::any::Any>> {
    let mut result: HashMap<String, Box<dyn std::any::Any>> = HashMap::new();
    
    for (name, command) in commands {
        for (parameter, data) in &command.available_settings {
            let value = data.triggers.clone();
            if value.is_empty() {
                continue;
            }
            if !concat {
                result.entry(name.clone()).or_insert_with(HashMap::new).insert(parameter.clone(), Box::new(value));
            } else {
                result.insert(format!("{}.{}", name, parameter), Box::new(value));
            }
        }
    }
    
    result
}
```