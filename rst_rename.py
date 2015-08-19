#! /usr/bin/env python3
# encoding: utf8

# This script renames a file in argv[1] to argv[2] and replaces all the references
# in any .rst file.
# The file to be replaced and the .rst files should be in a subfolder of pwd (or pwd itself)

# TODO: a lot of cleanup
#       currently only shows changes without performing them
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
        return self._rename_references(testonly=True)

    def perform_changes(self):
        """ As print_changes() but performing the changes """
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
        #print ("XXX _rename_references_in_file(%s)"%rstfile)
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
        #if regexp.pattern.startswith("^"): print ("XXX\t _rename_references_in_line('%s') newlink %s"%(line.rstrip(), dstlink))
        refs = myfindall(regexp, line)
        changed = False
        for srcref in refs:
            src = srcref.rstrip(os.linesep)  # remove newline
            #if regexp.pattern.startswith("^"): print ("XXX\t\t 1) srcref: '%s'"%(src))
            #if regexp.pattern.startswith("^"): print ("XXX\t\t 2) srcref: '%s'"%(src))
            src = add_extension_if_missing(src)
            #if regexp.pattern.startswith("^"): print ("XXX\t\t 3) srcref: '%s'"%(src))
            src = normalizebasepath(self.basepath, rstpath, src)
            if not os.path.isfile(src):
                continue
            if not os.path.samefile(src, self.srcpath):
                continue
            #if regexp.pattern.startswith("^"): print ("XXX\t new link: '%s'"%dstlink)
            newline = re.sub(srcref, dstlink, line)
            line = newline
            changed = True
            #if regexp.pattern.startswith("^"): print ("XXX\t _rename_references_in_line() --> '%s'"%line.rstrip())
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

def remove_quotes(ref):
    #return ref.strip("`")   # remove `
    return ref

def remove_tags(ref):
    #return ref.rstrip(">").lstrip("<").strip("`") # remove <>
    return ref

def remove_indent(ref):
    return ref.lstrip()

def add_quotes(ref):
    #return "`%s`"%ref
    return ref

def add_tags(ref):
    #return "<%s>"%ref
    return ref


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
       # resultlist.append(seq[result.start():result.end()])
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

# def relativepath(basepath, path):
#     """ returns the path without the basepath when it starts with it.
#         E.g. basepath="/one/two" and path="/one/two/tree/four.rst" ==> "/tree/four.rst"
#         E.g. basepath="/one/two" and path="/one/two/four.rst" ==> "/four.rst"
#         E.g. basepath="/one/two" and path="/one/three/two/four.rst" ==> "/one/three/two/four.rst" 
#     """
#     if path[:len(basepath)]==basepath:
#         return path[len(basepath):]
#     else:
#         return path

#def has_regular_references(basepath, rstfile, searchedfile):
#    """ returns true if rstfile contains regular references to searchedfile
#        TODO: you can optimize it if breaking on the first hit
#    """
#    rstbasepath = os.path.dirname(rstfile)
#    filerefs = []
#    with open(rstfile) as f:
#        for l in f.readlines():
#            refs = [ s.strip("`") for s in myfindall(_regexp_quoted, l)]
#            refs += [ s.rstrip('>').lstrip('<') for s in myfindall(_regexp_tagged, l) ]
#            if refs:
#                refs = [ (normalizepath(basepath, f) if os.path.isabs(f) else normalizepath(rstbasepath, f)) 
#                         for f in refs 
#                        ]
#                refs = [ add_extension_if_missing(f) for f in refs ]
#                refs = [ f for f in refs if os.path.isfile(f) ]
#                filerefs += [ f for f in refs if os.path.samefile(f, searchedfile) ]
#    return len(filerefs) > 0
#

