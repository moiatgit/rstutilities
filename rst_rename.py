#! /usr/bin/env python3

"""
    This script renames rst files including references

    It is git aware in the sense that, if the file to be renamed is in a git repo,
    it is renamed using git to ease control identification.
"""

# XXX TODO: absolute references (/) are relative to the source directory. Relative references are relative to the rst file
# XXX TODO: allow specifying a recursive option to check within the subfolders of src
# XXX TODO: add a non-git option to allow avoiding to be git aware

import sys, os, re
import argparse
import pathlib

if __name__ == "__main__":
    main()


def main():
    options = parse_commandline_args()
    check_options(options)
    perform_renaming(**options)


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


####################################################################################################
# Arguments processing
####################################################################################################

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


####################################################################################################
# renaming suport
####################################################################################################


def check_line_for_tag(tag, line, src, dst):
    """ checks the tag in the line
        it returns:
        - state: the new state from this check
                 - 'new tag' when the line is finished
                 - 'caption only' when the last tag is splitted and targe has to be found in a next line
        - has_changed: True if line has a change
        - new_line: contents of the line after change
    """
    new_state = 'new tag'
    print(f"XXX\t\t check_line_for_tag({line}) enters")
    has_changed = False
    pos = 0
    while True:
        print(f"XXX\t\t\t in the loop state {new_state} has_changed {has_changed} pos {pos} line |{line}|")
        new_state, has_change_partial, line, pos = check_partial_line_for_tag(tag, line, pos, src, dst)
        has_changed = has_changed or has_change_partial
        if new_state == 'caption only':
            break
        if pos < 1 or pos >= len(line):
            break
    return new_state, has_changed, line

def check_line_for_caption(line, src, dst):
    """ checks for <src> in line

        IMPORTANT: '<' cannot appear within the caption text

        It returns:
        - state: the new state: 'caption only' if no reference found or 'new tag' if refernce has been found
        - has_changed: True if the reference has been found
        - new_line: the contents of the line after the change
        - pos in line after processing the reference
    """
    print(f"\tXXX checking for caption only |{line}|")
    new_line = line
    has_changed = False
    new_state = 'caption only'
    pos_end_caption = len(line)     # in case it is not found
    pos_init_caption = line.find('<') 
    if pos_init_caption >= 0:
        new_state = 'new tag'
        pos_end_caption = line.find('>', pos_init_caption)
        assert pos_init_caption < pos_end_caption, "malformed rst on line %s" % line
        reference_contents = line[pos_init_caption +1:pos_end_caption]
        print(f"\t\tline has a potential reference between {pos_init_caption} and {pos_end_caption}: |{reference_contents}|")
        if reference_contents == src:
            new_line = line[:pos_init_caption + 1] + dst + line[pos_end_caption:]
            has_changed = True
    print(f"XXX\t\t returning from caption only new_state {new_state} has_changed {has_changed} line |{new_line}|")
    return new_state, has_changed, new_line, pos_end_caption + 1

def check_partial_line_for_tag(tag, line, pos, src, dst):
    """ given a line and a pos to start checking, it looks for tag from pos in the line.
        It returns:
        - state: the new state from this check
        - has_changed: True if line has a change
        - new_line: contents of the line after change
        - new_pos: pos in the line after checking last tag
    """
    print(f"XXX\t\t\t check_partial_line_for_tag(line |{line}| pos {pos}")
    has_changed = False
    new_line = line
    new_state = 'new tag'
    pos_tag = line.find(tag, pos)
    if pos_tag >= pos:
        print(f"XXX\t\t\t tag found at pos {pos_tag}")
        pos_open_tag = line.find('`', pos_tag)
        pos_close_tag = line.find('`', pos_open_tag + 1)
        if pos_close_tag < 0:   # splitted tag
            print(f"XXX\t\t\t close tag not found ")
            new_state = 'caption only'
            new_pos = len(line)
        else:
            new_pos = pos_close_tag + 1
            tag_content = line[pos_open_tag+1: pos_close_tag]
            print(f"XXX\t\t\t close tag found at {pos_close_tag} with contents |{tag_content}|")
            if tag_content == src:  # tag`target`
                new_line = line[:pos_open_tag+1] + dst + line[pos_close_tag:]
                print(f"XXX\t\t\t new_line |{new_line}|")
                has_changed = True
            elif '<' in tag_content:    # ref with caption
                pos_init_caption = line.find('<', pos_tag + 1)
                pos_end_caption = line.find('>', pos_init_caption + 1)
                assert pos_init_caption < pos_end_caption, "malformed rst on line %s" % line
                caption_content = line[pos_init_caption + 1:pos_end_caption]
                print(f"XXX\t\t\t it is a caption reference |{caption_content}|")
                if caption_content == src:
                    has_changed = True
                    new_line = line[:pos_init_caption + 1] + dst + line[pos_end_caption:]
    else:
        new_pos = len(line)         # no more tags here

    return new_state, has_changed, new_line, new_pos

