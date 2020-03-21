#! /usr/bin/env python3

"""
    This script renames rst files including references

    It is git aware in the sense that, if the file to be renamed is in a git repo,
    it is renamed using git to ease control identification.
"""

# XXX TODO: allow specifying a recursive option to check within the subfolders of src
# XXX TODO: add a non-git option to allow avoiding to be git aware

import sys, os, re
import argparse
import pathlib



##class Renamer:
##
##    # Regular expressions
##    _regexp_list = [re.compile("^\s+(.+)\s*$"),
##                    re.compile("`(.*?)`"),
##                    re.compile("<(.*?)>"),
##                    re.compile("^\s*\.\. literalinclude:: (.*)$"),
##                    re.compile("^\s*\.\. figure:: (.*)$") ]
##
##    def __init__(self, srcpath, dstpath):
##        """ srcpath does exists, dstpath doesn't """
##        assert os.path.isfile(srcpath)
##        assert not os.path.isfile(dstpath)
##        self.basepath = os.getcwd()
##        self.srcpath = srcpath
##        self.dstpath = dstpath
##        self.rstfiles = self._get_rst_files()
##
##    def print_changes(self):
##        """ It prints changes to be performed to stdout. It does not change any file contents.
##            It returns whether there are files with changes.
##        """
##        print ("$ mv %s %s"%(self._get_relative_path(self.srcpath),
##                           self._get_relative_path(self.dstpath)))
##        return self._rename_references(testonly=True)
##
##    def perform_changes(self):
##        """ Performs the renaming on the files and the renaming of src to dst """
##        changes = self._rename_references(testonly=False)
##        os.rename(self.srcpath, self.dstpath)
##        return changes
##
##    def _rename_references(self, testonly=True):
##        """ for each file in self.rstfiles it shows the changes to be performed and, if not
##        testonly, it performs them on the files.
##        It returns True if there are files to change.
##        """
##        fileswithchanges = False
##        for rst in self.rstfiles:
##            fileswithchanges = self._rename_references_in_file(rst, testonly) or fileswithchanges
##        return fileswithchanges
##
##    def _rename_references_in_file(self, rstfile, testonly):
##        """ It shows the changes to be performed on file rst and, if not testonly, it performs
##        them on the file. 
##        It returns True if there are changes in this file.
##        """
##        dstlink = self._get_link_of_renamed_file_for_rst(rstfile)
##        lines = get_lines_in_file(rstfile)
##        rstpath = os.path.dirname(rstfile)
##        filechanged = False
##        for i, line in enumerate(lines):
##            for regexp in Renamer._regexp_list:
##                line, changed = self._rename_references_in_line(line, regexp, rstpath, dstlink)
##                if changed:
##                    if testonly:
##                        self._print_change(rstfile, lines[i], line)
##                    lines[i] = line
##                    filechanged = True
##
##        if filechanged and not testonly:
##           save_lines_in_file(rstfile, lines)
##
##        return filechanged
##
##    def _print_change(self, rstfile, oldline, newline):
##        """ Prints the change to the standard output """
##        print ("%s: '%s' --> '%s'"%(self._get_relative_path(rstfile), oldline.rstrip(), newline.rstrip()))
##
##
##    def _rename_references_in_line(self, line, regexp, rstpath, dstlink):
##        """ Replaces references to self.srcpath in line by a proper link to self.dstpath.
##            References match regexp pattern.
##            Finally it returns the resulting line, and whether it has been changed
##        """
##        refs = myfindall(regexp, line)
##        changed = False
##        for srcref in refs:
##            src = srcref.rstrip(os.linesep)  # remove newline
##            src = normalizebasepath(self.basepath, rstpath, src)
##            if not os.path.isfile(src):
##                src = add_extension_if_missing(src)
##                if not os.path.isfile(src):
##                    continue
##            if not os.path.samefile(src, self.srcpath):
##                continue
##            line = re.sub(srcref, dstlink, line)
##            changed = True
##        return line, changed
##
##    def _get_link_of_renamed_file_for_rst(self, rst):
##        """ Given an rstfile, it returns the link that would reference the dstfile """
##        if same_path(rst, self.dstpath):
##            link = os.path.basename(self.dstpath)
##        else:
##            link = self._get_relative_path(self.dstpath)
##        link = remove_rst_extension_if_present(link)
##        return link
##
##    def _get_relative_path(self, path):
##        """ returns the path without the basepath when it starts with it.
##            E.g. basepath="/one/two" and path="/one/two/tree/four.rst" ==> "/tree/four.rst"
##            E.g. basepath="/one/two" and path="/one/two/four.rst" ==> "/four.rst"
##        """
##        if path.startswith(self.basepath):
##            return path[len(self.basepath):]
##        else:
##            return path
##
##    def _get_rst_files(self):
##        """ returns the list of rst files contained in cwd """
##        rstfiles = []
##        for root, _, files in os.walk(self.basepath):
##            rstfiles+=[ os.path.join(root, f) for f in files if is_rst_file(f) ]
##        return rstfiles
##
### Utility functions
##
##def is_rst_file(path):
##    """ True if path is an .rst file """
##    return path[-4:] == ".rst"
##
##def same_path(f1, f2):
##    """ True if both files have the same path """
##    return os.path.dirname(f1) == os.path.dirname(f2)
##
##def get_lines_in_file(path):
##    """ returns the lines contained in file """
##    with open(path) as f:
##        lines = f.readlines()
##    return lines
##
##def save_lines_in_file(path, lines):
##    with open(path, "w") as f:
##        f.writelines(lines)
##
##
##def normalizepath(basepath, path):
##    """ returns the path prefixed with basepath (even if path is absolute) """
##    if (os.path.isabs(path)):
##        newpath = os.path.join(basepath, path[1:]) # sorry MSWindows :(
##    else:
##        newpath = os.path.join(basepath, path)
##    return os.path.normpath(newpath)
##
##def myfindall(regex, seq):
##    resultlist=[]
##    pos=0
##    while True:
##       result = regex.search(seq, pos)
##       if result is None:
##          break
##       resultlist.append(result.group(1))
##       pos = result.start()+1
##    return resultlist
##
##def add_extension_if_missing(filename):
##    """ returns the same filename with .rst extension if missing """
##    return filename if filename[-4:].lower() == '.rst' else filename + ".rst"
##
##def remove_rst_extension_if_present(filename):
##    """ """
##    return filename[:-4] if filename[-4:].lower() == '.rst' else filename
##
##def has_toc_references(basepath, rstfile, searchedfile):
##    """ returns True if rstfile contains actual toc references to searchedfile """
##    rstbasepath = os.path.dirname(rstfile)
##    with open(rstfile) as f:
##        for l in f.readlines():
##            m = _regexp_toc.match(l)
##            if m:
##                srcref = m.group(1).strip()
##                src = add_extension_if_missing(srcref)
##                if os.path.isabs(src):
##                    ref = normalizepath(basepath, src)
##                else:
##                    ref = normalizepath(rstbasepath, src)
##                if os.path.isfile(ref) and os.path.samefile(ref, searchedfile):
##                    return True
##    return False
##
##
##def normalizebasepath(basepath, rstbasepath, ref):
##    """ """
##    return normalizepath(basepath, ref) if os.path.isabs(ref) else normalizepath(rstbasepath, ref)
##
##def ask_confirmation():
##    """ asks for confirmation to the user and returns True if she actually confirms """
##    response = input("Please, confirm changes? (C: confirm, anything else: no changes): ")
##    return response.lower() in ["c", "confirm"]
##
##def oldmain():
##
##    basepath = os.getcwd()
##
##    # check arguments declared
##    if len(sys.argv) != 3:
##        print("Usage: %s «sourcefilename» «destfilename»"%sys.argv[0])
##        sys.exit(1)
##
##    srcfilename=normalizepath(basepath, sys.argv[1])
##    dstfilename=normalizepath(basepath, sys.argv[2])
##
##    if not os.path.isfile(srcfilename):
##        print("File '%s' must exist"%srcfilename)
##        sys.exit(1)
##
##    if os.path.isfile(dstfilename):
##        print("File '%s' must NOT exist"%dstfilename)
##        sys.exit(1)
##
##    renamer = Renamer(srcfilename, dstfilename)
##    changes = renamer.print_changes()
##    if changes:
##        if ask_confirmation():
##            renamer.perform_changes()
##            print("Changes performed")
##        else:
##            print("No changes performed")
##    else:
##        print ("No changes required")
#

