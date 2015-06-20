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

def _(name):
    return (name, name.lower().replace(' ', '_'))

fmt = (
    (("09", "10"),
     2, ("Survey Year", "year_end")),
    (("09", "10"),
     1, _("Newborn status")),
    (("09", "10"),
     1, _("Units for age")),
    (("09", "10"),
     2, _("Age")),
    (("09", "10"),
     1, _("Sex")),
    (("09", "10"),
     1, _("Race")),
    (("09", "10"),
     1, _("Marital status")),
    (("09", "10"),
     2, ("Discharge month", "month")),
    (("09", "10"),
     1, _("Discharge status")),
    (("09", "10"),
     4, _("Days of care")),
    (("09", "10"),
     1, _("Length of stay flag")),
    (("09", "10"),
     1, ("Geographic region", "region")),
    (("09", "10"),
     1, _("Number of beds")),
    (("09", "10"),
     1, _("Hospital ownership")),
    (("09", "10"),
     5, ("Analysis weight", "weight")),
    (("09", "10"),
     2, ("First 2 digits of survey year", "year_begin")),
    (("09", "10"),
     5, _("Diagnosis code #1")),
    (("09", "10"),
     5, _("Diagnosis code #2")),
    (("09", "10"),
     5, _("Diagnosis code #3")),
    (("09", "10"),
     5, _("Diagnosis code #4")),
    (("09", "10"),
     5, _("Diagnosis code #5")),
    (("09", "10"),
     5, _("Diagnosis code #6")),
    (("09", "10"),
     5, _("Diagnosis code #7")),
    (("10", ),
     5, _("Diagnosis code #8")),
    (("10", ),
     5, _("Diagnosis code #9")),
    (("10", ),
     5, _("Diagnosis code #10")),
    (("10", ),
     5, _("Diagnosis code #11")),
    (("10", ),
     5, _("Diagnosis code #12")),
    (("10", ),
     5, _("Diagnosis code #13")),
    (("10", ),
     5, _("Diagnosis code #14")),
    (("10", ),
     5, _("Diagnosis code #15")),
    (("09", "10"),
     4, _("Procedure code #1")),
    (("09", "10"),
     4, _("Procedure code #2")),
    (("09", "10"),
     4, _("Procedure code #3")),
    (("09", "10"),
     4, _("Procedure code #4")),
    (("10", ),
     4, _("Procedure code #5")),
    (("10", ),
     4, _("Procedure code #6")),
    (("10", ),
     4, _("Procedure code #7")),
    (("10", ),
     4, _("Procedure code #8")),
    (("09", "10"),
     2, _("Primary expected source of payment")),
    (("09", "10"),
     2, _("Secondary expected source of payment")),
    (("09", "10"),
     3, _("Diagnosis-Related Groups")),
    (("09", "10"),
     1, _("Type of admission")),
    (("09", "10"),
     2, _("Source of admission")),
    (("09", "10"),
     5, _("Admitting diagnosis")),
)

region_mapping = collections.defaultdict(lambda: "Missing", {
    "1": "Northeast",
    "2": "Midwest",
    "3": "South",
    "4": "West"
})


class Entry:
    def __init__(self, line, target=None):
        self._year = line[:2]

        if target is None:
            target = self._year
        self._target = target

        self._fmt = [spec
                     for spec, (years, _, _) in zip(fmt, fmt)
                     if self._year in years]

        self._fmtstring = "".join(str(length) + "s"
                                  for (years, length, _) in self._fmt)

        self._fmtmapping = { name: i
                            for i, (years, _, names) in enumerate(self._fmt)
                            for name in names }

        self._fields = struct.unpack(self._fmtstring, line.strip("\r\n"))

    def __getitem__(self, key):
        return self._fields[self._fmtmapping[key]]

    def columns(self, short_column_names=False, target=None):
        if target is None:
            target = self._year

        names = [names[1] if short_column_names else names[0]
                 for (years, _, names) in self._fmt
                 if target in years]

        return names

    def fields(self, strip_fields=False, target=None):
        if target is None:
            target = self._year

        return [self[name].strip() if strip_fields else self[name]
                for (years, _, (name, _)) in self._fmt
                if target in years]

def main(filename, consolidate_date=False, map_regions=False,
         short_column_names=False, strip_fields=False, estimate_count=False,
         target=None):
    writer = csv.writer(sys.stdout)
    with open(filename, "r") as f:
        for i, line in enumerate(f):
            entry = Entry(line)
            if i == 0:
                columns = entry.columns(short_column_names, target)

                if consolidate_date:
                    columns += ["date"]
                if map_regions:
                    columns += ["region_name"]
                if estimate_count:
                    columns += ["count"]

                writer.writerow(columns)

            fields = entry.fields(strip_fields, target)
            if consolidate_date:
                date = entry["year_begin"] + entry["year_end"] + entry["month"]
                fields += [date]
            if map_regions:
                region_name = region_mapping[entry["region"]]
                fields += [region_name]
            if estimate_count:
                number_of_discharges = int(entry["weight"].strip())
                fields += [number_of_discharges]

            writer.writerow(fields)

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
    parser.add_argument("-S", "--strip-fields", dest="strip_fields",
                        action="store_true")
    parser.add_argument("-e", "--estimate-count", dest="estimate_count",
                        action="store_true")
    parser.add_argument("-t", "--target", dest="target",
                        default=None)
    args = parser.parse_args()

    main(**vars(args))
