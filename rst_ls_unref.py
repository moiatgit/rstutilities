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
    print("XXX once checked, options", options)
    #changes = compute_changes(**options)
    #if changes:
    #    show_changes(changes, options['base_folder'])
    #    confirmed = ask_for_confirmation(options['force'])
    #    if confirmed:
    #        perform_changes(changes)
    #        rename_src(options['src'], options['dst'])
    #    else:
    #        print("No changes performed")
    #else:
    #    print("No references found. Only the file %s will be renamed" % options['src'].relative_to(options['base_folder']))
    #    confirmed = ask_for_confirmation(options['force'])
    #    if confirmed:
    #        rename_src(options['src'], options['dst'])


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
    print("XXX check_options()", options)
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




