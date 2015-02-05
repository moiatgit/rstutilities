#! /usr/bin/env python
# encoding: utf-8

# This script gets a rst filename and sets the metadata 'date' to
# current date. If there's a metadata next_entry, it sets it to
# current date minus a minute so it can appear after first entry in a
# standard Pelican set. The process continues recursively with the
# rest of the linked entries.
# 

import sys, argparse, os
import datetime
from rst_metadata import RstFile

class RstDatesFixer:
    """ This class fix the date of a rst file and the subsequent chain
    of files linked by :next_entry: metadata """

    _DATETIMEFORMAT ="%Y-%m-%d %H:%M:%S" 

    def __init__(self, startingdate, nochange):
        self.nextdate = startingdate
        self.nochange = nochange
        self.processed = [] # already processed files (to avoid circularity)

    def process(self, path):
        """ processes a rst file: 
        If the file is already processed, it just ignores it with a
        warning.
        Otherwise, it changes/adds the :date: metadata with the
        self.nextdate and recomputes next date.
        Once processed, the file is added to the processed list.
        In case path contains :next_entry: metadata, it processes the
        next entry recursively."""

        if path in self.processed:
            print >> sys.stderr, "Warning: file %s already processed (ignored)"%path
            return

        self.processed.append(path)

        rst = RstFile(path)
        if self.nochange:
            print "%s date would be set to %s"%(path, self._formatDate())
        else:
            rst.set_metadata_value("date", self._formatDate())
            rst.replace_metadata()
            print "procesed %s with date %s"%(path, self._formatDate())
        self._recompute_next_date()
        nextpath = rst.get_metadata_value("next_entry")
        if nextpath:
            self.process(nextpath)

    def _formatDate(self):
        """ returns the next date in the expected format"""
        return self.nextdate.strftime(RstDatesFixer._DATETIMEFORMAT)

    def _recompute_next_date(self):
        """ recomputes the next date """
        self.nextdate -= datetime.timedelta(minutes=1)

def checkDate(strdate):
    """ checks if strdate corresponds a well defined date:
    yyyy-mm-dd hh:mm:ss """
    print >> sys.stderr, "Error: this option is not implemented yet"
    sys.exit(1)
    pass

def is_rst_file(path):
    """ returns true if the path corresponds to an existing rst file """
    _, ext = os.path.splitext(path)
    if ext != ".rst":
        print >> sys.stderr, "Warning: .rst extension expected in %s (ignored)"%path
        return False
    #
    if not os.path.exists(path):
        print >> sys.stderr, "Warning: file not found: %s (ignored)"%path
        return False
    #
    return True

def filter_paths(paths):
    """ checks each path and returns the list of paths corresponding
    to existing rst files """
    return [p for p in paths if is_rst_file(p)]

def checkParams():
    """ checks that the arguments of the program call are as expected. 
    In case something's wrong, an error missage is issued and 
    finishes execution with an error code.
    When everything is ok, it returns the configuration information
    in a tuple: filelist, operation """

    p = argparse.ArgumentParser(description="Manages Pelican metadata information of ReStructuredText files", version="1.0")
    p.add_argument('paths', metavar='path', nargs='+', help="Source file path with .rst extension")
    p.add_argument("-d", "--date", action="store_true", help="Define starting date", dest="starting_date")
    p.add_argument("-n", "--no-changes", action="store_true",
                   help="Do no perform any changes. Just show the results", dest="nochange")
    #
    options = p.parse_args()
    #
    sourcelist = filter_paths(options.paths)
    if len(sourcelist) == 0:
        print >> sys.stderr, "Error: no files to act on"
        sys.exit(2)
    #
    if options.starting_date:
        startingDate = checkDate(options.starting_date)
    else:
        startingDate = datetime.datetime.now()

    return sourcelist, startingDate, options.nochange
#

def main():
    # get configuration information
    sourcelist, startingdate, nochange = checkParams()
    fixer = RstDatesFixer(startingdate, nochange)
    for entry in sourcelist:
        fixer.process(entry)

    return 0

#
if __name__=="__main__":
    sys.exit(main())




