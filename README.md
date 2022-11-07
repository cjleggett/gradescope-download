# Gradescope Downloader

### Connor Leggett
### 11/06/2022

This code is meant to download submissions from Gradescope, sort them by TF, and create a homepage for each TF to provide easier access to homepage submissions. This is necessary because while Gradescope does allow you to download all submissions at once, the download can take a couple of hours, and if any changes occur such as new submissions or submissions being graded, the process is terminated. With a class of 500+ students, it is nearly impossible to go several hours without any changes being made.

## Setup

1. Configure Environment
   1. Clone/Fork this repository, then navigate to the appropriate directory
   2. Use `conda env create -f environment.yml` to create the new environment
   3. Activate your new environment with `conda activate gradescope_download`
2. Provide Environment Variables: Create a file titled `.env` and fill it using the template below:
```
USERNAME=[Your Gradescope Username]
PASS=[Your Gradescope Password]
COURSE_NO=[The Gradescope Course Number]
ASSIGNMENT_NO=[The Gradescope Assignment Number]
```
3. Set start time. To save time, this program will not download the same submission twice, so it keeps track of the submission time of the most recent submission. When downloading for the first time, edit `last_sweep.txt` to a date from last year

## Usage

Run the program by navigating to the appropriate directory and running
```bash
python main.py
```

## Output

When the program finishes running, there will be a folder for each TF in the `downloads` directory, which contains a directory for each of their students' projects, and an `index.html` file which will allow them to easily navigate to most of their students websites. A list of TFs whos folders have been updated will be printed to the terminal, which will be helpful in managing late submissions, as only those TFs need to have their folders updated.

## Distribution

The best way I've found in the past for distributing these files is by uploading these folders to Google Drive and sharing them with each TF. It would be an interesting future task to automate this process.