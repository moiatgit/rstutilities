#! /usr/bin/env python3
# encoding: utf8

# This script renames a file in argv[1] to argv[2] and replaces all the references
# in any .rst file.
# The file to be replaced and the .rst files should be in a subfolder of pwd (or pwd itself)

# TODO: some cleanup
#       add for literalincludes: references after ::
#
import sys, os, re

class Renamer:

    # Regular expressions
    _regexp_toc    = re.compile("^\s+(.+)\s*$")
    _regexp_quoted = re.compile("`(.*?)`")
    _regexp_tagged = re.compile("<(.*?)>")

    def __init__(self, srcpath, dstpath):
        """ srcpath does exists, dstpath doesn't """
        assert os.path.isfile(srcpath)
        assert not os.path.isfile(dstpath)
        self.basepath = os.getcwd()
        self.srcpath = srcpath
        self.dstpath = dstpath
        self.rstfiles = self._get_rst_files()

    def print_changes(self):
        """ It prints changes to be performed to stdout. It does not change any file contents.
            It returns whether there are files with changes.
        """
        print ("$ mv %s %s"%(self._get_relative_path(self.srcpath),
                           self._get_relative_path(self.dstpath)))
        return self._rename_references(testonly=True)

    def perform_changes(self):
        """ Performs the renaming on the files and the renaming of src to dst """
        changes = self._rename_references(testonly=False)
        os.rename(self.srcpath, self.dstpath)
        return changes

    def _rename_references(self, testonly=True):
        """ for each file in self.rstfiles it shows the changes to be performed and, if not
        testonly, it performs them on the files.
        It returns True if there are files to change.
        """
        fileswithchanges = False
        for rst in self.rstfiles:
            fileswithchanges = self._rename_references_in_file(rst, testonly) or fileswithchanges
        return fileswithchanges

    def _rename_references_in_file(self, rstfile, testonly):
        """ It shows the changes to be performed on file rst and, if not testonly, it performs
        them on the file. 
        It returns True if there are changes in this file.
        """
        dstlink = self._get_link_of_renamed_file_for_rst(rstfile)
        lines = get_lines_in_file(rstfile)
        rstpath = os.path.dirname(rstfile)
        filechanged = False
        for i, line in enumerate(lines):
            line, quochanged = self._rename_references_in_line(line, Renamer._regexp_quoted,
                                                               rstpath, dstlink)
            line, tagchanged = self._rename_references_in_line(line, Renamer._regexp_tagged,
                                                               rstpath, dstlink)
            line, tocchanged = self._rename_references_in_line(line, Renamer._regexp_toc,
                                                               rstpath, dstlink)
            if (quochanged or tagchanged or tocchanged):
                if testonly:
                    self._print_change(rstfile, lines[i], line)
                lines[i] = line
                filechanged = True

        if filechanged and not testonly:
           save_lines_in_file(rstfile, lines)

        return filechanged

    def _print_change(self, rstfile, oldline, newline):
        """ Prints the change to the standard output """
        print ("%s: '%s' --> '%s'"%(self._get_relative_path(rstfile), oldline.rstrip(), newline.rstrip()))


    def _rename_references_in_line(self, line, regexp, rstpath, dstlink):
        """ Replaces references to self.srcpath in line by a proper link to self.dstpath.
            References match regexp pattern.
            Finally it returns the resulting line, and whether it has been changed
        """
        refs = myfindall(regexp, line)
        changed = False
        for srcref in refs:
            src = srcref.rstrip(os.linesep)  # remove newline
            src = add_extension_if_missing(src)
            src = normalizebasepath(self.basepath, rstpath, src)
            if not os.path.isfile(src):
                continue
            if not os.path.samefile(src, self.srcpath):
                continue
            newline = re.sub(srcref, dstlink, line)
            line = newline
            changed = True
        return line, changed

    def _get_link_of_renamed_file_for_rst(self, rst):
        """ Given an rstfile, it returns the link that would reference the dstfile """
        if same_path(rst, self.dstpath):
            link = os.path.basename(self.dstpath)
        else:
            link = self._get_relative_path(self.dstpath)
        link = remove_rst_extension_if_present(link)
        return link

    def _get_relative_path(self, path):
        """ returns the path without the basepath when it starts with it.
            E.g. basepath="/one/two" and path="/one/two/tree/four.rst" ==> "/tree/four.rst"
            E.g. basepath="/one/two" and path="/one/two/four.rst" ==> "/four.rst"
        """
        if path.startswith(self.basepath):
            return path[len(self.basepath):]
        else:
            return path

    def _get_rst_files(self):
        """ returns the list of rst files contained in cwd """
        rstfiles = []
        for root, _, files in os.walk(self.basepath):
            rstfiles+=[ os.path.join(root, f) for f in files if is_rst_file(f) ]
        return rstfiles