# def rename_quoted_references_in_line(basepath, rstbasepath, line, searchedfile, renamedfile):
#     """ Replaces quoted references to searchedfile in line by renamedfile
#         Quotes are of the form "`rstfilewithoutextension`" and "`anyfile`"
#         It returns a tuple:
#             - the resulting line (without any change if there where no references.
#             - True if returned line has changed
#     """
#     refs = myfindall(_regexp_quoted, line)
#     changed = False
#     for srcref in refs:
#         src = remove_quotes(srcref)
#         src = add_extension_if_missing(src)
#         src = normalizebasepath(basepath, rstbasepath, src)
#         if not os.path.isfile(src):
#             continue
#         if not os.path.samefile(src, searchedfile):
#             continue
#         newline = re.sub(srcref, add_quotes(renamedfile), line)
#         line = newline
#         changed = True
#     return line, changed
# 
# def rename_tagged_references_in_line(basepath, rstbasepath, line, searchedfile, renamedfile):
#     """ Replaces tagged references to searchedfile in line by renamedfile
#         Quotes are of the form "<rstfilewithoutextension>" and "<anyfile>"
#         It returns a tuple:
#             - the resulting line (without any change if there where no references.
#             - True if returned line has changed
#     """
#     refs = myfindall(_regexp_tagged, line)
#     changed = False
#     for srcref in refs:
#         src = remove_tags(srcref)
#         src = add_extension_if_missing(src)
#         src = normalizebasepath(basepath, rstbasepath, src)
#         if not os.path.isfile(src):
#             continue
#         if not os.path.samefile(src, searchedfile):
#             continue
#         newline = re.sub(srcref, add_tags(renamedfile), line)
#         line = newline
#         changed = True
#     return line, changed
# 
# 
# def rename_quoted_references_in_file(basepath, rstfile, searchedfile, renamedfile, testonly=True):
#     """ """
#     rstbasepath = os.path.dirname(rstfile)
#     renamed = relativepath(basepath, remove_rst_extension_if_present(renamedfile))
#     if os.path.dirname(renamed) == relativepath(basepath, rstbasepath):
#         renamed = os.path.basename(renamed)
#     with open(rstfile) as f:
#         lines = f.readlines()
#     anychange = False
#     for i in range(len(lines)):
#         line = lines[i]
#         newline, changed = rename_quoted_references_in_line(basepath, rstbasepath, line, searchedfile, renamed)
#         if changed:
#             print ("\t%s: '%s' --> '%s'"%(relativepath(basepath, rstfile), line.rstrip(), newline.rstrip()))
#             anychange = True
# 
#     if anychange and not testonly:
#         with open(rstfile, "w") as f:
#             f.writelines(lines)
# 
# def rename_tagged_references_in_file(basepath, rstfile, searchedfile, renamedfile, testonly=True):
#     """ """
#     rstbasepath = os.path.dirname(rstfile)
#     renamed = relativepath(basepath, remove_rst_extension_if_present(renamedfile))
#     if os.path.dirname(renamed) == relativepath(basepath, rstbasepath):
#         renamed = os.path.basename(renamed)
#     with open(rstfile) as f:
#         lines = f.readlines()
#     anychange = False
#     for i in range(len(lines)):
#         line = lines[i]
#         newline, changed = rename_tagged_references_in_line(basepath, rstbasepath, line, searchedfile, renamed)
#         if changed:
#             print ("\t%s: '%s' --> '%s'"%(relativepath(basepath, rstfile), line.rstrip(), newline.rstrip()))
#             anychange = True
# 
#     if anychange and not testonly:
#         with open(rstfile, "w") as f:
#             f.writelines(lines)
# 
# def rename_toc_references_in_file(basepath, rstfile, searchedfile, renamedfile, testonly=True):
#     """ rewrites rstfile contents and changes references to searchedfile to renamedfile """
#     rstbasepath = os.path.dirname(rstfile)
#     renamed = relativepath(basepath, remove_rst_extension_if_present(renamedfile))
#     if os.path.dirname(renamed) == relativepath(basepath, rstbasepath):
#         renamed = os.path.basename(renamed)
#     lines = []
#     with open(rstfile) as f:
#         lines = f.readlines()
#     if not lines:
#         return
#     anychanges = False
#     for i in range(len(lines)):
#         line = lines[i]
#         m = _regexp_toc.match(line)
#         if m:
#             srcref = m.group(1).strip()
#             src = add_extension_if_missing(srcref)
#             if os.path.isabs(src):
#                 ref = normalizepath(basepath, src)
#             else:
#                 ref = normalizepath(rstbasepath, src)
#             if os.path.isfile(ref):
#                 if os.path.samefile(ref, searchedfile):
#                     newline = re.sub(srcref, renamed, line)
#                     lines[i] = newline
#                     anychanges = True
#                     print ("\t%s: '%s' --> '%s'"%(relativepath(basepath, rstfile), line.rstrip(), newline.rstrip()))
#     if anychanges and not testonly:
#         with open(rstfile, "w") as f:
#             f.writelines(lines)
# 
# 
# 
# def rename_quoted_references(basepath, rstfile, searchedfile, renamedfile):
#     """ rewrites rstfile contents and changes references to searchedfile to renamedfile """
#     rstbasepath = os.path.dirname(rstfile)
#     lines = []
#     with open(rstfile) as f:
#         lines = f.readlines()
#     if not lines:
#         return
#     anychanges = False
#     for i in range(len(lines)):
#         searchpos = -1
#         while True:
#             l = lines[i]
#             searchpos+=1
# 
#             m = _regexp_quoted.search(l, searchpos)
#             if m: 
#                 srcref = m.group(1)
#                 src = srcref.strip("`").strip() # remove `
#                 src = add_extension_if_missing(src)
#                 if os.path.isabs(src):
#                     ref = normalizepath(basepath, src)
#                 else:
#                     ref = normalizepath(rstbasepath, src)
#                     if os.path.isfile(ref):
#                         if os.path.samefile(ref, searchedfile):
#                             renaming="`%s`"%renamedfile
#                             lines[i] = re.sub(srcref, renaming, l)
# #                             print("XXX \t\toldline:'%s'"%l.strip())
# #                             print("XXX \t\tnewline:'%s'"%lines[i].strip())
#                             anychanges = True
#             else:
#                 break
#     if anychanges:
# #         print ("XXX QUO !!!! changing file %s with quoted regularrefs (not done!)"%rstfile)
#         #with open(rstfile, "w") as f:
#         #    f.writelines(lines)
# 
# def rename_tagged_references(basepath, rstfile, searchedfile, renamedfile):
#     """ rewrites rstfile contents and changes references to searchedfile to renamedfile """
#     rstbasepath = os.path.dirname(rstfile)
#     lines = []
#     with open(rstfile) as f:
#         lines = f.readlines()
#     if not lines:
#         return
#     anychanges = False
#     for i in range(len(lines)):
#         searchpos = -1
#         while True:
#             l = lines[i]
#             searchpos+=1
# 
#             m = _regexp_tagged.search(l, searchpos)
#             if m: 
#                 srcref = m.group(1)
#                 src = srcref.rstrip(">").lstrip("<").strip("`").strip() # remove <>
#                 src = add_extension_if_missing(src)
# #                 #print("XXX\t\t once extended %s"%src)
#                 if os.path.isabs(src):
#                     ref = normalizepath(basepath, src)
#                 else:
#                     ref = normalizepath(rstbasepath, src)
#                 if os.path.isfile(ref):
#                     if os.path.samefile(ref, searchedfile):
#                         renaming="<%s>"%renamedfile
#                         lines[i] = re.sub(srcref, renaming, l)
# #                         print("XXX \t\toldline:'%s'"%l.strip())
# #                         print("XXX \t\tnewline:'%s'"%lines[i].strip())
#                         anychanges = True
#             else:
#                 break
#     if anychanges:
# #         print ("XXX TAG !!!! changing file %s with tagged regularrefs (not done!)"%rstfile)
#         #with open(rstfile, "w") as f:
#         #    f.writelines(lines)


