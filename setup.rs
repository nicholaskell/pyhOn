```rust
// This is a Rust equivalent of the Python setup script using Cargo.
// It defines a library crate for controlling hOn devices.

use std::fs;
use std::path::Path;

// Function to read the README file and return its content as a String
fn read_readme() -> String {
    let readme_path = Path::new("README.md");
    fs::read_to_string(readme_path).expect("Failed to read README.md")
}

fn main() {
    // Define the long description by reading the README file
    let long_description = read_readme();

    // Define the package metadata
    let package_metadata = toml::toml! {
        [package]
        name = "pyhOn"
        version = "0.15.15"
        authors = ["Andre Basche"]
        description = "Control hOn devices with Rust"
        readme = "README.md"
        license = "MIT"
        edition = "2021"

        [dependencies]
        aiohttp = "3.8"
        typing-extensions = "4.8"
        yarl = "1.8"

        [package.metadata]
        project_urls = { 
            GitHub = "https://github.com/Andre0512/pyhOn",
            PyPI = "https://pypi.org/project/pyhOn"
        }

        [package.classifiers]
        "Development Status :: 4 - Beta"
        "Environment :: Console"
        "License :: OSI Approved :: MIT License"
        "Natural Language :: English"
        "Operating System :: OS Independent"
        "Programming Language :: Rust"
        "Topic :: Software Development :: Libraries :: Rust Crates"
    };

    // Write the package metadata to Cargo.toml
    let cargo_toml_path = Path::new("Cargo.toml");
    fs::write(cargo_toml_path, package_metadata.to_string()).expect("Failed to write Cargo.toml");

    // Entry point for the console script
    // This would typically be defined in the main.rs file of the crate
    // Here we just print a message for demonstration purposes
    println!("pyhOn is ready to be used!");
}
```

### Explanation:
- The Rust code uses the `std::fs` module to read the README file and write the package metadata to a `Cargo.toml` file.
- The `toml` crate is used to format the package metadata in TOML format, which is the format used by Cargo for Rust projects.
- The `main` function serves as the entry point, similar to how the `setup.py` script is executed in Python.
- The dependencies and metadata are defined in a similar structure to the Python `setup` function.
- Note that Rust does not have a direct equivalent to Python's `setuptools`, so the approach is slightly different, focusing on creating a `Cargo.toml` file instead.