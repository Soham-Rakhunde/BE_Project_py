Use conda create --name <env> --file requirements.txt to install all packages with correct versions
After adding a new pip package run this command from project directory: 
conda list -e > requirements.txt

TO save data run 
sender -> main.py
receiver -> test.py Just comment out rest of the path if u wnat

To retrieve data run
retreiver -> main.py but comment trackers code
stored computers -> test.py