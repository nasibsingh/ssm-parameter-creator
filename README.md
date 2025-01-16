README: AWS Project Manager Script
==================================

Overview
--------

This script is designed to streamline the management of AWS environments and projects. It allows users to:

-   Create project directories with environment-specific folders.
-   Manage AWS SSM Parameter Store parameters efficiently.
-   Add logging functionality for tracking script activities.

Prerequisites
-------------

### 1\. Python

Ensure you have Python 3.6+ installed. This script is tested with Python 3.11.3.

### 2\. AWS CLI

Install and configure the AWS CLI. At least one AWS profile should be set up beforehand.

### 3\. Required Permissions

Ensure your AWS IAM user or role has the following permissions:

-   `ssm:GetParameter`
-   `ssm:PutParameter`
-   `ssm:AddTagsToResource`
-   `ssm:GetParametersByPath`

### 4\. Directory Structure

-   Create a base directory named `environments` in the script's location.
-   Inside `environments`, store project-specific folders with environment sub-folders (e.g., `dev`, `stg`, `prod`).

### 5\. Dependencies

Install required Python libraries using:

```
pip install -r requirements.txt
```

*(If you are using external libraries for logging or subprocess extensions)*

Features
--------

### 1\. **Project Management**

-   Create new projects with environment-specific folders.
-   Add environments dynamically during project setup.

### 2\. **AWS Profile Management**

-   Select AWS CLI profiles dynamically during execution.

### 3\. **Parameter Store Management**

-   Automatically create or update parameters in AWS SSM Parameter Store.
-   Skip parameters with unchanged values.
-   Prompt to update existing parameters with different values.
-   Add custom tags to parameters.

### 4\. **Logging**

-   Logs are saved in `logs/<profile_name>/<project_name>/<environment>/`.
-   Log filenames include timestamps for better traceability.

Usage
-----

### Step 1: Run the Script

Execute the script:

```
python script_name.py
```

### Step 2: Add a New Project

When prompted:

1.  Choose to add a new project.
2.  Enter the project name.
3.  Specify the environments (comma-separated, e.g., `dev,stg,prod`).

### Step 3: Select AWS Profile

Choose an AWS profile from the list of configured profiles.

### Step 4: Select Project and Environment

Choose a project and its environment from the available options.

### Step 5: Manage Parameters

The script will:

1.  Read `.env` files from the selected environment folder.
2.  Check for existing parameters in AWS SSM Parameter Store.
3.  Skip, update, or create parameters based on user input.

### Step 6: Logging

Check the logs in the directory `logs/<profile_name>/<project_name>/<environment>/` for details about the execution.

Sample Directory Structure
--------------------------

```
project-folder/
|-- environments/
|   |-- ProjectA/
|   |   |-- dev/
|   |   |   |-- .env
|   |   |-- stg/
|   |   |-- prod/
|-- logs/
    |-- profile1/
        |-- ProjectA/
            |-- dev/
                |-- log_2025-01-16_12-00-00.log
```

Environment File Format
-----------------------

The `.env` file should contain key-value pairs in the following format:

```
KEY=value
ANOTHER_KEY=another_value
```

Script Output
-------------

-   Successful execution logs.
-   Prompts for user input if updates are required for existing parameters.
-   Error messages if issues occur during AWS operations.

Customization
-------------

### Change KMS Key for SecureString Parameters

Update the variable `kms_key_id` in the `create_or_update_parameter_store` function with your desired KMS key alias or ARN.

### Add Custom Tags

Modify the `tags` list in the script to include additional key-value pairs for tagging parameters.

Error Handling
--------------

-   Logs all errors in the log file.
-   Prints user-friendly error messages to the console for immediate resolution.

Future Enhancements
-------------------

-   Add advanced security features.
-   Enable cloud-based logging and monitoring.
-   Provide a graphical interface for easier management.

Troubleshooting
---------------

-   Ensure the `environments` directory and its structure are correctly set up.
-   Verify AWS CLI configuration and permissions.
-   Check the logs for detailed error messages.
