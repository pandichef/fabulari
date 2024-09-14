import sys
import os
import json
import requests
from pprint import pprint
import subprocess

PA_USERNAME = os.environ["PYTHONANYWHERE_USERNAME"]
PA_API_TOKEN = os.environ["PYTHONANYWHERE_API_KEY"]
DOMAIN_NAME = PA_USERNAME + ".pythonanywhere.com"

# Step 0: Get account status
def get_pythonanywhere_account_status():
    response = requests.get(
        f"https://www.pythonanywhere.com/api/v0/user/{PA_USERNAME}/cpu/",
        headers={"Authorization": f"Token {PA_API_TOKEN}"},
    )
    if response.status_code == 200:
        print("--- CPU quota info ---")
        pprint(json.loads(response.content.decode("utf-8")))
    else:
        print(
            "Got unexpected status code {}: {!r}".format(
                response.status_code, response.content
            )
        )


# Step 1: Commit and push to git
def git_commit(commit_message):
    # os.chdir(REPO_PATH)
    subprocess.run(["git", "add", "."])
    subprocess.run(["git", "commit", "-m", commit_message])
    subprocess.run(["git", "push"])


# Step 2: Call PythonAnywhere API to run commands
def get_pythonanywhere_console_id():
    # url = f"https://www.pythonanywhere.com/api/v0/user/{PA_USERNAME}/consoles/"
    # headers = {"Content-Type": "application/json"}
    # headers =
    # data = {"command": command, "bash": True}
    response = requests.get(
        f"https://www.pythonanywhere.com/api/v0/user/{PA_USERNAME}/consoles/",
        headers={"Authorization": f"Token {PA_API_TOKEN}"},
    )
    try:
        response_dict = json.loads(response.content.decode("utf-8"))[
            0
        ]  # Get the first avaiable console
    except IndexError:
        raise IndexError(
            "There are no open consoles on pythonanywhere.com.  Create one in the browser first and try again."
        )
    # print(response.status_code)
    # pprint(response_dict)
    if response.status_code == 200:
        print(f"Found console ID {response_dict['id']}.")
        return response_dict["id"]
    else:
        print(f"Failed to run get_pythonanywhere_console_id.")
        return None


# Step 3: Call PythonAnywhere API to run commands
def run_pythonanywhere_console_command(command, console_id):
    # headers = {"Content-Type": "application/json"}
    # headers = {"Authorization": "Token {token}".format(token=PA_API_TOKEN)}
    # data = {"command": command, "bash": True}
    response = requests.post(
        f"https://www.pythonanywhere.com/api/v0/user/{PA_USERNAME}/consoles/{console_id}/send_input/",
        headers={"Authorization": f"Token {PA_API_TOKEN}"},
        json={"input": command + "\n"},
    )
    # print(response.status_code)
    if response.status_code == 200:
        print(f"Command '{command}' executed successfully.")
    else:
        print(
            f"Failed to run '{command}'. Status code: {response.status_code}, Error: {response.text}"
        )


# Step 3: Reload the PythonAnywhere web app
def reload_web_app():
    # webapp_url = PA_USERNAME + "pythonanywhere.com"
    # url =
    response = requests.post(
        f"https://www.pythonanywhere.com/api/v0/user/{PA_USERNAME}/webapps/{DOMAIN_NAME}/reload/",
        headers={"Authorization": f"Token {PA_API_TOKEN}"},
    )
    if response.status_code == 200:
        print("Web app reloaded successfully.")
    else:
        print(
            f"Failed to reload the web app. Status code: {response.status_code}, Error: {response.text}"
        )


# def get_untracked_files():
#     result = subprocess.run(
#         ["git", "ls-files", "--others", "--exclude-standard"],
#         stdout=subprocess.PIPE,
#         text=True,
#     )
#     # Split the output by newline to get a list of files
#     untracked_files = result.stdout.splitlines()
#     return untracked_files


# def get_modified_files():
#     result = subprocess.run(
#         ["git", "diff", "--name-only"], stdout=subprocess.PIPE, text=True
#     )
#     # Split the output by newline to get a list of files
#     modified_files = result.stdout.splitlines()
#     return modified_files


# Main script flow
def main():
    commit_message = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "unnamed commit"

    # untracked_files = get_untracked_files()
    # modified_files = get_modified_files()
    # if untracked_files:
    #     print("Untracked files:", untracked_files)
    # else:
    #     print("No untracked files.")

    # print("######################################################")
    # print(f"NEW FILES     : {', '.join(untracked_files)}")
    # print(f"MODIFIED FILES: {', '.join(modified_files)}")
    print("######################################################")
    subprocess.run(["git", "status"])
    print("######################################################")
    print(f"COMMIT MESSAGE: {commit_message}")
    print("######################################################")
    user_input = (
        input("Do you want to continue with this deployment (yes/no): ").strip().lower()
    )
    if user_input not in ["y", "ye", "yes"]:
        print("Deployment aborted.")
        return

    # Step 1: Commit and push to git
    print("Committing and pushing to git...")
    git_commit(commit_message)

    # Step 2: Run database migrations on PythonAnywhere
    console_id = get_pythonanywhere_console_id()
    # Step 3: Run database migrations on PythonAnywhere
    print("Running console commands.")
    run_pythonanywhere_console_command("cd ~/fabulari", console_id)
    run_pythonanywhere_console_command("git pull", console_id)
    run_pythonanywhere_console_command("python manage.py migrate", console_id)
    run_pythonanywhere_console_command(
        "python manage.py collectstatic --no-input", console_id
    )

    # Step 3: Collect static files (optional step, you can comment it out if not needed)
    # print("Collecting static files...")
    # run_pythonanywhere_command("python manage.py collectstatic --noinput")

    # Step 4: Reload the web application
    print("Reloading the web app...")
    reload_web_app()


if __name__ == "__main__":
    main()
