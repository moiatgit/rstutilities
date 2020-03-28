#! /usr/bin/env python3

"""
    This script lists the files that have no references in a base rst folder

    The script gets the list of files to check and returns those of them that have no rst file referencing
    to them.
"""
import sys
import argparse
import pathlib

import rstutils


####################################################################################################

def main():
    options = parse_commandline_args()
    check_options(options)
    unreferenced = check_unreferenced(**options)
    if unreferenced:
        print("List of unreferenced files:")
        for path in unreferenced:
            print("\t", path.relative_to(options['base_folder']))
    else:
        print("All files are referenced")

def check_unreferenced(paths, base_folder):
    """ given a list of paths and a base folder containing the rst files, it
        returns the list of paths that are referenced by any rst file in the base folder """
    referenced = list()
    checked_files = list()
    items = paths[:]
    while items:
        item = items.pop()
        if item .is_symlink():
            continue            # symlinks are ignored to avoid potential infinite loops
        if item .is_dir():
            items.extend(list(item .iterdir()))
            continue
        checked_files.append(item)
        path = item.relative_to(base_folder)
        for rst in rstutils.get_rst_in_folder(base_folder):
            if rstutils.seek_references_in_file(rst, path):
                referenced.append(base_folder / path)
                break
    return [path for path in checked_files if path not in referenced]

def parse_commandline_args():
    """ defines the arguments and returns a dict containing the options with
        the following normalization:
        * 'paths' are converted to pathlib.Path
        * 'base_folder' is also converted if given
    """
    parser = argparse.ArgumentParser(
        description=("Script that lists all the resources defined in the "
                     "--paths argument that are not referenced in any rst "
                     "file in the --base-dir.")
    )

    parser.add_argument("paths",
                        type=str,
                        nargs='+',
                        help="files to check")
    parser.add_argument("-b", "--base-dir",
                        required=False,
                        help=("Base directory for the rst project. If not specified, then "
                              "the deepest common path in --paths will be considered instead."),
                        dest='base_folder',
                        type=str,
                        )

    args = parser.parse_args()
    normalized_args = dict()
    normalized_args['paths'] = list()
    for path in args.paths:
        normalized_args['paths'].append(pathlib.Path(path).resolve())
    if args.base_folder:
        normalized_args['base_folder'] = pathlib.Path(args.base_folder).resolve()
    return normalized_args

def check_options(options):
    """ checks the existence of the paths
        it breaks execution if:
        - any of the options['paths'] doesn't exist
        - in case options['base_folder'] is provided, it is not an ancestor of all the paths
        In case base_folder is not provided, it is set to the deepest common path of all the paths
    """
    if any(not path.exists() for path in options['paths']):
        print("ERROR: all the paths must exist")
        sys.exit(1)

    cdp = rstutils.deepest_common_path(options['paths'])

    if 'base_folder' not in options:
        options['base_folder'] = cdp
        return

    if options['base_folder'] not in (cdp / '_').parents:
        print("ERROR: base folder must contain all the paths")
        sys.exit(1)


if __name__ == "__main__":
    main()




