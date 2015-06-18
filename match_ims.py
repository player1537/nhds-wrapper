#!/usr/bin/python

from __future__ import division
import csv
import collections
import datetime
import calendar

START_DATE = datetime.datetime(year=2009, month=4, day=1)
END_DATE = datetime.datetime(year=2010, month=4, day=1)

def main(filenames, icd9_prefix=""):
    counts = collections.defaultdict(int)
    for filename in filenames:
        with open(filename, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row["diagnosis_code_#1"][:len(icd9_prefix)] != icd9_prefix:
                    continue
                counts[row["date"]] += int(row["count"])

    for date_str in sorted(counts.keys()):
        date = datetime.datetime.strptime(date_str, "%Y%m")

        if not (START_DATE <= date < END_DATE):
            continue

        days_in_month = calendar.monthrange(date.year, date.month)[1]
        for _ in range(days_in_month):
            print counts[date_str] / days_in_month

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("filenames", nargs="+")
    parser.add_argument("-m", "--match-icd9", dest="icd9_prefix", default="")
    args = parser.parse_args()

    main(**vars(args))
