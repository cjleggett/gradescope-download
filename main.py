from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import load_dotenv
import os
import csv
import time
import shutil
from jinja2 import Environment, FileSystemLoader

load_dotenv()
USER = os.getenv("USERNAME")
PASS = os.getenv("PASS")
COURSE_NO = os.getenv("COURSE_NO")
ASSIGNMENT_NO = os.getenv("ASSIGNMENT_NO")
BASE_URL = "https://www.gradescope.com"
ASSIGNMENT_URL = f"{BASE_URL}/courses/{COURSE_NO}/assignments/{ASSIGNMENT_NO}"

# Get most recent file read date:
with open("last_sweep.txt", "r") as f:
    last_sweep = f.read()

def open_browser():
    """Sets up chromedriver and opens browser"""
    options = webdriver.ChromeOptions()
    prefs = {
        "download.default_directory": f"{os.getcwd()}/downloads"
    }
    options.add_experimental_option("prefs", prefs)
    driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=options)
    return driver

def login(driver):
    """Logs into gradescope with username and password provided in .env file"""
    login_url = f"{BASE_URL}/login"
    driver.get(login_url)
    username_input = driver.find_element("id", "session_email")
    password_input = driver.find_element("id", "session_password")
    submit = driver.find_element("name", "commit")
    username_input.send_keys(USER)
    password_input.send_keys(PASS)
    submit.click()

def download_submission_csv(driver):
    """Downloads csv with info on submissions"""
    download_url = f"{ASSIGNMENT_URL}/scores.csv"
    driver.get(download_url)
    try:
        os.remove(f"{os.getcwd()}/downloads/csv/scores.csv")
    except FileNotFoundError:
        pass
    while True:
        time.sleep(1)
        files = os.listdir("downloads/")
        found = False
        for file in files:
            if ".csv" in file:
                if not os.path.isdir(f"downloads/csv"):
                    os.makedirs(f"downloads/csv")
                os.rename(f"downloads/{file}", f"downloads/csv/scores.csv")
                found = True
        if found:
            break

def get_tfs_dict():
    """Uses CSV to return dictionary in the form tf_name: list of students"""
    tfs = {}
    with open("downloads/csv/scores.csv", "r") as f:
        reader = csv.DictReader(f)
        most_recent = last_sweep
        for row in reader:
            tf = row["Sections"]
            if tf not in tfs:
                tfs[tf] = []
            if row["Submission Time"]:
                if row["Submission Time"] > most_recent:
                    most_recent = row["Submission Time"]
                tfs[tf].append({
                    "student": row["Name"],
                    "link": f"{ASSIGNMENT_URL}/submissions/{row['Submission ID']}.zip",
                    "submission_id": row["Submission ID"],
                    "sub_time": row["Submission Time"]
                })

    with open("last_sweep.txt", "w") as f:
        f.write(most_recent)
    return tfs

def setup_tf_folders(tfs):
    """Creates a new folder for each TF in the downloads folder"""
    for tf in tfs:
        if not os.path.isdir(f"downloads/{tf}"):
            os.makedirs(f"downloads/{tf}")

def manage_one_sub(tf, student, link, sub_id, driver):
    """Downloads one submission, unzips it, and places it in the correct file"""
    # Necessary to get rid of previous "file too large" message on page
    driver.get(BASE_URL)
    driver.get(link)
    try:
        alert = driver.find_element("css selector", ".l-header > div")
        return False
    except:
        pass
    while True:
        time.sleep(1)
        if f"{sub_id}.zip" in os.listdir("downloads/"):
            break
    os.rename(f"downloads/{sub_id}.zip", f"downloads/{tf}/{student}.zip")
    try:
        shutil.unpack_archive(f"downloads/{tf}/{student}.zip", f"downloads/{tf}/{student}")
        os.remove(f"downloads/{tf}/{student}.zip")
    except:
        print(f"Could not Unzip {student} in {tf}")
    return True

def download_subs(tfs, driver):
    """Download all submissions, keeping track of which are too big"""
    too_big = set()
    updated_tfs = set()
    sub_count = 0
    for tf, students in tfs.items():
        for student in students:
            sub_count += 1
            if student["sub_time"] > last_sweep:
                print(f"Downloading Submission {sub_count}")
                updated_tfs.add(tf)
                if not manage_one_sub(tf, student["student"], student["link"], student["submission_id"], driver):
                    too_big.add(student["student"])
    print("Changes made to:")
    for tf in updated_tfs:
        print(f"  - {tf}")
    return too_big

def create_homepage(tfs, too_big):
    """Creates an HTML file with links to students' index.html pages"""
    environment = Environment(loader=FileSystemLoader("templates/"))
    template = environment.get_template("template.html")
    for tf, students in tfs.items():
        students = {s["student"]: f"./{s['student']}/index.html" if s["student"] not in too_big else f"{ASSIGNMENT_URL}/submissions/{s['submission_id']}" for s in students}
        content = template.render(
            tf=tf,
            students=students
        )
        with open(f"downloads/{tf}/index.html", "w") as f:
            f.write(content)


def main():
    driver = open_browser()
    login(driver)
    download_submission_csv(driver)
    tfs = get_tfs_dict()
    setup_tf_folders(tfs)
    too_big = download_subs(tfs, driver)
    create_homepage(tfs, too_big)
    time.sleep(5)


main()