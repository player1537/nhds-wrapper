import struct
import csv
import sys
import collections

"""Parses and gives a unified access to all the different NHDS datasets

Each dataset consists of lines of fixed-length records, that are often
different from one year to the next. The data is retrieved from the
National Hospital Discharge Survey conducted by the CDC and documented
at:

    http://www.cdc.gov/nchs/nhds.htm

"""

class Entry:
    fmt = ((1,  2, "Survey Year", "year_end"),
           (3,  1, "Newborn status"),
           (4,  1, "Units for age"),
           (5,  2, "Age"),
           (7,  1, "Sex"),
           (8,  1, "Race"),
           (9,  1, "Marital status"),
           (10, 2, "Discharge month", "month"),
           (12, 1, "Discharge status"),
           (13, 4, "Days of care"),
           (17, 1, "Length of stay flag"),
           (18, 1, "Geographic region", "region"),
           (19, 1, "Number of beds"),
           (20, 1, "Hospital ownership"),
           (21, 5, "Analysis weight", "weight"),
           (26, 2, "First 2 digits of survey year", "year_begin"),
           (28, 5, "Diagnosis code #1", "dx_cd"),
           (33, 5, "Diagnosis code #2"),
           (38, 5, "Diagnosis code #3"),
           (43, 5, "Diagnosis code #4"),
           (48, 5, "Diagnosis code #5"),
           (53, 5, "Diagnosis code #6"),
           (58, 5, "Diagnosis code #7"),
           (63, 4, "Procedure code #1"),
           (67, 4, "Procedure code #2"),
           (71, 4, "Procedure code #3"),
           (75, 4, "Procedure code #4"),
           (79, 2, "Primary expected source of payment"),
           (81, 2, "Secondary expected source of payment"),
           (83, 3, "Diagnosis-Related Groups"),
           (86, 1, "Type of admission"),
           (87, 2, "Source of admission"),
           (89, 5, "Admitting diagnosis"),
           (94, 2, "Newline"))

    fmtstring = "".join(str(tup[1]) + "s" for tup in fmt)
    fmtmapping = { name: i
                   for i, tup in enumerate(fmt)
                   for name in tup[2:] }

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

            writer.writerow([
                date,
                region_mapping[region],
                number_of_discharges
            ] + diagnosis_codes)

if __name__ == "__main__":
    import sys
    if len(sys.argv) == 2:
        main(sys.argv[1])
    elif len(sys.argv) == 3:
        main(sys.argv[1], sys.argv[2])
    else:
        raise Exception("Need argument")
