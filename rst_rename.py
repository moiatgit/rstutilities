#! /usr/bin/env python3

"""
    This script renames rst files including references

    It is git aware in the sense that, if the file to be renamed is in a git repo,
    it is renamed using git to ease control identification.

    Limitations:

    - Current version does not work recursively. If there's a .rst in a subfolder referencing the src file,
      this script will fail to detect it.

      One of the implications: while it allows referencing with '/' (e.g. .. literalinclude:: /object.java),
      since it only considers .rst files at base_folder, it is always exactly
      the same as without (e.g. .. literalinclude:: object.java)

    - Current version does not allow working git unaware. If the base folder is
      in a git repository, it will rename using git mv instead of os.mv

    - Current version does not deal with special splittings that seem to be valid in Sphinx. For example,
        .. image::
            object.png
            :align: center

      The exemple works in my current version of Sphinx but it is not supported by this script.
"""


import sys, os, re
import argparse
import pathlib
import subprocess

import rstutils

# Scape sequences for colorize the output
_HIGHLIGHT_ESCAPE = "\033[31;2m"    # colorize from this (red, bold)
_STANDARD_SCAPE = "\033[0m"         # reset to normal color


def main():
    options = parse_commandline_args()
    check_options(options)
    changes = seek_references(options['src'], options['dst'], options['base_folder'])
    if changes:
        show_changes(changes, options['base_folder'])
        confirmed = ask_for_confirmation(options['force'])
        if confirmed:
            perform_changes(changes)
            rename_src(options['src'], options['dst'])
        else:
            print("No changes performed")
    else:
        print("No references found. Only the file %s will be renamed" % options['src'].relative_to(options['base_folder']))
        confirmed = ask_for_confirmation(options['force'])
        if confirmed:
            rename_src(options['src'], options['dst'])

def seek_references(src, dst, base_folder):
    """ composes the changes to be performed on the rst files 
        The result is a list of dicts with the following keys:
        - linenr; the line number of the change
        - src: the original contents of the line
        - dst: the contents of the line once the replacements on it have took place
        - repr: the representation of the changes with scape characters to highlight the changes
    """
    changes = dict()    # { file: list_of_changes }
    for rst in rstutils.get_rst_in_folder(base_folder):
        changes_in_file = rstutils.seek_references_in_file(rst, src, base_folder)
        if changes_in_file:
            with open(rst) as f:
                lines = f.readlines()
            changes[rst] = expand_changes_on_contents(lines, changes_in_file,
                                                      str(src.relative_to(base_folder)),
                                                      str(dst.relative_to(base_folder)))
    return changes

def show_changes(changes, base_folder):
    """ Given a list of changes, it shows them on stdout with paths relative to base_folder """
    for path, expanded_changes in changes.items():
        print(path.relative_to(base_folder))
        for expanded_change in expanded_changes:
            print("[%d];\t%s" % (expanded_change['linenr'], expanded_change['src'].strip('\n')))
            print("\t%s" % (expanded_change['repr'].strip('\n')))
            print()

def perform_changes(changes):
    """ Given a list of changes it performs them on the corresponding files """
    for path, expanded_changes in changes.items():
        with open(path) as f:
            lines = f.readlines()
        for change in expanded_changes:
            lines[change['linenr']] = change['dst']
        with open(path, "w") as f:
            f.write("".join(lines))
    print("Renamed references")



def rename_src(src, dst):
    """ performs the renaming depending on whether src is or not in a git repository
        It assumes src and dst belong to the same git repository """
    if is_file_in_git(src.parent):
        git_mv(src, dst)
        print("File renamed with git")
    else:
        src.rename(dst)
        print("File renamed")


####################################################################################################
# Arguments processing
####################################################################################################

def parse_commandline_args():
    """ defines the arguments and returns a dict containing the options with
        the following normalization:
        * 'force': will always appear with the corresponding value
        * 'src', 'dst' and 'base_folder': are converted to pathlib.Path
        * 'base_folder' is set to src parent if not explicitly set by user
    """
    parser = argparse.ArgumentParser(
        description="Script that helps you to rename files and their references in rst folders")
    parser.add_argument("-f", "--force",
                        action="store_true",
                        help="execute changes without asking",
                        required=False)
    parser.add_argument("src", help="source file name (must exist)")
    parser.add_argument("dst", help="destination file name (must not exist)")
    parser.add_argument("-b", "--base-dir",
                        required=False,
                        help="Base directory for the rst project",
                        dest='base_folder',
                        type=str,
                        )

    args = parser.parse_args()
    normalized_args = { k:v for k,v in vars(args).items() if v }
    normalized_args.setdefault('force', False)
    for tag in ('src', 'dst'):
        normalized_args[tag] = pathlib.Path(normalized_args[tag]).resolve()
    normalized_args['base_folder'] = (pathlib.Path(normalized_args['base_folder']).resolve()
                                      if 'base_folder' in normalized_args
                                      else normalized_args['src'].parent)

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
    if (options['base_folder'] not in options['src'].parents or
        options['base_folder'] not in options['dst'].parents):
        print("ERROR: base folder must contain both source and destination")
        sys.exit(1)


####################################################################################################
# renaming suport
####################################################################################################

def create_representation(linesrc, linedst, src, dst):
    """ given the source and the renamed line, and the source and destination names of the file,
        it composes and returns a new line highlighting the changes """

    src, dst = clean_commonalities(src, dst)
    linesrclist = list(linesrc)
    linedstlist = list(linedst)
    linereprlist = list()
    srcpos = 0
    dstpos = 0
    while srcpos < len(linesrc):
        if linesrclist[srcpos] == linedstlist[dstpos]:
            linereprlist.append(linesrclist[srcpos])
            srcpos += 1
            dstpos += 1
            continue
        linereprlist.append(_HIGHLIGHT_ESCAPE)
        linereprlist.append(dst)
        linereprlist.append(_STANDARD_SCAPE)
        srcpos += len(src)
        dstpos += len(dst)
    return "".join(linereprlist)


