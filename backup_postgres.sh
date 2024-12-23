#!/bin/bash

# Check if the required arguments are provided
if [ $# -lt 1 ]; then
    echo "Usage: $0 <db_name> [username] [host] [port] [backup_dir]"
    exit 1
fi

# Get parameters
DB_NAME=$1                       # The first argument is the database name
DB_USER=$2                        
DB_HOST=${3:-localhost}          # Optional: Defaults to 'localhost' if not provided
DB_PORT=${4:-5432}               # Optional: Defaults to '5432' if not provided
BACKUP_DIR=${5:-/backups}        # Optional: Defaults to '/backups' if not provided

# Generate the backup filename
TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")
BACKUP_FILE="$BACKUP_DIR/${DB_NAME}_backup_$TIMESTAMP.dump"

# Ensure the backup directory exists

mkdir -p "$BACKUP_DIR"
if [ $? -ne 0 ]; then
    echo "Failed to create directory: $BACKUP_DIR"
    exit 1
fi
echo "Directory created successfully: $BACKUP_DIR"
# Create the database dump in custom format (.dump)
echo "Starting backup for database: $DB_NAME"
pg_dump -U "$DB_USER" -h "$DB_HOST" -p "$DB_PORT" -F c -f "$BACKUP_FILE" "$DB_NAME"

# Check if the dump was successful
if [ $? -eq 0 ]; then
    echo "Backup successful! File saved to: $BACKUP_FILE"
else
    echo "Backup failed!"
    exit 1
fi

# Optional: Remove old backups (e.g., older than 7 days)
#find "$BACKUP_DIR" -type f -name "${DB_NAME}_backup_*.dump" -mtime +7 -exec rm {} \;
#echo "Old backups cleaned up."

exit 0
