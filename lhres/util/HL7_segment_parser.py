#!/usr/bin/env python
"""
Trivial parser to help with HL7 message debugging.
"""
import glob
from optparse import OptionParser
import sys
import os.path

usage = """%prog [options] segment sequence[,sequence]* file[s]ToParse

This will echo to stdout all the matches found for the given parameters.
Try `%prog --help` for additional information.

  segment          restricted to segments of this type, i.e. 'MSH' or 'PV1'
  sequence        parser splits each HL7 message on the '|' delimiter;
                   which sequence[s] to display, multiple sequences separated
                   by commas are supported, i.e. 6,12,44. NB, MSH counts
                   different from all other segments, as the field separator
                   '|' counts as sequence one.
  file[s]ToParse   one or more files to parse for matches; glob pattern
                   support included
"""

class Parser(object):
    
    def __init__(self):
        self.segments_of_interest = ""
        self.sequences = []
        self.filelist = []
        self.show_ADT = False
        self.show_file = False
        self.show_time = False
        self.show_visitID = False
        self.show_pc = False

    def processArgs(self, argv):
        """ Process any optional arguments and possitional parameters
        """
        parser = OptionParser(usage=usage)
        parser.add_option("-a", "--show_ADT", action="store_true", dest="show_ADT",
                          default=self.show_ADT, help="Display ADT value if set")
        parser.add_option("-f", "--show_file", action="store_true", dest="show_file",
                          default=self.show_file, help="Display matching filename if set")
        parser.add_option("-t", "--show_time", action="store_true", dest="show_time",
                          default=self.show_time, help="Display message time")
        parser.add_option("-v", "--show_visitID", action="store_true", dest="show_visitID",
                          default=self.show_visitID, help="Display visit ID")
        parser.add_option("-p", "--show_pc",
                          action="store_true",
                          dest="show_pc",
                          default=self.show_pc,
                          help="Display patient class")

        (options, pargs) = parser.parse_args()
        if len(pargs) < 3:
            parser.error("incorrect number of arguments")

        self.show_ADT = parser.values.show_ADT
        self.show_file = parser.values.show_file
        self.show_time = parser.values.show_time
        self.show_visitID = parser.values.show_visitID
        self.show_pc = parser.values.show_pc
        
        self.segments_of_interest = pargs.pop(0)
        if len(self.segments_of_interest) != 3:
            parser.error("segment '%s' looks incorrect, expected something like 'PV1'"
                         % self.segments_of_interest)

        try:
            nums = pargs.pop(0).split(",")
            for num in nums:
                if 'MSH' == self.segments_of_interest:
                    num = int(num) - 1
                self.sequences.append(int(num))
        except:
            parser.error("sequence must be an integer, separate multiple w/ comma and no spaces")

        for patternOrFile in pargs:
            for file in glob.glob(patternOrFile):
                if not os.path.isfile(file):
                    parser.error("can't open input file %s" % file)
                self.filelist.append(file)
    
        # Require at least one file
        if not len(self.filelist):
            parser.error("at least one input file is required")

    def parse(self):
        for filename in self.filelist:
            if self.show_file:
                print "READING FILE:",filename

            FILE = open(filename, "r")
            # by default, the files don't contain newlines.  read the whole
            # thing in and split on \r
            raw = FILE.read()

            # occasionally we have a newline type file from a direct
            # SQL query or the like - convert back
            if raw.find('\n') > 0:
                raw = raw.replace('\n','\r')
            if raw.find('\\r') > 0:
                raw = raw.replace('\\r','\r')

            for l in raw.split('\r'):
                # hang onto useful message header info and purge
                # potentials from the previous message
                if 'MSH' == l[0:3]:
                    sequences = l.split('|')
                    TIME = sequences[6]
                    ADT = sequences[8]
                    PATIENTCLASS, VISITID = '', ''

                # hang onto visit id if requested
                if self.show_visitID and 'PID' == l[0:3]:
                    sequences = l.split('|')
                    VISITID = sequences[18]

                # hang onto patient_class if requested
                if self.show_pc and 'PV1' == l[0:3]:
                    sequences = l.split('|')
                    PATIENTCLASS = sequences[2].split('^')[0]

                # print this out if it matches
                if self.segments_of_interest == l[0:3]:
                    sequences = l.split('|')
                    out = "|".join(
                        [sequences[e] for e in self.sequences if e < len(sequences)])
                    # strip newlines
                    out = out.replace("\n","")
                    if out:
                        if self.show_time:
                            out = ":".join([TIME,out])
                        if self.show_ADT:
                            out = ":".join([ADT,out])
                        if self.show_pc:
                            out = ":".join([PATIENTCLASS,out])
                        if self.show_visitID:
                            out = ":".join([VISITID,out])

                        print out

def main():
    parser = Parser()
    parser.processArgs(sys.argv[1:])
    parser.parse()

if __name__ == '__main__':
    main()