# Utility functions

def is_rst_file(path):
    """ True if path is an .rst file """
    return path[-4:] == ".rst"

def same_path(f1, f2):
    """ True if both files have the same path """
    return os.path.dirname(f1) == os.path.dirname(f2)

def get_lines_in_file(path):
    """ returns the lines contained in file """
    with open(path) as f:
        lines = f.readlines()
    return lines

def save_lines_in_file(path, lines):
    with open(path, "w") as f:
        f.writelines(lines)


def normalizepath(basepath, path):
    """ returns the path prefixed with basepath (even if path is absolute) """
    if (os.path.isabs(path)):
        newpath = os.path.join(basepath, path[1:]) # sorry MSWindows :(
    else:
        newpath = os.path.join(basepath, path)
    return os.path.normpath(newpath)

def myfindall(regex, seq):
    resultlist=[]
    pos=0
    while True:
       result = regex.search(seq, pos)
       if result is None:
          break
       resultlist.append(result.group(1))
       pos = result.start()+1
    return resultlist

def add_extension_if_missing(filename):
    """ returns the same filename with .rst extension if missing """
    return filename if filename[-4:].lower() == '.rst' else filename + ".rst"

def remove_rst_extension_if_present(filename):
    """ """
    return filename[:-4] if filename[-4:].lower() == '.rst' else filename

def has_toc_references(basepath, rstfile, searchedfile):
    """ returns True if rstfile contains actual toc references to searchedfile """
    rstbasepath = os.path.dirname(rstfile)
    with open(rstfile) as f:
        for l in f.readlines():
            m = _regexp_toc.match(l)
            if m:
                srcref = m.group(1).strip()
                src = add_extension_if_missing(srcref)
                if os.path.isabs(src):
                    ref = normalizepath(basepath, src)
                else:
                    ref = normalizepath(rstbasepath, src)
                if os.path.isfile(ref) and os.path.samefile(ref, searchedfile):
                    return True
    return False


def normalizebasepath(basepath, rstbasepath, ref):
    """ """
    return normalizepath(basepath, ref) if os.path.isabs(ref) else normalizepath(rstbasepath, ref)

def ask_confirmation():
    """ asks for confirmation to the user and returns True if she actually confirms """
    response = input("Please, confirm changes? (C: confirm, anything else: no changes): ")
    return response.lower() in ["c", "confirm"]

def main():

    basepath = os.getcwd()

    # check arguments declared
    if len(sys.argv) != 3:
        print("Usage: %s «sourcefilename» «destfilename»"%sys.argv[0])
        sys.exit(1)

    srcfilename=normalizepath(basepath, sys.argv[1])
    dstfilename=normalizepath(basepath, sys.argv[2])

    if not os.path.isfile(srcfilename):
        print("File '%s' must exist"%srcfilename)
        sys.exit(1)

    if os.path.isfile(dstfilename):
        print("File '%s' must NOT exist"%dstfilename)
        sys.exit(1)

    renamer = Renamer(srcfilename, dstfilename)
    changes = renamer.print_changes()
    if changes:
        if ask_confirmation():
            renamer.perform_changes()
            print("Changes performed")
        else:
            print("No changes performed")
    else:
        print ("No changes required")
#

if __name__ == "__main__":
    main()
