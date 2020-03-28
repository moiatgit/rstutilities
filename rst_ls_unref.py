#! /usr/bin/env python3

"""
    This script lists the files that have no references in a base rst folder

    The script gets the list of files to check and returns those of them that have no rst file referencing
    to them.
"""
import argparse
import pathlib

####################################################################################################

def main():
    options = parse_commandline_args()
    #check_options(options)
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
        * 'paths' and 'base_folder': are converted to pathlib.Path
        * 'base_folder' is set to deepest common ancestor of all the given paths if not explicitly set by user
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
    #normalized_args['base_folder'] = (pathlib.Path(normalized_args['base_folder']).resolve()
    #                                  if 'base_folder' in normalized_args
    #                                  else normalized_args['src'].parent)
    print("XXX normalized_args", normalized_args)
    return normalized_args


if __name__ == "__main__":
    main()




