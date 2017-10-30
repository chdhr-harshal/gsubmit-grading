#!/usr/bin/python

'''
Filaneme            : create-hw-grade-file.py
Author              : Harshal Chaudhari
Creation Date       : 2017-10-05
Python Version      : 2.7
'''

import os
import argparse
import numpy as np
import pandas as pd
import json

# Get command line arguments
parser = argparse.ArgumentParser(description="Compile final grades file")
parser.add_argument('homework',
                    type=str,
                    help="Name of homework")
parser.add_argument('--grace',
                    type=int,
                    default=3,
                    help="Grace period given")
args = parser.parse_args()

# Paths
CURRENT_DIR = os.path.abspath(".")
GRADES_DIR = os.path.join(CURRENT_DIR, "grades", args.homework)
CONFIG_DIR = os.path.join(CURRENT_DIR, "configs")

# Read configs file
f = open(os.path.join(CONFIG_DIR, args.homework + "_config.json"), "r")
config = json.load(f)

# Read grades file
partwise_df = pd.read_csv(os.path.join(GRADES_DIR, "partwise_grades.csv"), sep=",", header=0)
grades_df = pd.read_csv(os.path.join(GRADES_DIR, "grades.csv"), sep=",", header=0)

final_grades_df = pd.merge(grades_df, partwise_df[['Username', 'Total']], on='Username')
max_points = config['Max Points']

# Add adjusted totals using the grace period
final_grades_df['AdjustedTotal'] = 0.0

def calculate_adjusted_total(s):
    total = s['Total']
    late_days = s['LateDays']
    if late_days > args.grace:
        return 0
    elif late_days <= 0:
        return total
    else:
        return np.ceil((total * (1-(0.1*late_days))*max_points) / max_points)

final_grades_df['AdjustedTotal'] = final_grades_df.apply(calculate_adjusted_total, axis=1)
del final_grades_df['Filename']
del final_grades_df['SubmissionDate']

# Export the grade file
final_grades_df.to_csv(os.path.join(GRADES_DIR, "final_grades.csv"), sep=",",
                      header=True, index=False)
