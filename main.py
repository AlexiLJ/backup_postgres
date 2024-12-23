import subprocess
from env_handler import var_getter

def run_bash_script(script_path, *args):
    """
    Runs a bash script with optional arguments and returns its output.
    :param script_path: Path to the bash script
    :param args: Arguments to pass to the script
    :return: The standard output of the bash script
    """
    try:
        # Build the command
        command = ["bash", script_path] + list(args)
        # Run the bash script and capture its output
        result = subprocess.run(command, check=True, text=True, capture_output=True)
        # Return the script's output
        return result.stdout.strip()

    except subprocess.CalledProcessError as e:
        print("Error executing script:", e)
        print("Error Output:\n", e.stderr)
        return None


# Example usage
if __name__ == "__main__":
    # Replace with the actual path to your bash script
    script_path = "./backup_postgres.sh"

    # Example arguments to the script

    arguments = [var_getter('POSTGRESQL_NAME'), var_getter('POSTGRESQL_USER'), var_getter('POSTGRESQL_PASSWORD')]
    # Run the script and get the output
    output = run_bash_script(script_path, *arguments)

    # Print the output
    if output:
        print("Script Output:\n", output)