#! /usr/bin/env python3

"""
    This script renames rst files including references

    It is git aware in the sense that, if the file to be renamed is in a git repo,
    it is renamed using git to ease control identification.
"""

# XXX TODO: absolute references (/) are relative to the source directory. Relative references are relative to the rst file
#           There's a first attempt to deal with it. Check function check_for_image_tag()
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
        changes = check_rst_references(lines, 
                                               src.relative_to(rst.parent),
                                               dst.relative_to(rst.parent))
    #XXX HERE!:
    #    - consider removing the posibility to define more than one folder but for base path
    #    - consider XXX for recursive option
    #    - then prepare a function to show the changes if interactive (not forced)
    #    - then perform the changes including renaming src file


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

def check_line_for_caption(line, target):
    """ checks for <target> in line

        IMPORTANT: '<' cannot appear within the caption text

        It returns:
        - if the reference is still splitted (no reference found)
        - the position where the target has been found (-1 if not found)
        - the position where to keep looking for further references
    """
    pos_init_caption = line.find('<') 
    if pos_init_caption < 0:
        reference_splitted = True
        target_pos = -1
        next_pos = len(line)
    else:
        reference_splitted = False
        pos_end_caption = line.find('>')
        assert pos_init_caption < pos_end_caption, "malformed rst on line %s" % line
        reference = line[pos_init_caption + 1: pos_end_caption]
        if reference == target:
            target_pos = pos_init_caption + 1
        else:
            target_pos = -1
        next_pos = pos_end_caption + 2 # counting '>`'
    return reference_splitted, target_pos, next_pos


def check_partial_line_for_tag(tag, line, pos, target):
    """ given a line and a pos to start checking, it looks for tag from pos in the line.
        It returns:
        - if the reference is splitted. i.e. there's a caption and <> part will appear in another line
        - the position where the target has been found (-1 if not found)
        - the position where to keep looking for further references
    """
    pos_tag = line.find(tag, pos)
    if pos_tag < 0:
        return False, -1, len(line)

    pos_open_tag = line.find('`', pos_tag)
    pos_close_tag = line.find('`', pos_open_tag + 1)
    if pos_close_tag < 0:   # splitted tag
        return True, -1, len(line)

    next_pos = pos_close_tag + 1
    tag_content = line[pos_open_tag+1: pos_close_tag]
    if tag_content == target:  # tag`target`
        return False, pos_open_tag + 1, next_pos

    if '<' not in tag_content:    # references to another target
        return False, -1, next_pos

    pos_init_caption = line.find('<', pos_tag + 1)
    pos_end_caption = line.find('>', pos_init_caption + 1)
    assert pos_init_caption < pos_end_caption, "malformed rst on line %s" % line
    caption_content = line[pos_init_caption + 1:pos_end_caption]
    if caption_content == target:
        return False, pos_init_caption + 1, next_pos

    return False, -1, next_pos


def check_line_for_tag(tag, reference_splitted, line, target):
    """ checks for tag in the line
        It works in two different ways depending on the value of reference_splitted:
        - False: it expects to find the tag
        - True: the tag was found in a previous line, so it looks just for the target
        It will consume the whole line when return
        It returns:
        - if the reference is still splitted
        - a list of positions in the line where src has been found
    """
    positions = []
    next_pos = 0
    while 0 <= next_pos < len(line):
        if reference_splitted:
            reference_splitted, reference_pos, next_pos = check_line_for_caption(line, target)
        else:
            reference_splitted, reference_pos, next_pos = check_partial_line_for_tag(tag, line, next_pos, target)
        if reference_pos >= 0:
            positions.append(reference_pos)
    return reference_splitted, positions


def look_for_tag(tag, rstcontents, src, rst_only=True):
    """ This method is specialized in references with directives like :ref: and :doc:
        It expects tag to contain ':ref:' or ':doc:'
        These directives allow the following variants:
        - :ref:`objectwithoutextension`
        - :ref:`text for caption <objectwithoutextension>`
        When object appears within <>, it can appear splitted from the tag line. e.g.
            :ref:`a ref
            with
            a caption <target>`
    """
    if rst_only:
        if src.suffix != '.rst':
            return list()       # non rst can't be in a toctree
        target = str(src)[:-4]  # remove extension since rst_only references go without
    else:
        target = str(src)       # keep the extension when non rst_only
    changes = list()
    reference_splitted = False   # initially, the tag is expected
    for nr, line in enumerate(rstcontents):
        reference_splitted, positions = check_line_for_tag(tag, reference_splitted, line, target)
        changes.extend([(nr, pos) for pos in positions])
    return changes

