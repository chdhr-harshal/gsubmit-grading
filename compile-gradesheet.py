#!/usr/local/bin/python

'''
Filaname        : compile-gradesheet.py
Author          : Harshal Chaudhari
Creation Date   : 2017-10-07
Python Version  : 2.7
'''

import os
import argparse
import numpy as np
import pandas as pd

# Get command line arguments
parser = argparse.ArgumentParser(description="Compile gradsheet with grades of all homeworks")
parser.add_argument('homework',
                    type=str,
                    help="Homeworks to add grades from")
parser.add_argument('--course',
                    type=str,
                    default="cs565",
                    help="Course name")
parser.add_argument('--students',
                    type=str,
                    default="students.csv",
                    help='Enrollment file containing students "Name", "ID", "Username"')
args = parser.parse_args()

# Paths
CURRENT_DIR = os.path.abspath(".")
GRADES_DIR = os.path.join(CURRENT_DIR, "grades", args.homework)

# Read students csv file
enrolled_df = pd.read_csv(args.students, sep=",", header=0)

# Read course grade file if any or create one
try:
    grades_df = pd.read_csv(args.course + '_grades.csv', sep=",", header=0)
except:
    grades_df = enrolled_df

# Read homework grade file
hw_grades_df = pd.read_csv(os.path.join(GRADES_DIR, "final_grades.csv"), sep=",", header=0)

combined_grades_df = pd.merge(grades_df, hw_grades_df[['AdjustedTotal', 'Username']], on='Username')

# Rename column to homework name
grades_df = combined_grades_df.rename(columns={'AdjustedTotal': args.homework})

# Export course grade file
grades_df.to_csv(args.course + '_grades.csv', sep=",", header=True, index=False)
