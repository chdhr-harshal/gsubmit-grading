#!/usr/bin/python

'''
Filename        : pull-submissions.py
Author          : Harshal Chaudhari
Creation Date   : 2017-09-06
Python Version  : 2.7
'''

import os
import time
import argparse
from shutil import rmtree, copyfile
from datetime import datetime, timedelta
import tzlocal
import pandas as pd

local_timezone = tzlocal.get_localzone()

# Get command line arguments

parser = argparse.ArgumentParser(description="Pull homework submission files")
parser.add_argument('course',
                    type=str,
                    help="Course Number e.g. cs565")
parser.add_argument('--semester',
                    type=str,
                    default="current",
                    help="Semester in <Fall|Spring>-<YYYY> format e.g. Fall-2017")
parser.add_argument('path',
                    type=str,
                    default="data",
                    help="Homework submission directory")
parser.add_argument('deadline',
                    type=str,
                    help="Deadline in format YYYY-MM-DD")
parser.add_argument('--grace',
                    type=int,
                    default=0,
                    help="Grace period")
parser.add_argument('--students',
                    type=str,
                    default="students.csv",
                    help='Enrollment file containing students "Name", "ID", "Username"')
args = parser.parse_args()

# Gsubmit base path
path = os.path.join("/cs/course", args.course, args.semester, "homework/spool")
submission_students = os.listdir(path)

# Read students file
try:
    enrolled = pd.read_csv(args.students, sep=",", header=0)
except:
    exit("Students enrollment file not provided.")

# Create grades directory if it does not exists
if not os.path.exists("grades"):
    os.makedirs("grades")

# Create directory for submissions of the particular homework
if os.path.exists(os.path.join("grades", args.path)):
    rmtree(os.path.join("grades", args.path))
os.makedirs(os.path.join("grades", args.path))

# Create and clear directory for storing submission files
if not os.path.exists("submissions"):
    os.makedirs("submissions")

# Create directory for submissions of the particular homework
if os.path.exists(os.path.join("submissions", args.path)):
    rmtree(os.path.join("submissions", args.path))
os.makedirs(os.path.join("submissions", args.path))

# Pull submissions
submissions = []

for index, student in enrolled.iterrows():
    if student['Username'] not in submission_students:
        print "Student {} has not made a submission ever".format(student['Username'])
        continue

    student_dict = {}
    student_dict['Name'] = student['Name']
    student_dict['ID'] = student['ID']
    student_dict['Username'] = student['Username']
    student_dict['Filename'] = None
    student_dict['SubmissionDate'] = None
    student_dict['LateDays'] = 0

    if os.path.exists(os.path.join(path, student['Username'], args.path)):
        print "Pulling {} submission for student {}".format(args.path, student['Username'])

        submission_dir = os.path.join(path, student['Username'], args.path)
        try:
            homework_file = os.listdir(submission_dir)[0]
        except:
            print "No file exists"
            continue

        filepath = os.path.join(path, student['Username'], args.path, homework_file)
        ctime = os.path.getctime(filepath)
        ctime = datetime.fromtimestamp(ctime, local_timezone)
        ctime = ctime.strftime("%Y-%m-%d %H:%M:%S")
        ctime = datetime.strptime(ctime, "%Y-%m-%d %H:%M:%S")

        student_dict['Filename'] = student['Username'] + ".pdf"
        student_dict['SubmissionDate'] = ctime.strftime("%Y-%m-%d %H:%M:%S")
        student_dict['LateDays'] = (ctime - datetime.strptime(args.deadline, "%Y-%m-%d %H:%M:%S")).days

        # Copy submission file and store as username.pdf
        copyfile(filepath, os.path.join("submissions", args.path, student['Username'] + ".pdf"))

    submissions.append(student_dict)

# Create and save gradefile which would be filled later
gradefile = pd.DataFrame(submissions)
gradefile.to_csv(os.path.join("grades", args.path, "grades.csv"), sep=",", header=True, index=False)
