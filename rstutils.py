"""
    Utilities for the rst scripts
"""

import pathlib
import re


def deepest_common_path(paths):
    """ given a list of absolute pathlib.Path, it returns a pathlib.Path such
        that it is the deepest common path for all of them.
        - In case the list is empty, it returns the root path
        - In case the list contains just one path, it returns the path itself
          when it is a directory or its parent otherwise
    """
    if not paths:
        return pathlib.Path('/')
    common_paths = set((paths[0] / '_').parents if paths[0].is_dir() else paths[0].parents)
    for path in paths[1:]:
        parents = set((path / '_').parents if path.is_dir() else path.parents)
        common_paths = common_paths.intersection(parents)
    return max(common_paths)

def get_rst_in_folder(folder):
    """ given a folder, it
        generates the pathlib.Path of all the rst files in the folder and all subfolders

        Note: currently the recursive option is disabled (commented out)
    """
    for item in folder.iterdir():
        if item.is_symlink():
            continue            # symlinks are ignored to avoid potential infinite loops
        if item.is_dir():
            continue            # non recursive yet
        #    for subitem in get_potential_rst(item):
        #        yield subitem
        elif item.is_file() and item.suffix == '.rst':
            yield item

def seek_references_in_file(rstpath, target, base_folder):
    """ seeks in the contents of the rstpath for the target (both pathlib.Path)
        It returns a list of pairs (line, pos) of all the references of target in rstpath.  """
    if not target.stem in rstpath.read_text():  # quick filter
        return []
    with open(rstpath) as f:
        lines = f.readlines()
    return check_rst_references(lines, target.relative_to(base_folder))

####################################################################################################
#   Check references
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

def look_for_literalinclude(rstcontents, src):
    """ this method is specialized in references to literalinclude"""
    return check_for_image_tag('.. literalinclude::', rstcontents, src)

def look_for_toctrees(rstcontents, src):
    """ This method is specialized in references on toctrees """
    if src.suffix != '.rst':
        return list()       # non rst can't be in a toctree
    target = str(src)
    target_without_extension = target[:-4]
    non_space = re.compile(r'\S')
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


def check_for_image_tag(tag, rstcontents, src, accept_absolute = True):
    """ given a image tag (e.g. '.. image::' or '.. figure::' it returns
        the lines in rstcontents containing a image reference to src.

        Note: As an unconfortable curiosity, the following contents are valid in Sphinx:
            .. figure::
               file.png
               :align: center

        For simplicity, this version of the script doesn't contemplate this case.

        The function returns a list of pairs of change localization
    """
    target = str(src)
    changes = []
    for nr, line in enumerate(rstcontents):
        if tag not in line:
            continue
        pos_tag = line.find(tag)
        if line[:pos_tag].strip():
            continue    # it's not a real tag probably within a comment
        pos_target = line.find(target, pos_tag)
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
                     look_for_literalinclude,
                     look_for_toctrees,
                     look_for_ref,
                     look_for_doc,
                     look_for_dowmload,
                     ):
        changes += function(rstcontents, src)
    return changes


if __name__ == "__main__":
    print("ERROR: nothing to see here!")
