import struct
import csv
import sys
import collections
import datetime
import calendar

"""Parses and gives a unified access to all the different NHDS datasets

Each dataset consists of lines of fixed-length records, that are often
different from one year to the next. The data is retrieved from the
National Hospital Discharge Survey conducted by the CDC and documented
at:

    http://www.cdc.gov/nchs/nhds.htm

"""

fmt = (
    (("09", ),
     2, "Survey Year", "year_end"),
    (("09", ),
     1, "Newborn status"),
    (("09", ),
     1, "Units for age"),
    (("09", ),
     2, "Age"),
    (("09", ),
     1, "Sex"),
    (("09", ),
     1, "Race"),
    (("09", ),
     1, "Marital status"),
    (("09", ),
     2, "Discharge month", "month"),
    (("09", ),
     1, "Discharge status"),
    (("09", ),
     4, "Days of care"),
    (("09", ),
     1, "Length of stay flag"),
    (("09", ),
     1, "Geographic region", "region"),
    (("09", ),
     1, "Number of beds"),
    (("09", ),
     1, "Hospital ownership"),
    (("09", ),
     5, "Analysis weight", "weight"),
    (("09", ),
     2, "First 2 digits of survey year", "year_begin"),
    (("09", ),
     5, "Diagnosis code #1", "dx_cd"),
    (("09", ),
     5, "Diagnosis code #2"),
    (("09", ),
     5, "Diagnosis code #3"),
    (("09", ),
     5, "Diagnosis code #4"),
    (("09", ),
     5, "Diagnosis code #5"),
    (("09", ),
     5, "Diagnosis code #6"),
    (("09", ),
     5, "Diagnosis code #7"),
    (("09", ),
     4, "Procedure code #1"),
    (("09", ),
     4, "Procedure code #2"),
    (("09", ),
     4, "Procedure code #3"),
    (("09", ),
     4, "Procedure code #4"),
    (("09", ),
     2, "Primary expected source of payment"),
    (("09", ),
     2, "Secondary expected source of payment"),
    (("09", ),
     3, "Diagnosis-Related Groups"),
    (("09", ),
     1, "Type of admission"),
    (("09", ),
     2, "Source of admission"),
    (("09", ),
     5, "Admitting diagnosis"),
    (("09", ),
     2, "Newline")
)

class Entry:
    def __init__(self, line):
        year = line[:2]

        self.fmtstring = "".join(str(tup[1]) + "s"
                                 for tup in fmt
                                 if year in tup[0])
        self.fmtmapping = { name: i
                       for i, tup in enumerate(fmt)
                       for name in tup[2:]
                       if year in tup[0] }

        self.fields = struct.unpack(Entry.fmtstring, line)

    def __getitem__(self, key):
        return self.fields[self.fmtmapping[key]]

def main(filename, consolidate_date, map_regions, short_column_names):
    writer = csv.writer(sys.stdout)
    region_mapping = collections.defaultdict(lambda: "Missing", {
        "1": "Northeast",
        "2": "Midwest",
        "3": "South",
        "4": "West"
    })
    counts = collections.defaultdict(int)
    with open(input_filename, "r") as f:
        for line in f:
            entry.parse_line(line)

            if entry["dx_cd"][:len(search)] != search:
                continue

            number_of_discharges = int(entry["weight"].strip())
            region = entry["region"]
            date = entry["year_begin"] + entry["year_end"] + entry["month"]
            diagnosis_names = ["Diagnosis code #" + str(i) for i in range(1, 8)]
            diagnosis_codes = [entry[name] for name in diagnosis_names]

            if 0: writer.writerow([
                date,
                region_mapping[region],
                number_of_discharges
            ])

            counts[date] += number_of_discharges

    for date_str in sorted(counts.keys()):
        date = datetime.datetime.strptime(date_str, "%Y%m")

        if date.year != 2009 or date.month < 4:
            continue

        days_in_month = calendar.monthrange(date.year, date.month)[1]
        for _ in range(days_in_month):
            print counts[date_str] / float(days_in_month)

if __name__ == "__main__":
    import sys
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("filename")
    parser.add_argument("-d", "--consolidate-date", dest='consolidate_date',
                        action="store_true")
    parser.add_argument("-r", "--map-regions", dest='map_regions',
                        action="store_true")
    parser.add_argument("-s", "--short-column-names", dest='short_column_names',
                        action="store_true")

    main(filename=parser.filename,
         consolidate_date=parser.consolidate_date,
         map_regions=parser.map_regions,
         short_column_names=parser.short_column_names)
