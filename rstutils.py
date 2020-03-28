"""
    Utilities for the rst scripts
"""

import pathlib


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


if __name__ == "__main__":
    print("ERROR: nothing to see here!")
