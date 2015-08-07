### NHDS Wrapper ###

What is it?
-----------

This is a tool to convert the fixed-width records of the
[National Hospital Discharge Survey](http://www.cdc.gov/nchs/nhds.htm)
into CSV files that can be more easily manipulated. This tool handles
all of these steps:

* Download the raw data from the NHDS FTP service
* Convert the fixed with records to CSV
* Generate a per-day infection rate similar to the output of the IMS
  data tools, described in more detail below.
* Create an sqlite database that maps the ICD9 codes to their
  descriptions

Example Usage
-------------

The entire tool is executed using `make`. To generate a CSV file for a
particular year, run:

```
$ make gen/as_csv/2009.csv
```

Similarly, to generate data that is similar to the IMS matrices, run:

```
$ make gen/match_ims/breast-cancer.txt
```

Implementation Notes
--------------------

The list of diseases is located in the [Makefile](Makefile) near the
top. This list is formatted as `ICD9_PREFIX:DISEASE_NAME`
(e.g. `174:breast-cancer`).

The format of the fixed-width records changes every year, so the
`nhds/parse_nhds.py` script has to keep track of which year every
field is included in the dataset. For example, in 2009, there were
only 7 diagnosis codes recorded, but 2010 introduced 8 more.

The format strings are in the following format:

```python
fmt = (
    (("09", "10"),
     2, ("Survey Year", "year_end")),
    (("09", "10"),
     1, _("Newborn status")),
    (("09", "10"),
     1, _("Units for age")),
# ...
)
```

Each tuple begins with a tuple of years that the field is valid for
(in this case, all of these fields are in the 2009 and 2010 datasets),
followed by the width of the field (So the second field is 1 character
long), and then a tuple of `(Given Name, Clean Name)`, which relates
to the name in the NHDS documentation, as well as a name which is
easier to parse and work with (typically in all lowercase, with spaces
replaced with underscores.

Similarly, the script keeps track of the target format to output. This
means that it can generate only fields present in the 2009 dataset,
even if it's reading a 2010 set. When no target is specified, it will
include all columns available in the output.

To change the target, the rule for `gen/as_csv/%.csv` must be changed.
