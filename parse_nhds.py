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

class Entry:
    fmt = ((2, "Survey Year", "year_end"),
           (1, "Newborn status"),
           (1, "Units for age"),
           (2, "Age"),
           (1, "Sex"),
           (1, "Race"),
           (1, "Marital status"),
           (2, "Discharge month", "month"),
           (1, "Discharge status"),
           (4, "Days of care"),
           (1, "Length of stay flag"),
           (1, "Geographic region", "region"),
           (1, "Number of beds"),
           (1, "Hospital ownership"),
           (5, "Analysis weight", "weight"),
           (2, "First 2 digits of survey year", "year_begin"),
           (5, "Diagnosis code #1", "dx_cd"),
           (5, "Diagnosis code #2"),
           (5, "Diagnosis code #3"),
           (5, "Diagnosis code #4"),
           (5, "Diagnosis code #5"),
           (5, "Diagnosis code #6"),
           (5, "Diagnosis code #7"),
           (4, "Procedure code #1"),
           (4, "Procedure code #2"),
           (4, "Procedure code #3"),
           (4, "Procedure code #4"),
           (2, "Primary expected source of payment"),
           (2, "Secondary expected source of payment"),
           (3, "Diagnosis-Related Groups"),
           (1, "Type of admission"),
           (2, "Source of admission"),
           (5, "Admitting diagnosis"),
           (2, "Newline"))

    fmtstring = "".join(str(tup[0]) + "s" for tup in fmt)
    fmtmapping = { name: i
                   for i, tup in enumerate(fmt)
                   for name in tup[1:] }

    def parse_line(self, line):
        self.fields = struct.unpack(Entry.fmtstring, line)

    def __getitem__(self, key):
        return self.fields[Entry.fmtmapping[key]]

def main(input_filename, search="174"):
    entry = Entry()
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
    if len(sys.argv) == 2:
        main(sys.argv[1])
    elif len(sys.argv) == 3:
        main(sys.argv[1], sys.argv[2])
    else:
        raise Exception("Need argument")