def main():

    basepath = os.getcwd()
#     #print("XXX basepath=%s"%basepath)

    # check arguments declared
    if len(sys.argv) != 3:
        print("Usage: %s «sourcefilename» «destfilename»"%sys.argv[0])
        sys.exit(1)

    srcfilename=normalizepath(basepath, sys.argv[1])
    dstfilename=normalizepath(basepath, sys.argv[2])

    # check srcfilename does exists and is in the pwd path
#     #print("XXX not done: check srcfilename does exists and is in the pwd path")
    # check dstfilename doesn't exist
#     #print("XXX not done: check dstfilename doesn't exist")

    renamer = Renamer(srcfilename, dstfilename)
    changes = renamer.print_changes()
    if changes:
        renamer.perform_changes()
    else:
        print ("No changes required")

    #  # all rst files in the path
    #  rstfiles = []
    #  for root, subfolders, files in os.walk(os.getcwd()):
    #      rstfiles+=[ os.path.join(root, f) for f in files if f[-4:] == ".rst" ]

#     #  #print ("XXX rst files %s"%rstfiles)
    #  # keep only files containing srcfilename
    #  for rst in rstfiles:

    #      rename_quoted_references_in_file(basepath, rst, srcfilename, dstfilename)
    #      rename_tagged_references_in_file(basepath, rst, srcfilename, dstfilename)
    #      rename_toc_references_in_file(basepath, rst, srcfilename, dstfilename)
    #      # Show files with toc references to srcfilename
    #      # if has_toc_references(basepath, rst, srcfilename):
#     #      #     #print ("XXX file %s contains toc references to %s"%(relativepath(basepath, rst), relativepath(basepath, srcfilename)))
    #      #     rename_toc_references(basepath, rst, srcfilename, relativepath(basepath, dstfilename))

    #      # if has_regular_references(basepath, rst, srcfilename):
#     #      #     print ("XXX file %s contains regular references to %s"%(relativepath(basepath, rst), relativepath(basepath, srcfilename)))
    #      #     rename_quoted_references(basepath, rst, srcfilename, relativepath(basepath, dstfilename))
    #      #     rename_tagged_references(basepath, rst, srcfilename, relativepath(basepath, dstfilename))


    #      # 
    #      #show_file_references(srcfilename, f)


    #  # ask for confirmation

    #  # perform replacement on all the .rst files

    #  # perform mv on actual file

