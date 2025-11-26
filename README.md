# AWS IAM Cleanup Tool
A Python script to cleanup AWS access keys and IAM users across multiple accounts using cross-account role assumption.

## Features
- Enable AWS access keys
- Disable AWS access keys
- Delete AWS access keys
- Disable console login for IAM users
- Delete IAM users
- 2-tier cross-account role assumption
- Multi-threaded processing

## Prerequisites
- AWS credentials configured in your environment (via AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, etc.)
- A role in the central account that your current credentials can assume
- The same role name must exist in all target accounts (with appropriate trust policies)
- The central account role must have permission to assume the same role in target accounts

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/its-arun-g/Aws-keys-cleanup.git
    ```
2. Set up the environment:
    ```bash
    python3 -m venv .venv && \
    source .venv/bin/activate && \
    pip install -r requirements.txt
    ```

3. Set AWS environment variables for your central account:
    ```bash
    export AWS_ACCESS_KEY_ID=your_access_key
    export AWS_SECRET_ACCESS_KEY=your_secret_key
    export AWS_SESSION_TOKEN=your_session_token  # if using temporary credentials
    ```

## CSV File Format
The CSV file should contain two columns:
- `account_id`: The AWS account ID where the resource exists
- `object`: The access key ID (e.g., `AKIA...`) or IAM username

Example `resources.csv`:
```csv
account_id,object
123456789012,AKIAIOSFODNN7EXAMPLE
123456789012,john.doe
987654321098,AKIAI44QH8DHBEXAMPLE
987654321098,jane.smith
```

## Usage
```bash
usage: main.py [-h] --object {key,user} --action {enable,disable,delete} --csv-file-path CSV_FILE_PATH --central-account-id CENTRAL_ACCOUNT_ID --role-name ROLE_NAME [--threads THREADS]

Manage AWS access keys and users across multiple accounts using 2-tier role assumption.

options:
  -h, --help                    show this help message and exit
  --object {key,user}           The object type to manage (key or user).
  --action {enable,disable,delete}
                                The action to perform (enable, disable, or delete).
  --csv-file-path CSV_FILE_PATH Path to CSV file with account_id and object columns.
  --central-account-id CENTRAL_ACCOUNT_ID
                                Central AWS account ID where the initial role exists.
  --role-name ROLE_NAME         Name of the IAM role (same name in central account and all target accounts).
  --threads THREADS             Number of threads to use for processing (default: 1).
```

### Examples

#### Delete access keys
```bash
python3 main.py --object key --action delete --csv-file-path resources.csv --central-account-id 783023365380 --role-name CrossAccountRole --threads 5
```

#### Delete IAM users
```bash
python3 main.py --object user --action delete --csv-file-path resources.csv --central-account-id 783023365380 --role-name CrossAccountRole --threads 5
```

#### Disable access keys
```bash
python3 main.py --object key --action disable --csv-file-path resources.csv --central-account-id 783023365380 --role-name CrossAccountRole --threads 5
```

#### Enable access keys
```bash
python3 main.py --object key --action enable --csv-file-path resources.csv --central-account-id 783023365380 --role-name CrossAccountRole --threads 5
```

#### Disable console login for users
```bash
python3 main.py --object user --action disable --csv-file-path resources.csv --central-account-id 783023365380 --role-name CrossAccountRole --threads 5
```

## How It Works (2-Tier Role Assumption)
1. The script reads the CSV file and groups resources by account ID
2. **First Tier**: It assumes the central account role using your current AWS credentials (from environment variables)
3. **Second Tier**: For each target account, it uses the central account role credentials to assume the cross-account role in that account
4. It processes all objects in the CSV as the specified type (key or user) based on the `--object` parameter
5. Resources are processed concurrently using the specified number of threads
6. All operations are logged with timestamps and account information

### Role Assumption Flow
```
Your Credentials (env vars)
    ↓
Central Account Role (--central-account-id, --role-name)
    ↓
Target Account Role (--role-name) in each target account
    ↓
Perform IAM operations (delete/disable keys or users)
```