####################################################################################################

def check_rst_references(rstcontents, src, dst):
    """ Given:
            rstcontents: str with the contents of a rst file
            src: a pathlib relative to the rst file with the old name
            dst: a pathlib relative to the rst file with the new name
        it returns a dict with the following keys
            result: a boolean indicating if there are changes (True) or not. This key will always be present.
            changes: a list of dict describing the changes in the file
                     a change is described with a dict:
                     line: the number of the line where the change has been produced
                     src: the original contents of the line
                     dst: the proposed change of the line

        A reference to rst can appear in the following ways:
        - if src is a .rst itself, the reference could appear with and without the .rst extension
        - the reference path are always relative to the rst. 
          - when the reference starts with /, it means from the parent of the rst
          - otherwise it also means the same, so / at the beginning is superfluous
        - references can be:
          - on a toctree (with or without .rst extension)
          - after a :ref: (including the <> variant) (without .rst extension)
          - after a :doc: (including the <> variant) (without .rst extension)
          - after a literalinclude::
          - after a figure::
          - after a image::
          - after a :download: (including the <> variant)
    """

    def look_for_images(rstcontents, src, dst):
        """ this method is specialized in references to images/figures
        """
        _regex_image = r"^(\s*\.\. (image|figure)::\ */?)(%s)$" % src
        changes = list()
        for nr, line in enumerate(rstcontents):
            m = re.match(_regex_image, line)
            if not m:
                continue
            change = dict()
            change['line'] = nr
            change['src'] = line
            change['dst'] = re.sub(_regex_image, r'\1%s' % dst, line)
            changes.append(change)

        return changes

    result = dict()
    changes = list()    # list of changes
    changes += look_for_images(rstcontents, src, dst)
    result['result'] = len(changes) > 0
    result['changes'] = changes
    return result


