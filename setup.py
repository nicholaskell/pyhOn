```python
import os

def read_readme():
    """Read the README file and return its content as a string."""
    readme_path = "README.md"
    try:
        with open(readme_path, 'r') as file:
            return file.read()
    except IOError as e:
        raise RuntimeError("Failed to read README.md") from e

def main():
    """Main entry point for the script."""
    # Define the long description by reading the README file
    long_description = read_readme()

    # Define the package metadata
    package_metadata = f"""
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
project_urls = {{ 
    GitHub = "https://github.com/Andre0512/pyhOn",
    PyPI = "https://pypi.org/project/pyhOn"
}}

[package.classifiers]
"Development Status :: 4 - Beta"
"Environment :: Console"
"License :: OSI Approved :: MIT License"
"Natural Language :: English"
"Operating System :: OS Independent"
"Programming Language :: Rust"
"Topic :: Software Development :: Libraries :: Rust Crates"
"""

    # Write the package metadata to Cargo.toml
    cargo_toml_path = "Cargo.toml"
    try:
        with open(cargo_toml_path, 'w') as file:
            file.write(package_metadata)
    except IOError as e:
        raise RuntimeError("Failed to write Cargo.toml") from e

    # Print a message indicating that the package is ready to be used
    print("pyhOn is ready to be used!")

if __name__ == "__main__":
    main()
``` 

### Explanation:
- The `read_readme` function reads the content of `README.md` and handles any potential I/O errors.
- The `main` function constructs the package metadata in a string format that mimics the TOML structure used in Rust's `Cargo.toml`.
- The metadata is then written to a file named `Cargo.toml`, with error handling for file writing.
- Finally, a message is printed to indicate that the package is ready for use.