def check_rst_references(rstcontents, src):
    """ Given:
            rstcontents: str with the contents of a rst file
            src: a pathlib relative to the rst file with the old name
        it returns a list of pairs (line, pos) where
            - line: és el número de línia on s'ha trobat una referència a substituir
            - pos: és el número del caràcter dins de la línia on comença la referència a substituir

        It is possible that there are more than one pair on the same line as there can be more than one reference
        in the same line.

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
                     look_for_figures,
                     look_for_toctrees,
                     look_for_ref,
                     look_for_doc,
                     look_for_dowmload,
                     ):
        changes += function(rstcontents, src)
    return changes

def check_for_image_tag(tag, rstcontents, src, accept_absolute = True):
    """ given a image tag (e.g. '.. image::' or '.. figure::' it returns
        the lines in rstcontents containing a image reference to src.

        XXX Note: As an unconfortable curiosity, the following contents are valid in Sphinx:
            .. figure::
               file.png
               :align: center
        For simplicity, this version of the script doesn't contemplate this case.

        The function returns a list of pairs of change localization
    """
    target = str(src)
    changes = []
    for nr, line in enumerate(rstcontents):
        print(f"XXX checking line {nr} |{line}| for tag |{tag}|")
        if tag not in line:
            continue
        pos_tag = line.find(tag)
        if line[:pos_tag].strip():
            continue    # it's not a real tag probably within a comment
        print("XXX tag found at pos", pos_tag)
        pos_target = line.find(target, pos_tag)
        print(f"XXX target {target} results on {pos_target}")
        if pos_target < 0:
            continue    # a reference to another figure
        contents_between_tag_and_target = line[pos_tag + len(tag):pos_target].strip()
        if contents_between_tag_and_target:
            if not accept_absolute or contents_between_tag_and_target != '/':
                continue    # there's something more before the tag.
        if line[pos_target+len(target):].strip():
            continue    # there's something more after the tag
        changes.append((nr, pos_target))
    return changes

####################################################################################################
#   helping functions for each way of referencing a file
####################################################################################################

def look_for_ref(rstcontents, src):
    """ This method is specialized in references :ref: """
    return look_for_tag(':ref:', rstcontents, src)

def look_for_doc(rstcontents, src):
    """ This method is specialized in references :doc: """
    return look_for_tag(':doc:', rstcontents, src)

def look_for_dowmload(rstcontents, src):
    """ This method is specialized in references :download: """
    return look_for_tag(':download:', rstcontents, src, rst_only=False)

def look_for_images(rstcontents, src):
    """ this method is specialized in references to images """
    return check_for_image_tag('.. image::', rstcontents, src)

def look_for_figures(rstcontents, src):
    """ this method is specialized in references to figures """
    return check_for_image_tag('.. figure::', rstcontents, src)

def look_for_toctrees(rstcontents, src):
    """ This method is specialized in references on toctrees """
    if src.suffix != '.rst':
        return list()       # non rst can't be in a toctree
    target = str(src)
    target_without_extension = target[:-4]
    non_space = re.compile('\S')
    tag = '.. toctree::'
    changes = list()
    in_toctree = False
    min_indentation = 0     # minimum indentation for items in toctree
    for nr, line in enumerate(rstcontents):
        if not in_toctree:
            if tag in line:
                in_toctree = True
                min_indentation = line.find(tag) + 1 # doctree refs should present at least this indentation
            continue
        if not line.strip():    # ignore empty lines
            continue
        m = non_space.search(line)
        if m and m.start() < min_indentation:   # end of this toctree
            in_toctree = False
            continue
        rest_of_line = line[m.start():].strip()
        if rest_of_line == target or rest_of_line == target_without_extension:
            changes.append((nr, m.start()))

    return changes