def perform_renaming(src, dst, folders, force):
    """ performs the renaming of src to dst considering the folders as containers 
        of reStructuredText files that could make reference to src, and
        considering boolean force option to decide whether ask or not for confirmation """
    def get_potential_rst(folders):
        """ given a list of pathlib folders, it 
            generates the pathlib.Path of all the rst files in these folders """
        for folder in folders:
            for file in folder.glob("*.rst"):
                yield file.resolve()

    def quick_filter(rst, src):
        """ returns True if rst contains the name of the src file (no extension) """
        return src.stem in rst.read_text()

    for rst in get_potential_rst(folders):
        if not quick_filter(rst, src):
            continue
        with open(rst) as f:
            lines = f.readlines()
        checking_result = check_rst_references(lines, 
                                               src.relative_to(rst.parent),
                                               dst.relative_to(rst.parent))
        print("XXX checking_result", checking_result)

def parse_commandline_args():
    """ defines the arguments and returns a dict containing the options with
        the following normalization:
        * 'force': will always appear with the corresponding value
        * 'src', 'dst': are converted to pathlib.Path
    """
    parser = argparse.ArgumentParser(
        description="Script that helps you to rename files and their references in rst folders")
    parser.add_argument("-f", "--force",
                        action="store_true",
                        help="execute changes without asking",
                        required=False)
    parser.add_argument("src", help="source file name (must exist)")
    parser.add_argument("dst", help="destination file name (must not exist)")
    parser.add_argument("-d", "--source-directories",
                        help="additional folders to check for rst files",
                        dest='folders',
                        type=str,
                        nargs='*',
                        )

    args = parser.parse_args()
    normalized_args = { k:v for k,v in vars(args).items() if v }
    normalized_args.setdefault('force', False)
    for tag in ('src', 'dst'):
        normalized_args[tag] = pathlib.Path(normalized_args[tag]).resolve()

    normalized_args.setdefault('folders', list())
    normalized_args['folders'].append(str(normalized_args['src'].parent))   # add src's directory
    normalized_args['folders'] = list(set(normalized_args['folders']))      # remove dups
    normalized_args['folders'] = [pathlib.Path(f) for f in normalized_args['folders']]
    return normalized_args

def check_options(options):
    """ checks the existence of source and destination files.
        In case source doesn't exist, or destination does exist
        it breaks execution
    """
    if not options['src'].is_file():
        print("ERROR: source file must exist")
        sys.exit(1)
    if options['dst'].is_file():
        print("ERROR: destination file must not exist")
        sys.exit(1)
    resulting_folders = list()
    # XXX folders should be in the path of src and dst
    for folder in options['folders']:
        if not folder.is_dir():
            print("WARNING: ignoring non existing folder %s" % folder)
            continue
        resulting_folders.append(folder)
    options['folders'] = resulting_folders

def main():
    options = parse_commandline_args()
    check_options(options)
    perform_renaming(**options)

if __name__ == "__main__":
    main()
