import re
import subprocess
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
from env_handler import var_getter
from pathlib import Path

parent_path = Path(__file__).resolve().parents[:-2]
print(parent_path)

def run_bash_script(script_path, *args):
    """
    Runs a bash script with optional arguments and returns its output.
    :param script_path: Path to the bash script
    :param args: Arguments to pass to the script
    :return: The standard output of the bash script
    """
    try:
        command = ["bash", script_path] + list(args)
        # Run the bash script and capture its output
        result = subprocess.run(command, check=True, text=True, capture_output=True)
        # Return the script's standard output
        return result.stdout.strip()

    except subprocess.CalledProcessError as e:
        print("Error executing script:", e)
        print("Error Output:\n", e.stderr)
        return None

def upload_to_s3(file_path, bucket_name, directory, region="us-east-1"):
    """
    Uploads a file to a specific directory in an S3 bucket.

    Args:
        file_path (str): Path to the local file to upload.
        bucket_name (str): Name of the S3 bucket.
        directory (str): The directory (prefix) in the S3 bucket where the file should be uploaded.
        region (str): AWS region of the S3 bucket (default is 'us-east-1').

    Returns:
        str: The S3 URL of the uploaded file if successful.
    """
    try:
        # Extract the file name from the local file path
        file_name = file_path.split("/")[-1]

        # Construct the full S3 key (directory + file name)
        s3_key = f"{directory}/{file_name}" if directory else file_name

        # Create an S3 client
        s3_client = boto3.client('s3',
                                 aws_access_key_id=var_getter('AWS_ACCESS_KEY_ID', path=parent_path),
                                 aws_secret_access_key=var_getter('AWS_SECRET_ACCESS_KEY', path=parent_path),
                                 region_name=region)

        # Upload the file
        s3_client.upload_file(file_path, bucket_name, s3_key)

        # Generate the S3 URL
        s3_url = f"https://{bucket_name}.s3.{region}.amazonaws.com/{s3_key}"
        print(f"File uploaded successfully to {s3_url}")
        return s3_url

    except FileNotFoundError:
        print(f"Error: The file {file_path} was not found.")
    except NoCredentialsError:
        print("Error: AWS credentials not found.")
    except PartialCredentialsError:
        print("Error: Incomplete AWS credentials.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    # Replace with the actual path to your bash script
    script_path = parent_path / 'backup_postgres.sh'

    # Example arguments to the script
    arguments = [var_getter('POSTGRESQL_NAME', path=parent_path),
                 var_getter('POSTGRESQL_USER', path=parent_path),
                 var_getter('POSTGRESQL_PASSWORD', path=parent_path)]

    # Run the script and get the output
    output = run_bash_script(script_path, *arguments)
    # Print the output
    if output:
        print("Script Output:\n", output)
        pattern = r"(/home[^ ]*?/backup_postgres[^ ]*?\.dump)"
        matches = re.findall(pattern, output)
        print("Script Output:\n", matches)

        upload_to_s3(file_path=matches[0],
                     bucket_name=var_getter('AWS_STORAGE_BUCKET_NAME', path=parent_path),
                     directory='pg_backups',
                     region=var_getter('AWS_S3_REGION_NAME', path=parent_path)
                     )