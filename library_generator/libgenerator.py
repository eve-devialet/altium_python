#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to generate an Altium lib with repetitive components.
First, export altium SCHLIB as PCAD V16 (.lia file)
Create Jinja template file with said SCHLIB and put it in template folder.
Template has to be UTF-8 encoded.

For the moment this script only generates a E96 resistor value library.

@author: Eve Redero
"""
import os
import jinja2 as jj2
import codecs
import numpy as np

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

output_dir = SCRIPT_DIR

# Configure template engine
template_env = jj2.Environment(
        extensions=['jinja2.ext.loopcontrols'],
        loader=jj2.FileSystemLoader(os.path.join(SCRIPT_DIR, 'templates'),
            followlinks=True))
template_env.globals['target'] = 'libc'

# Jinja magic
templates = os.listdir(os.path.join(SCRIPT_DIR, 'templates'))
templates = [os.path.splitext(f)[0] for f in templates if os.path.splitext(f)[1] == '.in']
templates = [f for f in templates if f != 'macros.c']

def human_format_resistors(num):
    '''
    Float formating function to return a pretty "1k" / "1R" resistor-like
    number format
    '''
    num = float('{:.3g}'.format(num))
    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0
    return '{}{}'.format('{:f}'.format(num).rstrip('0').rstrip('.'), ['R', 'k', 'M', 'B', 'T'][magnitude])

def render_template(template_name, replacement_dict):
    '''
    Renders a template "template_name" using the replacement dictionnary
    "replacement_dict"
    '''
    # Render files from templates
    if template_name in templates:
        with open(template_name, 'w+') as fd:
            template = template_env.get_template(template_name + '.in')
            fd.write(template.render(replacement_dict))

    # Change text file formating from UTF-8, \n line ending to ISO-8859-1, \r\n
    # line ending. Would make Altium loop infinitely otherwise.
    with open(os.path.join(output_dir, template_name), 'r') as outfile:
        copytext = outfile.read()

    copytext = copytext.replace(os.linesep, '\r\n')
    with codecs.open(os.path.join(output_dir, template_name), 'w', "ISO-8859-1") as myfile:
        myfile.write(copytext)

def create_resistor_lib(template_name="resistors.lia"):
    # Resistor generation parameters, starting from a knows series
    e96_series = np.array([1, 1.02, 1.05, 1.07, 1.10, 1.13, 1.15, 1.18, 1.21, 1.24, 1.27, 1.30, 1.33, 1.37, 1.40, 1.43, 1.47, 1.50, 1.54, 1.58, 1.62, 1.65, 1.69, 1.74, 1.78, 1.82, 1.87, 1.91, 1.96, 2.00, 2.05, 2.10, 2.15, 2.21, 2.26, 2.32, 2.37, 2.43, 2.49, 2.55, 2.61, 2.67, 2.74, 2.80, 2.87, 2.94, 3.01, 3.09, 3.16, 3.24, 3.32, 3.40, 3.48, 3.57, 3.65, 3.74, 3.83, 3.92, 4.02, 4.12, 4.22, 4.32, 4.42, 4.53, 4.64, 4.75, 4.87, 4.99, 5.11, 5.23, 5.36, 5.49, 5.62, 5.76, 5.90, 6.04, 6.19, 6.34, 6.49, 6.65, 6.81, 6.98, 7.15, 7.32, 7.50, 7.68, 7.87, 8.06, 8.25, 8.45, 8.66, 8.87, 9.09, 9.31, 9.53, 9.76],
                          dtype=float)

    n_octaves = 6
    footprint_series = ["0201", "0402", "0603", "0805"]
    e96_all = np.concatenate([e96_series * 10**i for i in range(n_octaves)])

    e96_formatted = [human_format_resistors(num) for num in e96_all]

    replacement_dict = {"resistor_values" : e96_formatted,
                        "resistor_packages" : footprint_series}
    render_template(template_name, replacement_dict)

def import_capa_csv(filename):
    '''
    Imports a CSV from supplier database
    CSV has to contain following columns : MPN, Designation, Family, DVLT_CAT
    CSV has to be sorted by MPN column for doublon check to work
    Returns a list of lists: serial number and package
    '''
    import csv
    import re
    content = list()
    with open(filename, 'r') as myfile:
        csvfile = csv.reader(myfile)
        for num, line in enumerate(csvfile):
            if num==0:
                header=line
                try:
                    pn_col=header.index('MPN')
                    desi_col=header.index('Designation')
                    fam_col=header.index('Family')
                    supplier_col=header.index('Supplier')
                except:
                    raise IOError("Invalid CSV file, please check formats" +\
                                  "and columns")
            else:
                # Check if product is a capacitor
                if (line[fam_col] == "Passives - Ceramic capacitors"
                        and line[supplier_col] == "_Generic_"):
                    # Check for doublons (only if CSV is sorted)
                    if len(content) == 0 or line[pn_col] != content[-1][0]:
                        content.append([line[pn_col], line[desi_col]])
    # Capa name parser
    cap_parser = re.compile("([0-9\.]+.)F (\d+)V (\d+)\% (\d+) (\S+)")
    capalist = list()

    for capa in content:
        cap_data = cap_parser.findall(capa[0])
        if len(cap_data) == 0:
            continue
        cap_data = cap_data[0]
        cap_dict = {"value": "{}F {}V {}% {} {}".format(cap_data[0].lower(),
                         cap_data[1], cap_data[2], cap_data[3], cap_data[4]),
                    "package": cap_data[3]}
        capalist.append(cap_dict)
    return(capalist)

def create_capacitor_lib(csv_filename="capa_list.csv",
                         template_name="capacitors.lia"):
    '''
    Imports CSV and render template
    '''
    replacement_dict = {"capas": import_capa_csv(csv_filename)}
    render_template(template_name, replacement_dict)


if __name__ == "__main__":
    create_resistor_lib()
    create_capacitor_lib()