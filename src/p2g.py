import re
import sys
import argparse
import time
import pathlib
from collections import Counter

import P4


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


try:
    p4 = P4.P4()
except:
    eprint(
        "Could not load P4 module. Make sure the P4 CLI is installed on this computer."
    )
    sys.exit(1)

parser = argparse.ArgumentParser(
    description="Gather data from Perforce server for reporting and creates Gource-style log for visualizations."
)

parser.add_argument(
    "depotPath",
    nargs="*",
    help="Depot path to collect data from. Defaults to '//...' which will include all branches of all depots on the server.",
    default=["//..."],
)
parser.add_argument(
    "-e",
    "--exclude",
    help="A path element to exclude from the results. Can be used multiple times.",
)
parser.add_argument(
    "-p",
    "--port",
    help="Overrides any P4PORT setting with the specified protocol:host:port.",
)
parser.add_argument(
    "-P",
    "--password",
    help="Enables a password (or ticket) to be passed on the command line, thus bypassing the password associated with P4PASSWD.",
)
parser.add_argument(
    "-u", "--user", help="Overrides any P4USER setting with the specified user name."
)
parser.add_argument(
    "--no-gource",
    dest="do_gource",
    help="Disables the creation of a Gource log.",
    action="store_false",
)
parser.add_argument(
    "-l", "--logname", help="Name of Gource log file to create.", default="gource.log"
)


REGEX_DEFS = {
    "*": "[^\\/]+",
    "...": ".+",
}

GOURCE_OPS = {
    "branch": "A",
    "move/add": "A",
    "add": "A",
    "edit": "M",
    "integrate": "M",
    "delete": "D",
    "move/delete": "D",
    "purge": "D",
}


def main(args):
    connect_to_p4(args.port, args.user, args.password)

    start_time = time.time()
    print("Getting info on all changelists on server...", end=" ")
    cl_numbers = []
    for depot_path in args.depotPath:
        cl_numbers = list(cl["change"] for cl in get_changelists(depot_path))
    print(f"(took {round(time.time() - start_time)} seconds)")

    description_time = time.time()
    print("Getting descriptions of Changelists...", end=" ")
    descriptions = get_descriptions(cl_numbers)
    print(f"(took {round(time.time() - description_time)} seconds)")

    action_time = time.time()
    print("Getting file actions from Changelists...", end=" ")
    regex = make_regex(args.depotPath)
    file_data, action_counter, unique_usernames = get_file_actions(
        descriptions, regex, excludes=args.exclude
    )
    print(f"(took {round(time.time() - action_time)} seconds)")

    if args.do_gource:
        gource_time = time.time()
        print("Creating Gource log...", end=" ")
        create_gource_log(file_data, args.logname)
        print(f"(took {round(time.time() - gource_time)} seconds)")
        print(f"Gource log created at {pathlib.Path(args.logname).absolute()}")

    print(f"Total Duration: {round(time.time() - start_time)} seconds\n")
    print(f"# of Changelists: {len(cl_numbers)}")
    print(f"# of Users: {len(unique_usernames)}")
    print("Actions: ")
    for action in action_counter:
        print(f"  {action.ljust(12)} {action_counter[action]}")
    return file_data


def connect_to_p4(port=None, user=None, passwd=None):
    try:
        if port:
            p4.port = port
        if user:
            p4.user = user
        if passwd:
            p4.password = passwd
        print(f"Connecting to {p4.port} as {p4.user}")
        p4.connect()
    except:
        eprint(f"Could not connect to Perforce server at {p4.port} as {p4.user}")
        sys.exit(1)


def make_regex(depotPaths):
    """Converts a depot path to a regex Pattern object"""
    full_string = "$|".join(depotPaths) + "$"
    return re.compile(
        full_string.replace("*", REGEX_DEFS["*"]).replace("...", REGEX_DEFS["..."])
    )


def get_changelists(depot_path):
    return p4.run("changes", "-r", "-s", "submitted")


def get_descriptions(cl_numbers):
    return p4.run("describe", "-s", *cl_numbers)


def get_file_actions(descriptions, regex, excludes):
    per_file_data = []
    action_counter = Counter()
    unique_usernames = set()
    for description in descriptions:
        if "action" not in description:
            continue
        for i in range(len(description["action"])):
            if (
                is_in_path(description["depotFile"][i], regex)
                and excludes not in description["depotFile"][i]
            ):
                per_file_data.append(
                    {
                        "timestamp": description["time"],
                        "user": description["user"],
                        "action": GOURCE_OPS[description["action"][i]],
                        "file": description["depotFile"][i],
                    }
                )
                action_counter[description["action"][i]] += 1
                unique_usernames.add(description["user"])
    return per_file_data, action_counter, unique_usernames


def is_in_path(path, regex):
    return regex.match(path) is not None


def create_gource_log(file_data, log_file):
    with open(log_file, "w") as f:
        for file in file_data:
            f.write(
                f"{file['timestamp']}|{file['user']}|{file['action']}|{file['file']}\n"
            )


if __name__ == "__main__":
    args = parser.parse_args()
    result = main(args)
