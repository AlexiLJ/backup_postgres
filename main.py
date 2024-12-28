import re
import subprocess
import boto3
import logging
from pathlib import Path
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
from env_handler import var_getter

logging.basicConfig(
    level=logging.INFO,  # Set to DEBUG for more detailed logs
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("upload_to_s3.log"),  # Log to a file
        logging.StreamHandler()  # Log to the console
    ]
)

parent_path = Path(__file__).resolve().parent

def run_bash_script(script_path: Path, *args) -> str | None:
    """
    Runs a bash script with optional arguments and returns its output.

    :param script_path: Path to the bash script
    :param args: Arguments to pass to the script
    :return: str|None The standard output of the bash script
    """
    try:
        command = ["bash", script_path] + list(args)
        # Run the bash script and capture its output
        result = subprocess.run(command, check=True, text=True, capture_output=True)
        return result.stdout.strip()

    except subprocess.CalledProcessError as e:
        logging.error("Error executing script: %s", e)
        logging.error("Error Output: %s", e.stderr)
        return None

def upload_to_s3(file_path, bucket_name, directory, region="us-east-1"):
    """
    Uploads a file to a specific directory in an S3 bucket.

    :param file_path: Path to the local file to upload
    :param bucket_name: Name of the S3 bucket
    :param directory: Directory (prefix) in the S3 bucket where the file should be uploaded
    :param region: AWS region of the S3 bucket (default is 'us-east-1')
    :return: str The S3 URL of the uploaded file if successful
    """
    try:
        logging.info("Starting the upload process.")
        # Extract the file name from the local file path
        file_name = file_path.split("/")[-1]
        logging.debug("File name extracted: %s", file_name)
        # Construct the full S3 key (directory + file name)
        s3_key = f"{directory}/{file_name}" if directory else file_name

        s3_client = boto3.client('s3',
                                 aws_access_key_id=var_getter('AWS_ACCESS_KEY_ID', path=parent_path),
                                 aws_secret_access_key=var_getter('AWS_SECRET_ACCESS_KEY', path=parent_path),
                                 region_name=region)

        logging.info("Uploading to file '%s' to the '%s'.", file_name, s3_key)
        s3_client.upload_file(file_path, bucket_name, s3_key)
        # Generate the S3 URL
        s3_url = f"https://{bucket_name}.s3.{region}.amazonaws.com/{s3_key}"
        logging.info("File '%s' successfully uploaded to '%s'.", file_path, s3_url)
        return s3_url

    except FileNotFoundError:
        logging.error("Error: The file '%s' was not found.", file_path)
    except NoCredentialsError:
        logging.error("Error: AWS credentials not found.")
    except PartialCredentialsError:
        print("Error: Incomplete AWS credentials.")
    except Exception as e:
        logging.error("An unexpected error occurred: %s", e)
        raise

if __name__ == "__main__":
    script_path = parent_path / 'backup_postgres.sh'
    arguments = [var_getter('POSTGRESQL_NAME', path=parent_path),
                 var_getter('POSTGRESQL_USER', path=parent_path),
                 var_getter('POSTGRESQL_PASSWORD', path=parent_path),
                 str(parent_path)
                ]

    output = run_bash_script(script_path, *arguments)
    if output:
        logging.info("Script Output: '%s'", output)
        pattern = r"(/home[^ ]*?/backup_postgres[^ ]*?\.dump)"
        matches = re.findall(pattern, output)
        logging.info("PG dump file names: '%s'", matches)

        upload_to_s3(file_path=matches[0],
                     bucket_name=var_getter('AWS_STORAGE_BUCKET_NAME', path=parent_path),
                     directory='pg_backups',
                     region=var_getter('AWS_S3_REGION_NAME', path=parent_path)
                     )
    else:
        logging.error("No stdout returned.")