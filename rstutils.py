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
    print("XXX paths[0]", paths[0])
    print("XXX paths[0].is_dir()", paths[0].is_dir())
    common_paths = set((paths[0] / '_').parents if paths[0].is_dir() else paths[0].parents)
    print("XXX common_paths", common_paths)
    for path in paths[1:]:
        parents = set((path / '_').parents if path.is_dir() else path.parents)
        common_paths = common_paths.intersection(parents)
    return max(common_paths)



if __name__ == "__main__":
    print("ERROR: nothing to see here!")
