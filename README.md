# 🐚 PyShellX – Unix Shell Emulator in Python

PyShellX is a custom-built Unix/Linux shell emulator written in Python. It replicates the behavior of traditional shells by supporting built-in commands, external programs, argument parsing, and output redirection — ideal for learning system-level programming and process control in Python.

## ⚙️ Features

- Supports core shell commands: `cd`, `pwd`, `echo`, `exit`, `type`
- Executes external binaries via PATH resolution
- Handles quoted arguments and whitespace
- Implements `stdout` and `stderr` redirection (e.g., `>`, `2>`, `>>`)
- Provides informative error diagnostics for commands, permissions, and syntax
- Modular structure for easy extension

## 🧠 Tech Stack

- Python 3
- `subprocess`, `os`, `shutil`, `sys`

## 🚀 Getting Started

1. Clone the repository:
   ```bash
   git clone https://github.com/Hardik-codes7/PyShellX.git
   cd PyShellX
   ```

2. Run the shell:
   ```bash
   python3 pyshellx.py
   ```

3. Try commands like:
   ```bash
   pwd
   cd ..
   echo "Hello, Shell"
   ls > output.txt
   ```

## 📦 Dependencies

No external packages required — uses only standard Python libraries.

## 📜 License

This project is open-source and licensed under the MIT License.

## 🙌 Acknowledgements

Inspired by Unix shell design principles and Python's powerful standard library.
