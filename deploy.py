import sys
from copy import copy
import os
import json
import requests
from pprint import pprint
import subprocess
from purepython.settings import SUPPORTED_LANGUAGES, LANGUAGE_CHOICE_DICT
from purepython.practice_translation import from_native_language
from polib import pofile
import site
import shutil

# Get the site-packages path
django_admin_locale_path = os.path.join(
    site.getsitepackages()[1], "django", "contrib", "admin", "locale"
)

PA_USERNAME = os.environ["PYTHONANYWHERE_USERNAME"]
PA_API_TOKEN = os.environ["PYTHONANYWHERE_API_KEY"]
DOMAIN_NAME = PA_USERNAME + ".pythonanywhere.com"
FABULARI_USERNAME = os.environ["FABULARI_USERNAME"]
FABULARI_PASSWORD = os.environ["FABULARI_PASSWORD"]


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
def update_locale_files():
    def populate_pofile(language: str):
        language_verbose = LANGUAGE_CHOICE_DICT[language]
        po = pofile(f"locale/{language}/LC_MESSAGES/django.po")

        # Loop through each msgid and translate if msgstr is empty
        for entry in po:
            if entry.obsolete:
                # script was marking this obsolete before
                entry.obsolete = False

            if not entry.msgstr:
                # Check if the entry is pluralized and has values in msgstr[0] or msgstr[1]

                if entry.msgid_plural:
                    # Skip certain django admin entries
                    continue  # Skip if both plural forms are already translated
                elif entry.msgstr:
                    continue  # Skip if singular form is already translated

                translated_text = from_native_language(
                    sentence=entry.msgid,
                    working_on_verbose=language_verbose,  # Adjust this for the target language
                    native_language_verbose="English",  # Adjust this for the source language
                    openai_llm_model="gpt-4o-mini",  # You can use other OpenAI models as well
                    is_phrases=True,
                )
                print(language, " | ", entry.msgid, " | ", translated_text)
                if translated_text:
                    entry.msgstr = translated_text
        po.save()

    # os.chdir(REPO_PATH)
    supported_languages_excluding_english = copy(SUPPORTED_LANGUAGES)
    supported_languages_excluding_english.remove("en")
    # supported_languages_excluding_english = ["es"]
    # supported_languages_excluding_english.remove("la")  # hack: remove latin
    for language_code in supported_languages_excluding_english:
        # os.makedirs(f"locale\\{language_code}\\LC_MESSAGES", exist_ok=True)
        # Create the target locale directory for your project
        target_locale_dir = os.path.join("locale", language_code, "LC_MESSAGES")
        os.makedirs(target_locale_dir, exist_ok=True)

        # Path to the admin .po file in Django's locale folder
        admin_po_file = os.path.join(
            django_admin_locale_path, language_code, "LC_MESSAGES", "django.po"
        )

        # Path to the target .po file in your project's locale directory
        target_po_file = os.path.join(target_locale_dir, "django.po")

        # Check if the admin .po file exists and the target .po file does not
        if os.path.exists(admin_po_file) and not os.path.exists(target_po_file):
            # Copy the admin .po file to your project's locale folder
            shutil.copy(admin_po_file, target_po_file)
            print(f"Copied {admin_po_file} to {target_po_file}")
        elif os.path.exists(target_po_file):
            print(f"Target .po file already exists: {target_po_file}")
        else:
            print(f"No admin .po file found for {language_code}")
        # subprocess.run(["mkdir", f"locale\\{language_code}\\LC_MESSAGES"])
    # assert False
    subprocess.run(["django-admin", "makemessages", "--all"])
    for language_code in supported_languages_excluding_english:
        populate_pofile(language=language_code)
    subprocess.run(["django-admin", "compilemessages"])  # mo files not in repo


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

from requests.auth import HTTPBasicAuth


def download_file_with_basic_auth(url, username, password, output_filename):
    # Send a GET request with basic authentication
    response = requests.get(url, auth=HTTPBasicAuth(username, password))

    # Check if the request was successful
    if response.status_code == 200:
        # Save the file
        with open(output_filename, "wb") as f:
            f.write(response.content)
        print(f"File downloaded successfully and saved as {output_filename}")
        return True
    else:
        print(f"Failed to download the file. Status code: {response.status_code}")
        return False


# Main script flow
def main():
    commit_message = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "unnamed commit"

    # untracked_files = get_untracked_files()
    # modified_files = get_modified_files()
    # if untracked_files:
    #     print("Untracked files:", untracked_files)
    # else:
    #     print("No untracked files.")

    print("Updating locale files...")
    update_locale_files()
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
    run_pythonanywhere_console_command("python manage.py compilemessages", console_id)
    run_pythonanywhere_console_command(
        "python manage.py dumpdata > ../dbbackup.json", console_id
    )

    # Step 3: Collect static files (optional step, you can comment it out if not needed)
    # print("Collecting static files...")
    # run_pythonanywhere_command("python manage.py collectstatic --noinput")

    # Step 4: Reload the web application
    print("Reloading the web app...")
    reload_web_app()
    print("Retrieving dbbackup.json...")
    download_file_with_basic_auth(
        url="https://" + DOMAIN_NAME + "/download_dbbackup_json",
        username=FABULARI_USERNAME,
        password=FABULARI_PASSWORD,
        output_filename="notinrepo/dbbackup.json",
    )
    run_pythonanywhere_console_command("rm ../dbbackup.json", console_id)


if __name__ == "__main__":
    main()