def expand_changes_on_contents(rstcontents, changes, src, dst):
    """
        Given
        - rstcontents: a list of lines of a valid rst file
        - changes: a list of pairs (line, char) representing the points where a replacement must take place
        - src: a pathlib.Path relative to the base_folder with the reference to the file to replace
        - dst: a pathlib.Path relative to the base_folder with the reference to the destination file
        it expads composes a list of expanded changes consisting on a dict with the following keys:
        - linenr; the line number of the change
        - src: the original contents of the line
        - dst: the contents of the line once the replacements on it have took place
        - repr: the representation of the changes with scape characters to highlight the changes
    """
    def replace_change(line, pos, src, dst):
        """ given the contents of a line, replaces the occurrence in position pos of src by dst.
            In case src's extension is .rst and it appears without extension at line, the replacement is without
            extension too """
        if src.endswith('.rst'):    # it can appear without extension
            src = src[:-4]
            dst = dst[:-4]
        return line[:pos] + dst + line[pos + len(src):]


    expanded_changes = list()
    changed_lines = dict()
    for linenr, pos in changes:
        if linenr in changed_lines:
            expanded_change = changed_lines[linenr]
            expanded_change['dst'] = replace_change(expanded_change['dst'], pos, src, dst)
        else:
            expanded_change = dict()
            expanded_change['linenr'] = linenr
            expanded_change['src'] = rstcontents[linenr]
            expanded_change['dst'] = replace_change(expanded_change['src'], pos, src, dst)
            changed_lines[linenr] = expanded_change

    for expanded_change in changed_lines.values():
        expanded_change['repr'] = create_representation(expanded_change['src'], expanded_change['dst'], src, dst)
        expanded_changes.append(expanded_change)

    return expanded_changes

####################################################################################################
# Other helping functions
####################################################################################################

def clean_commonalities(text1, text2):
    """ given two strings, it creates two new strings such that 
        - are substrings of the originals
        - the longest common prefix in the originals do not appear in the results
        - the longest common suffix in the originals do not appear in the results

        >>> clean_commonalities('commonpreffix1difference1', 'commonpreffix2difference2')
        ('1difference1', '2difference2')
        >>> clean_commonalities('1difference1commonsuffix','2difference2commonsuffix')
        ('1difference1', '2difference2')
        >>> clean_commonalities('commonpreffix1difference1commonsuffix','commonpreffix2difference2commonsuffix')
        ('1difference1', '2difference2')
        >>> clean_commonalities('commonall','commonall')
        ('', '')
        >>> clean_commonalities('','')
        ('', '')
        >>> clean_commonalities('equal','different')
        ('equal', 'different')
    """
    if not text1 or not text2:
        return text1, text2
    preffix = True
    pos_ini = 0
    while pos_ini < min(len(text1), len(text2)) and text1[pos_ini] == text2[pos_ini]:
        pos_ini += 1

    pos_fin1 = len(text1)
    pos_fin2 = len(text2)
    while pos_ini < pos_fin1 and pos_ini < pos_fin2 and text1[pos_fin1-1] == text2[pos_fin2-1]:
        pos_fin1 -= 1
        pos_fin2 -= 1

    return text1[pos_ini:pos_fin1], text2[pos_ini:pos_fin2]


def ask_for_confirmation(force):
    """ it asks for confirmation of the changes from stdin and returns the answer
        if force, it returns directly True without asking """
    if force:
        return True
    response = input("Type exactly %syes%s if you want to perform these changes. Anything otherwise: " % (_HIGHLIGHT_ESCAPE, _STANDARD_SCAPE))
    return response == 'yes'

def run_easy(cmd, folder=None, timeout=None):
    """ runs a command and returns the standard output and the standard error.
        In case a folder is specified, the command is executed in the defined
        folder and, once done, it returns to the original folder
    """
    prev_cwd = pathlib.Path.cwd()
    folder = folder if folder else prev_cwd
    os.chdir(folder)
    cmd = f'timeout {timeout} {cmd}' if timeout else cmd
    cmd = 'env LANG=C.UTF-8 ' + cmd   # run it in english to unify output messages
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    stdout, stderr = process.communicate()
    os.chdir(prev_cwd)
    try:
        out = stdout.decode('utf8')
        err = stderr.decode('utf8')
    except UnicodeDecodeError as e:
        logging.warning("run_easy(cmd:%s): it wasn't possible to decode as UTF8 on command output"%cmd)
        out = stdout.decode("utf8", "replace")
        err = stderr.decode("utf8", "replace")
    finally:
        if process.returncode != 0:
            if process.returncode == 124:
                err += 'Process stopped by timeout'
            else:
                err += f'\nProcess finished with return code {process.returncode}'
        process.stdout.close()
        process.stderr.close()
    return out, err


def is_file_in_git(path):
    """ returns True when path has a commit in a git repository """
    cmd = f'git log {path}'
    out_msg, err_msg = run_easy(cmd, path)
    return 'fatal:' not in err_msg and out_msg

def git_mv(src, dst):
    """ renames src to dst """
    folder = src.parent
    cmd = f'git mv "{src}" "{dst}"'
    out_msg, err_msg = run_easy(cmd, folder)
    print(cmd)
    if out_msg: print("\t", out_msg)
    if err_msg: print("\t ", err_msg)


####################################################################################################

if __name__ == "__main__":
    main()



