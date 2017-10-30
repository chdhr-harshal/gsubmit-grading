#!/usr/bin/python

'''
Filename            : push-grades.py
Author              : Harshal Chaudhari
Creation Date       : 2017-10-03
Python Version      : 2.7
'''

import os
import argparse
import numpy as np
import pandas as pd
import json
from email.mime.text import MIMEText
from subprocess import Popen, PIPE

'''
Working example

msg = MIMEText("This is a test message.\nWhat the heck is this?")
msg["From"] = "harshal@bu.edu"
msg["To"] = "harshvoldy@gmail.com"
msg["Subject"] = "Data Mining homework grade."
p = Popen(["/usr/sbin/sendmail", "-t", "-oi"], stdin=PIPE)
p.communicate(msg.as_string())

'''

# Get command line arguments
parser = argparse.ArgumentParser(description="Send grades to students via emails")
parser.add_argument('homework',
                    type=str,
                    help="Name of homework")
args = parser.parse_args()

# Paths
CURRENT_DIR = os.path.abspath(".")
GRADES_DIR = os.path.join(CURRENT_DIR, "grades", args.homework)
CONFIG_DIR = os.path.join(CURRENT_DIR, "configs")

# Read partwise grades file
partwise_grades_df = pd.read_csv(os.path.join(GRADES_DIR, "partwise_grades.csv"), sep=",", header=0, index_col='Username')
final_grades_df = pd.read_csv(os.path.join(GRADES_DIR, "final_grades.csv"), sep=",", header=0, index_col='Username')

# Read config file
f = open(os.path.join(CONFIG_DIR, args.homework + "_config.json"), "r")
config = json.load(f)

# Create message body
for student in partwise_grades_df.index:
    msg = '''Username: {}\n--------------------\n'''.format(student)
    total_points = config['Max Points']
    total_points_scored = final_grades_df.loc[student]['Total']
    late_days = final_grades_df.loc[student]['LateDays']
    adjusted_total = final_grades_df.loc[student]['AdjustedTotal']
    msg += "Total Points: {}/{}\n".format(total_points_scored, total_points)
    msg += "Late Days: {}\n".format(late_days)
    msg += "Adjusted total points with late penalty: {}\n\n".format(adjusted_total)
    msg += "---------------------\nDetailed Grades\n---------------------\n"
    for exercise in config['Exercises']:
        for part in exercise['Parts']:
            max_points = part['Points']
            problem_number = exercise['Name'] + '.' + part['Name']
            points_scored = partwise_grades_df.loc[student][problem_number]
            comments = partwise_grades_df.loc[student][problem_number + "_comments"]
            msg += "Problem {}: {}/{}\n".format(problem_number, points_scored, max_points)
            msg += "Grader comments: {}\n\n".format(comments)
    msg += "---------------------\n---------------------\n"
    msg += "For grade disputes, please reply to this email.\n\n"
    msg += "--Harshal"
    if not pd.isnull(late_days):
        msg = MIMEText(msg)
        msg["From"] = "harshal@bu.edu"
        msg["To"] = "{}@bu.edu".format(student)
        # msg["To"] = "harshvoldy@gmail.com"
        msg["Subject"] = "CS565 homework grade for {}.".format(args.homework)
        p = Popen(["/usr/sbin/sendmail", "-t", "-oi"], stdin=PIPE)
        p.communicate(msg.as_string())
        print "Sent grade to {}".format(student)
