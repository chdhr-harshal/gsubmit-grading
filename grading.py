#!/usr/bin/python

'''
Filename            : grading.py
Author              : Harshal Chaudhari
Creation Date       : 2017-10-03
Python Version      : 2.7
'''

import os
import time
import argparse
from datetime import datetime, timedelta
import pandas as pd
import json
from lazyme.string import *

# Get command line arguments

parser = argparse.ArgumentParser(description="Used while grading")
parser.add_argument('homework',
                    type=str,
                    help="Name of homework")
args = parser.parse_args()

# Paths
CURRENT_DIR = os.path.abspath(".")
SUBMISSIONS_DIR = os.path.join(CURRENT_DIR, "submissions", args.homework)
GRADES_DIR = os.path.join(CURRENT_DIR, "grades", args.homework)
CONFIG_DIR = os.path.join(CURRENT_DIR, "configs")

# Read grades file
grades_df = pd.read_csv(os.path.join(GRADES_DIR, "grades.csv"), sep=",", header=0)

# Read config file
f = open(os.path.join(CONFIG_DIR, args.homework + "_config.json"), "r")
config = json.load(f)

# Start grading
grades_list = []

for x in grades_df.index[:5]:
    grade_dict = {}
    grade_dict['Username'] = grades_df.ix[x]['Username']

    for exercise in config['Exercises']:
        for part in exercise['Parts']:
            grade_dict[exercise['Name'] + "." + part['Name']] = 0

    grade_dict['Total'] = 0

    if pd.isnull(grades_df.ix[x]['Filename']):
        grades_list.append(grade_dict)
        continue

    color_print(str(x) + ": " + grades_df.ix[x]['Username'] + " ", color="black", highlight="yellow")

    for exercise in config['Exercises']:
        for part in exercise['Parts']:
            color_print(exercise['Name'] + "." + part['Name'], color="red")
            print "Grading tip: {}".format(part['Tip'])
            print "Max. points: {}".format(part['Points'])
            grade_dict[exercise['Name'] + "." + part['Name']] = int(raw_input("Points awarded: ") or 0)
            grade_dict[exercise['Name'] + "." + part['Name'] + "_comments"] = raw_input("Comments: ")
            grade_dict['Total'] += grade_dict[exercise['Name'] + "." + part['Name']]

    print "-----------------------"
    color_print("Total grade: {}".format(grade_dict['Total']), color="green")
    print "-----------------------\n"
    grades_list.append(grade_dict)

    # Compile final grades df
    updated_grades_df = pd.DataFrame(grades_list)
    updated_grades_df.to_csv(os.path.join(GRADES_DIR, "partwise_grades.csv"), sep=",",
                            header=True, index=False)
