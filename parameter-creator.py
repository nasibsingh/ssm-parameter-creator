import os
import subprocess
import logging
from datetime import datetime
import json

# Function to create a new project
def create_new_project(base_path):
    new_project_name = input("Enter the name of the new project: ").strip()
    if not new_project_name:
        print("Project name cannot be empty.")
        return
    
    project_path = os.path.join(base_path, new_project_name)
    if os.path.exists(project_path):
        print(f"Project '{new_project_name}' already exists.")
        return
    
    os.makedirs(project_path)
    print(f"Project folder '{new_project_name}' created successfully.")

    # Prompt for environments to add
    print("Enter the environments to add (e.g., dev, stg, prod). Separate them by commas:")
    environments = input().strip().split(',')

    for env in environments:
        env_name = env.strip()
        if not env_name:
            continue
        env_path = os.path.join(project_path, env_name)
        os.makedirs(env_path, exist_ok=True)
        print(f"Environment folder '{env_name}' created for project '{new_project_name}'.")
    
    print(f"Project '{new_project_name}' setup completed.")
    logging.info(f"New project '{new_project_name}' with environments {environments} created.")


# Function to set up logging
def setup_logging(profile_name, project_name, environment):
    log_dir = f"logs/{profile_name}/{project_name}/{environment}"
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, f"log_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log")
    logging.basicConfig(filename=log_file, filemode='w', format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
    print(f"Logs will be stored in {log_file}")
    logging.info(f"Logging initiated for AWS profile: {profile_name}, Project: {project_name}, Environment: {environment}")

# Function to list sub-folders in a directory
def list_folders(path):
    return [f.name for f in os.scandir(path) if f.is_dir()]

# Function to choose an option from a list
def choose_option(options, prompt):
    print(prompt)
    for i, option in enumerate(options, start=1):
        print(f"{i}. {option}")
    while True:
        try:
            choice = int(input("Select an option (by number): "))
            if 1 <= choice <= len(options):
                return options[choice - 1]
            else:
                print("Invalid choice. Please choose a valid number.")
        except ValueError:
            print("Please enter a valid number.")

# Function to choose an AWS profile
def choose_aws_profile(profiles):
    return choose_option(profiles, "Available AWS Profiles:")

# Function to set the AWS CLI profile
def set_aws_profile(profile):
    os.environ['AWS_PROFILE'] = profile
    print(f"AWS CLI profile set to: {profile}")

# Function to check if a parameter exists and fetch its value
def get_existing_parameter(parameter_name):
    try:
        result = subprocess.run(
            ["aws", "ssm", "get-parameter", "--name", parameter_name, "--with-decryption"],
            capture_output=True, text=True, check=True
        )
        parameter_data = json.loads(result.stdout)
        return parameter_data['Parameter']['Value']
    except subprocess.CalledProcessError:
        return None

# Function to add tags to an existing parameter
def add_tags_to_parameter(parameter_name, tags):
    try:
        tag_list = [{"Key": tag["Key"], "Value": tag["Value"]} for tag in tags]
        command = ["aws", "ssm", "add-tags-to-resource", "--resource-type", "Parameter", "--resource-id", parameter_name, "--tags"]
        command.extend([f"Key={tag['Key']},Value={tag['Value']}" for tag in tag_list])
        subprocess.run(command, check=True)
        logging.info(f"Tags added/updated for {parameter_name}")
    except subprocess.CalledProcessError as e:
        logging.error(f"Error adding tags to parameter {parameter_name}: {e}")
        print(f"Error adding tags to parameter {parameter_name}: {e}")

# Function to create or update parameters in the AWS Parameter Store
def create_or_update_parameter_store(project_name, environment, env_file_path, kms_key_id=None, description=None, tags=None):
    logging.info(f"Creating parameters for project: {project_name}, environment: {environment} from {env_file_path}")
    
    if not os.path.exists(env_file_path):
        print(f"Environment file not found at {env_file_path}. Please check the folder structure.")
        return

    with open(env_file_path, 'r') as env_file:
        for line in env_file:
            if '=' in line and not line.startswith('#'):
                key, value = line.strip().split('=', 1)
                parameter_name = f"/{project_name}/{environment}/{key}"
                
                # Check if the parameter already exists
                existing_value = get_existing_parameter(parameter_name)
                
                if existing_value:
                    # Skip updating if the value is the same
                    if existing_value == value:
                        print(f"Parameter {parameter_name} already exists with the same value. Skipping update.")
                        logging.info(f"Skipped updating parameter {parameter_name} as the value is identical.")
                        continue
                    
                    print(f"\nParameter {parameter_name} already exists.")
                    print(f"Current Value: {existing_value}")
                    print(f"New Value: {value}")
                    
                    # Prompt for valid update choice
                    while True:
                        update_choice = input("Do you want to update it? (yes/no): ").strip().lower()
                        if update_choice in ['yes', 'no']:
                            break
                        else:
                            print("Invalid choice. Please enter 'yes' or 'no'.")
                    
                    if update_choice == 'no':
                        print(f"Parameter {parameter_name} was not updated as per your choice.")
                        logging.info(f"User chose not to update parameter {parameter_name}.")
                        continue

                # Command to create/update the parameter
                command = [
                    "aws", "ssm", "put-parameter",
                    "--name", parameter_name,
                    "--value", value,
                    "--overwrite" if existing_value else ""
                ]

                # Add description
                if description:
                    command.extend(["--description", description])
                
                # Use KMS Key ID for SecureString
                if kms_key_id:
                    command.extend(["--type", "SecureString", "--key-id", kms_key_id])
                else:
                    command.extend(["--type", "String"])

                # Run the put-parameter command (without tags for updates)
                try:
                    subprocess.run(command, check=True)
                    logging.info(f"Parameter {parameter_name} created/updated successfully.")
                    print(f"Parameter {parameter_name} created/updated successfully.")

                    # Add tags separately if the parameter was updated
                    # if existing_value:
                    add_tags_to_parameter(parameter_name, tags)
                
                except subprocess.CalledProcessError as e:
                    logging.error(f"Error creating/updating parameter {parameter_name}: {e}")
                    print(f"Error creating/updating parameter {parameter_name}: {e}")



# Main execution function
def main():
    environments_base_path = "environments"

    # Prompt to add a new project
    print("Do you want to add a new project? (yes/no):")
    add_project = input().strip().lower()
    if add_project == "yes":
        create_new_project(environments_base_path)
    
    aws_profiles = subprocess.run(["aws", "configure", "list-profiles"], capture_output=True, text=True).stdout.splitlines()
    if not aws_profiles:
        print("No AWS profiles found. Please configure at least one profile.")
        return

    selected_profile = choose_aws_profile(aws_profiles)
    set_aws_profile(selected_profile)

    available_projects = list_folders(environments_base_path)
    selected_project = choose_option(available_projects, "Available Projects:")

    project_env_path = os.path.join(environments_base_path, selected_project)
    available_environments = list_folders(project_env_path)
    selected_environment = choose_option(available_environments, f"Available Environments for {selected_project}:")

    setup_logging(selected_profile, selected_project, selected_environment)

    env_file_path = os.path.join(project_env_path, selected_environment, ".env")

    kms_key_id = "alias/aws/ssm"  # Optional, only if using SecureString
    description = f"Parameters for {selected_project} in {selected_environment}"
    tags = [
        {"Key": "Project", "Value": selected_project},
        {"Key": "Environment", "Value": selected_environment},
        # {"Key": "Owner", "Value": "your-team"}
    ]

    create_or_update_parameter_store(selected_project, selected_environment, env_file_path, kms_key_id, description, tags)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
    finally:
        logging.info("Script execution finished.")
