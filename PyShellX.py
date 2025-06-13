import sys
import os
import subprocess
import shlex
from shutil import which  # To resolve executables from PATH

# Define the built-in commands
BUILTIN_COMMANDS = {"echo", "exit", "type", "pwd", "cd"}


def find_executable(command):
    """Search for the command in the directories listed in the PATH environment variable."""
    return which(command)  # Automatically searches in PATH


def run_external_command(command_parts, output_file=None, append_output=False, error_file=None, append_error=False):
    """Run an external command with optional output (overwrite/append) and error redirection."""
    try:
        stdout_mode = "a" if append_output else "w"
        stderr_mode = "a" if append_error else "w"

        stdout_target = open(output_file, stdout_mode) if output_file else subprocess.PIPE
        stderr_target = open(error_file, stderr_mode) if error_file else subprocess.PIPE

        result = subprocess.run(command_parts, text=True, stdout=stdout_target, stderr=stderr_target)

        # Print to console only if output is not redirected
        if not output_file:
            sys.stdout.write(result.stdout)

        if not error_file:
            sys.stderr.write(result.stderr)

        if output_file:
            stdout_target.close()
        if error_file:
            stderr_target.close()

    except FileNotFoundError:
        print(f"{command_parts[0]}: command not found", file=sys.stderr)
    except PermissionError:
        print(f"{command_parts[0]}: permission denied", file=sys.stderr)
    except Exception as e:
        print(f"Error running command: {e}", file=sys.stderr)


def change_directory(path):
    """Handle the cd command with absolute, relative, and home directory paths."""
    if path == "~":
        path = os.environ.get("HOME", "/")  # Get home directory, default to root if not set

    try:
        os.chdir(os.path.abspath(path))  # Convert relative path to absolute and change directory
    except FileNotFoundError:
        print(f"cd: {path}: No such file or directory", file=sys.stderr)
    except NotADirectoryError:
        print(f"cd: {path}: Not a directory", file=sys.stderr)
    except PermissionError:
        print(f"cd: {path}: Permission denied", file=sys.stderr)


def parse_input(user_input):
    """Parse input while handling quoted executables, arguments, and redirections."""
    try:
        return shlex.split(user_input, posix=True)  # Properly handles quotes, backslashes, and spaces
    except ValueError as e:
        print(f"Parsing error: {e}", file=sys.stderr)
        return []


def handle_redirection(command_parts):
    """
    Checks for output (`>`, `1>`, `>>`, `1>>`) and error (`2>`, `2>>`) redirection and returns:
    - The command without redirection parts
    - The output file (if present) and append mode flag
    - The error file (if present) and append mode flag
    """
    output_file = None
    append_output = False
    error_file = None
    append_error = False
    clean_command = []

    i = 0
    while i < len(command_parts):
        if command_parts[i] in [">", "1>"]:
            if i + 1 < len(command_parts):
                output_file = command_parts[i + 1]
                append_output = False  # Overwrite mode
                i += 1  # Skip next argument (filename)
            else:
                print("Syntax error: Missing file for output redirection", file=sys.stderr)
        elif command_parts[i] in [">>", "1>>"]:
            if i + 1 < len(command_parts):
                output_file = command_parts[i + 1]
                append_output = True  # Append mode
                i += 1  # Skip next argument (filename)
            else:
                print("Syntax error: Missing file for output redirection", file=sys.stderr)
        elif command_parts[i] == "2>":
            if i + 1 < len(command_parts):
                error_file = command_parts[i + 1]
                append_error = False  # Overwrite mode
                i += 1  # Skip next argument (filename)
            else:
                print("Syntax error: Missing file for error redirection", file=sys.stderr)
        elif command_parts[i] == "2>>":
            if i + 1 < len(command_parts):
                error_file = command_parts[i + 1]
                append_error = True  # Append mode
                i += 1  # Skip next argument (filename)
            else:
                print("Syntax error: Missing file for error redirection", file=sys.stderr)
        else:
            clean_command.append(command_parts[i])
        i += 1

    return clean_command, output_file, append_output, error_file, append_error


def execute_quoted_executable(command_parts, output_file=None, append_output=False, error_file=None,
                              append_error=False):
    """Handles cases where the executable name is quoted and contains spaces."""
    executable_path = command_parts[0]

    # Try direct execution if it's a valid path
    if os.path.isfile(executable_path) and os.access(executable_path, os.X_OK):
        run_external_command(command_parts, output_file, append_output, error_file, append_error)
        return

    # Check if command exists in PATH
    resolved_executable = find_executable(command_parts[0])
    if resolved_executable:
        command_parts[0] = resolved_executable  # Replace with full path
        run_external_command(command_parts, output_file, append_output, error_file, append_error)
    else:
        print(f"{executable_path}: command not found", file=sys.stderr)


def main():
    while True:
        sys.stdout.write("$ ")
        sys.stdout.flush()  # Ensure prompt is displayed immediately

        try:
            user_input = input().strip()
            if not user_input:
                continue  # Skip empty input

            command_parts = parse_input(user_input)  # Handle quoted executables and arguments properly
            if not command_parts:
                continue

            command_parts, output_file, append_output, error_file, append_error = handle_redirection(
                command_parts)  # Check for output and error redirection

            if not command_parts:
                continue

            if command_parts[0] == "exit" and len(command_parts) == 2 and command_parts[1] == "0":
                sys.exit(0)  # Exit with status code 0

            if command_parts[0] == "echo":
                # Handle echo command with optional redirection
                output = " ".join(command_parts[1:])
                if output_file:
                    mode = "a" if append_output else "w"
                    with open(output_file, mode) as f:
                        f.write(output + "\n")
                else:
                    print(output)

            elif command_parts[0] == "type":
                # Handle type command: check for built-ins and executables in PATH
                cmd_to_check = command_parts[1]
                if cmd_to_check in BUILTIN_COMMANDS:
                    print(f"{cmd_to_check} is a shell builtin")
                else:
                    executable_path = find_executable(cmd_to_check)
                    if executable_path:
                        print(f"{cmd_to_check} is {executable_path}")
                    else:
                        print(f"{cmd_to_check}: not found", file=sys.stderr)

            elif command_parts[0] == "pwd":
                # Handle pwd command
                output = os.getcwd()
                if output_file:
                    mode = "a" if append_output else "w"
                    with open(output_file, mode) as f:
                        f.write(output + "\n")
                else:
                    print(output)

            elif command_parts[0] == "cd":
                # Handle cd command
                if len(command_parts) > 1:
                    change_directory(command_parts[1])
                else:
                    home_path = os.environ.get("HOME", "/")  # Default to root if HOME is not set
                    os.chdir(home_path)

            else:
                # Handle executing quoted executable names
                execute_quoted_executable(command_parts, output_file, append_output, error_file, append_error)

        except EOFError:
            sys.exit(0)  # Handle EOF (Ctrl+D) gracefully with exit code 0
        except KeyboardInterrupt:
            sys.stdout.write("\n")  # Handle Ctrl+C and print a new line


if __name__ == "__main__":
    main()