#

if __name__ == "__main__":
    main()






# 
# # check if there're the two required args
# if [ "$#" -ne 2 ];
# then
#     echo "Usage: $0 «path to filename» «destination filename»"
#     exit 1
# fi
# 
# ext="${1##*.}"
# 
# # check if the file has a proper extension
# if [[ $ext == $1 ]];
# then
#     echo "WARNING: sorry, this version just works for files with extension"
#     exit 1
# fi
# 
# # check if destination file has path information
# if [ $(basename "$2") != "$2" ];
# then
#     echo "ERROR: destination filename should not contain any path $2"
#     exit 1
# fi
# 
# # check if file do exits
# if [ ! -e "$1" ];
# then
#     echo "ERROR: file not found $1"
#     exit 2
# fi
# 
# # compose destination file extension if not already present
# if [[ ${2##*.} != "$ext" ]];
# then
#     destfilename="$2.$ext"
# else
#     destfilename="$2"
# fi
# 
# # compose destination path
# filefolder=$(dirname $1)
# destfilepath="$filefolder/$destfilename"
# 
# # check if destination file already exists
# if [ -e "$destfilepath" ];
# then
#     echo "ERROR: destination file already exits ($destfilepath). Remove it and rerun $0"
#     exit 3
# fi
# 
# # check whether there're files affected by the renaming
# filename=$(basename "$1")
# 
# # require confirmation
# echo "The following will be performed:"
# echo "  $ mv $1 $destfilename"
# 
# # check if there are references to the original filename
# if [[ "" != $(find . -name '*.rst' -exec egrep -H "\<$filename\>" {} \;) ]];
# then
#     echo "  The following references to $filename will be replaced by $destfilename"
#     find . -name '*.rst' -exec egrep -H "\<$filename\>" {} \;
#     references_found=0
# else
#     references_found=1
# fi
# 
# read -p "Press c to perform changes, any other key to refrain: " resp
# if [[ $resp != "c" ]];
# then
#     echo "No changes performed. Ease yourself."
#     exit 0
# fi
# 
# # perform changes
# if [ $references_found -eq 0 ];
# then
#     find . -name '*.rst' -exec sed -i "s/\<$filename\>/$destfilename/g" {} \;
# fi
# mv $1 $destfilepath
# 
# echo "Done"

#def make_filter_contains_reference(basepath, srcfilename):
#    """ returns a function able to decide if a file contains references to srcfilename """
#
#    def tmp_show_references_to_files(line):
#        expr1="^\s+(\S+)\s*$"
# #        print("XXX tmp_show_references_to_files '%s' on '%s'"%(expr1, line))
#        m=re.match(expr1, line)
#        if m:
# #            print ("XXX \t found %s"%m.group(1))
#
#    def line_contains_rstreference(line):
#        """ returns true if line contains reference to srcfile (rst) """
#
# #        print ("XXX checking on line '%s'"%line)
#
#        # check file appearing in a toc list
#        expr1='^\s+%s(%s)?\s*$'%os.path.splitext(srcfilename)
#        if re.match(expr1, line):
#            return True
#
#        # check file appearing between ``
#        expr2='.*`%s(%s)?`'%os.path.splitext(srcfilename)
#        if re.match(expr2, line):
#            return True
#
#        return False
#
#    def line_contains_nonrstreference(line):
#        """ returns true if line contains reference to srcfile (non rst) """
#        contains = False
#        expr1='^\s+%s\s*$'%srcfilename
#        if re.match(expr1, line):
#            contains = True
#        return contains
#
#    def file_contains_rstreference(rstfile):
#        """ returns true if rstfile contains srcfilename (rst) """
# #        print("XXX checking %s contains %s"%(rstfile, srcfilename))
# #        print("XXX \t relative path %s"%rstfile[len(basepath):])
#        relativepath = os.path.dirname(rstfile[len(basepath):])
# #        print("XXX \r relative path only %s"%relativepath)
#        with open(rstfile) as rst:
#            lines = rst.readlines()
#            contains = False
#            for line in lines:
#                tmp_show_references_to_files(line)
#                if line_contains_rstreference(line):
#                    contains = True
#                    break
#        return contains
#
#    def file_contains_nonrstreference(rstfile):
#        """ returns true if rstfile contains srcfilename (non rst) """
# #        print("XXX checking %s contains %s"%(rstfile, srcfilename))
#        with open(rstfile) as rst:
#            lines = rst.readlines()
#            contains = False
#            for line in lines:
#                if line_contains_nonrstreference(line):
#                    contains = True
#                    break
#        return contains
#
#    if srcfilename[-4:] == ".rst":
#        return file_contains_rstreference
#    else:
#        return file_contains_nonrstreference

