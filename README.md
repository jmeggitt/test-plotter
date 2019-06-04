## Template Format
Templates are used for parsing input to the data collector. They follow the following formatting conventions.
 - `<field_name>`: A data field that you want to collect. This should be put where it appears in the data and will never include a newline once parsed.
 - `..`: Skip one or more words on a single line. Do not place directly before or after a field.
 - `...`: Skip one or more lines.
### Example 
##### Template
```
CPU(s): <cpu_num>
On-line CPU(s) list: <online_min>-<online_max>
...
CPU MHz: <speed>
CPU max MHz: <max_speed>
BogoMIPS: <mips>
```
##### Data
```
Architecture:        x86_64
CPU(s):              4
On-line CPU(s) list: 0-3
Stepping:            9
CPU MHz:             2901.000
CPU max MHz:         2901.0000
BogoMIPS:            5802.00
Virtualization:      VT-x
```
## Data collector
```bash
usage: data_collect.py [-h] [-c] [-i] template_file [input_file]

A script for collecting and plotting data.

positional arguments:
  template_file        Template to use for parsing input
  input_file           Input to parse

optional arguments:
  -h, --help           show this help message and exit
  -c, --csv            Output the collected data on stdout as a csv file
  -i, --ident-headers  Disable the identifier headers should be output
```