def check_line_for_tag(tag, line, src, dst):
    """ checks for tag in the line
        It will consume the whole line
        It returns:
        - has_changed: True if there's a change
        - new_line: contents of the line once replaced
    """
    has_changed = False
    new_line = line
    pos = 0
    state = 'new tag'
    while 0 <= pos < len(line):
        if state == 'new tag':
            state, has_change_partial, new_line, pos = check_partial_line_for_tag(tag, new_line, pos, src, dst)
        else: # state == 'caption only'
            state, has_changed_partial, new_line, pos = check_line_for_caption(new_line, src, dst)
        has_changed = has_changed or has_change_partial
    return has_changed, new_line


def look_for_tag(tag, rstcontents, src, dst):
    """ This method is specialized in references with directives like :ref: and :doc:
        It expects tag to contain ':ref:' or ':doc:'
        These directives allow the following variants:
        - :ref:`objectwithoutextension`
        - :ref:`text for caption <objectwithoutextension>`
        When object appears within <>, it can go in the next line
    """
    print(f"XXX look_for_ref(src {src} dst {dst})")
    if src.suffix != '.rst' or dst.suffix != '.rst':
        return list()       # non rst can't be in a toctree
    src = str(src)[:-4] # remove extension since references go without
    dst = str(dst)[:-4]
    changes = list()
    state = 'new tag'
    for nr, line in enumerate(rstcontents):
        has_changed, new_line = check_line_for_tag(tag, line, src, dst)
        if has_changed:
            change = {
                'line': nr, 
                'src': line,
                'dst': new_line.
            }
           changes.append(change)
    return changes

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
        - the reference path are always relative to the rst. 
          - when the reference starts with /, it means from the parent of the rst
          - otherwise it also means the same, so / at the beginning is superfluous
        - references can be:
          - after a figure::
          - after a image::
          - on a toctree (only for .rst with or without .rst extension)
          - after a :ref: (only for .rst including the <> variant) (without .rst extension)
          - after a :doc: (only for .rst including the <> variant) (without .rst extension)
          - after a literalinclude::
          - after a :download: (including the <> variant)
    """
    result = dict()
    changes = list()    # list of changes
    for function in (look_for_images, 
                     look_for_toctrees,
                     look_for_ref,
                     look_for_doc,
                     ):
        changes += function(rstcontents, src, dst)
    result['result'] = len(changes) > 0
    result['changes'] = changes
    return result

####################################################################################################
#   helping functions for each way of referencing a file
####################################################################################################

def look_for_ref(rstcontents, src, dst):
    """ This method is specialized in references :ref: """
    return look_for_tag(':ref:', rstcontents, src, dst)

def look_for_doc(rstcontents, src, dst):
    """ This method is specialized in references :doc: """
    return look_for_tag(':doc:', rstcontents, src, dst)

def look_for_images(rstcontents, src, dst):
    """ this method is specialized in references to images/figures
    """
    regex_image = r"^(\s*\.\. (image|figure)::\ */?)(%s)$" % src
    changes = list()
    for nr, line in enumerate(rstcontents):
        m = re.match(regex_image, line)
        if not m:
            continue
        change = dict()
        change['line'] = nr
        change['src'] = line
        change['dst'] = re.sub(regex_image, r'\1%s' % dst, line)
        changes.append(change)
    return changes

def look_for_toctrees(rstcontents, src, dst):
    """ This method is specialized in references on toctrees """
    if src.suffix != '.rst' or dst.suffix != '.rst':
        return list()       # non rst can't be in a toctree
    regex_toctree = r"^(\s*)\.\. toctree::\s*$"
    regex_toctree_entry = r"^(\s*)([^\s].*)?$"
    changes = list()
    in_toctree = False
    min_indentation = 0     # minimum indentation for items in toctree
    for nr, line in enumerate(rstcontents):
        if not in_toctree:
            m = re.match(regex_toctree, line)
            if m:
                in_toctree = True
                min_indentation = len(m.group(1)) + 1
            continue
        if not line.strip():    # ignore empty lines
            continue
        m = re.match(regex_toctree_entry, line)
        if not m or len(m.group(1)) < min_indentation:  # end of toctree
            in_toctree = False
            continue
        if not m.group(2).strip() in (str(src), str(src)[:-4]):  # not our src
            continue
        change = dict()
        change['line'] = nr
        change['src'] = line
        if m.group(2).strip() == str(src):
            change['dst'] = m.group(1) + str(dst)
        else:
            change['dst'] = m.group(1) + str(dst)[:-4]
        changes.append(change)
    return changes



