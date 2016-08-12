#!/usr/bin/env python
'''
This is the driver module.
'''
import argparse
import pyparsing as pp
from parse import *
from verify import *
from generate import *
import os
import subprocess
import re

if __name__ == "__main__":
    '''
    1. Read in the file.
    '''
    argparser = argparse.ArgumentParser(description="Parse some command line arguments.")
    argparser.add_argument("input_file")
    args = argparser.parse_args()
    file_path = args.input_file

    with open(file_path, 'r') as f:
        file_content = f.read()

    '''
    2. Clean line comments.
    '''
    oneLineComment = pp.Literal("#") + pp.SkipTo(pp.lineEnd)
    comment_positions = []
    for result, start, end in oneLineComment.scanString(file_content):
        comment_positions.append((start, end)) # Record start and end positions of each comment line.

    for start, end in reversed(comment_positions):
        file_content = file_content[:start] + file_content[end:]

    # Now file_content has removed all comments and ready for parsing modules

    '''
    3. Parse syntax.
    '''
    print "Parsing syntax...",
    RML_file_parser = build_RML_parser()
    result = RML_file_parser.parseString(file_content)
    print " done"

    '''
    4. Verify semantically.
    '''
    print "Verifying syntax validity...",
    verify_result(result)
    print " done"

    '''
    5. Convert RML to generate ISPL file.
    '''
    print "Generating ISPL file for MCMAS..."
    ispl_result = generate_ispl(result)
    print " done"


    '''
    6. Output ispl_result
    '''
    print "Writing ISPL file to current directory...",
    input_file_name = os.path.basename(file_path)
    output_file_name = ""

    if input_file_name.split(".")[-1] == "rml": # input filename ends in .rml
        output_file_name = ".".join(input_file_name.split(".")[0:-1]) + ".ispl"
        output_file_name = "./ispl/" + output_file_name
    else: # input filename does not end in .rml

        output_file_name = "./ispl/" + input_file_name + ".ispl"

    with open(output_file_name, "w") as f:
        f.write(ispl_result)

    print " done"

    '''
    7. Call MCMAS to check the result
    '''
    mcmas_output = subprocess.check_output(["mcmas", output_file_name])
    true_pattern = re.compile(".*Formula number 1.*is TRUE in the model.*", re.S)
    false_pattern = re.compile(".*Formula number 1.*is FALSE in the model.*", re.S)

    if true_pattern.match(mcmas_output):
        print "MCMAS checking returned TRUE, the input game does have Nash Equilibrium."
    elif false_pattern.match(mcmas_output):
        print "MCMAS checking returned FALSE, the input game has no Nash Equilibrium."
    else:
        print "ERROR: fail to recognize MCMAS result:"
        print "\n".join(mcmas_output.split("\n")[9:])

