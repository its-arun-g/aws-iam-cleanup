# AWS Manager
A Python script to cleanup AWS access keys and IAM users in multiple accounts using AWS profiles. 

**NOTE** - Required profiles MUST be present in the `.aws/config` file
## Features
- Enable AWS access keys
- Disable AWS access keys
- Delete AWS access keys
- Disable console login for IAM users
- Delete IAM users

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

3. Usage  
    ```bash
    usage: main.py [-h] --object {key,user} --action {enable,disable,delete} --csv-file-path CSV_PATH --profile-name PROFILE [--threads THREADS]

    Manage AWS access keys and users.

    options:
    -h, --help               show this help message and exit
    --object {key,user}      The object to manage (key or user).
    --action {enable,disable,delete}
                             The action to perform (enable, disable, or delete).
    --profile-name           Profile name which is present for all required accounts.
    --csv-file-path CSV_PATH Path to CSV file with account_id and resource.
    --threads THREADS        Number of threads to use for processing.
    ```


### To enable AWS access keys
```bash
python3 main.py --object key --action enable --csv-file-path resources.csv --profile-name AdministratorAccess
```
### To disable AWS access keys
```bash
python3 main.py --object key --action disable --csv-file-path resources.csv --profile-name AdministratorAccess
```
### To delete AWS access keys
```bash
python3 main.py --object key --action delete --csv-file-path resources.csv --profile-name AdministratorAccess
```
### To disable console login for IAM users
```bash
python3 main.py --object user --action disable --csv-file-path resources.csv --profile-name AdministratorAccess
```
### To delete IAM users
```bash
python3 main.py --object user --action delete --csv-file-path resources.csv --profile-name AdministratorAccess
```
