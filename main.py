import json
import argparse
import logging
from pathlib import Path
from dataclasses import dataclass

ItemDict = dict[str, str | bool]


@dataclass(kw_only=True)
class Item:
    title: str
    done: bool = False
    hidden: bool = False


def item_to_string(item: Item) -> str:
    if item.done:
        mark = "x"
    else:
        mark = " "
    return f"[{mark}] {item.title}"


def item_to_dict(item: Item) -> ItemDict:
    return {"title": item.title, "done": item.done, "hidden": item.hidden}


def dict_to_item(d: dict) -> Item:
    return Item(
        done=d.get("done", False), title=d["title"], hidden=d.get("hidden", False)
    )


def load_checklist_from_savefile(savefile_path: Path) -> list[Item]:
    logger = logging.getLogger("load_checklist_from_savefile")

    checklist: list[Item] = []
    with savefile_path.open("r", encoding="utf-8", newline="\n") as f:
        deserialized = json.load(f)  # type: ignore
        assert isinstance(deserialized, list)  # type: ignore

        for thing in deserialized:
            assert isinstance(thing, dict)
            checklist.append(dict_to_item(thing))
    logger.debug(f"Loaded Checklist: {checklist!r}")
    return checklist


def save_savefile(savefile_path: Path, checklist: list[Item]) -> None:
    logger = logging.getLogger("save_savefile")

    with savefile_path.open("w", encoding="utf-8", newline="\n") as f:
        savefile_items: list[ItemDict] = []
        for item in checklist:
            savefile_items.append(item_to_dict(item))

        json.dump(savefile_items, f, indent=4)

    logger.debug(f"Written file '{savefile_path}'")


def save_checklist(checklist: list[Item]) -> None:
    logger = logging.getLogger("save_checklist")

    filename = "checklist.txt"
    with open(filename, "w", encoding="utf-8", newline="\n") as f:
        f.write("=== CHECKLIST ===\n")

        for item in checklist:
            if item.hidden:
                continue
            f.write(f"{item_to_string(item)}\n")

    logger.debug(f"Written file '{filename}'")


def add_command(checklist: list[Item], splitted_string: list[str]) -> None:
    logger = logging.getLogger("add_command")

    logger.debug("ADD COMMAND")
    joined = " ".join(splitted_string)
    logger.debug(f"rest: {joined!r}")
    checklist.append(Item(done=False, title=joined))


def get_index_from_command_argument(splitted_string: list[str]) -> int | None:
    logger = logging.getLogger("get_index_from_command_argument")

    try:
        return int(splitted_string.pop(0), base=10)
    except (
        IndexError
    ) as err:  # when pop() failed, either it's nothing, or out of bounds
        logger.debug(f"IndexError: {err!r}")
        logger.error("You didn't supply anything")
        return None
    except ValueError as err:  # when int() failed and the string isnt a number
        logger.debug(f"ValueError: {err!r}")
        logger.error("What you typed in isn't a number")
        return None


def print_usage() -> None:
    print()
    print("REPL Commands:")
    print("  help        -- print this help message")
    print("  exit        -- exit the program")
    print("  add <name>  -- appends a new item to the checklist")
    print("  mark <id>   -- marks an item as completed")
    print("  delete <id> -- deletes an item from the checklist")
    print("  save        -- save the checklist manually")
    print("  clean       -- 'delete' all marked items")
    print()


def actual_main(savefile_path: Path) -> None:
    logger = logging.getLogger("main")

    if not savefile_path.exists():
        logger.error(f"The path provided: '{savefile_path}' doesn't exist.")
        return

    checklist = load_checklist_from_savefile(savefile_path)
    print_usage()

    # Loop
    while True:
        for pos, item in enumerate(checklist):
            if item.hidden:
                continue
            print(f"{pos:>2}  {item_to_string(item)}")

        # Read
        print()
        s = input("> ")
        logger.debug(repr(s))

        # Evaluate
        if s.strip() == "exit":
            break

        # https://docs.python.org/3/library/stdtypes.html#str.split:~:text=the%20result%20will%20contain%20no%20empty%20strings%20at%20the%20start%20or%20end%20if%20the%20string%20has%20leading%20or%20trailing%20whitespace
        # split() has a built-in strip()
        splitted_string = s.split()
        command = splitted_string.pop(0)

        if command == "add":
            add_command(checklist, splitted_string)
        elif command == "mark":
            index = get_index_from_command_argument(splitted_string)
            if index is None:
                continue

            if index >= len(checklist):
                logger.error("The index is out of bounds")
                continue

            checklist[index].done = True

        elif command == "delete":
            index = get_index_from_command_argument(splitted_string)
            if index is None:
                continue

            if index >= len(checklist):
                logger.error("The index is out of bounds")
                continue

            checklist[index].hidden = True

        elif command == "help":
            print_usage()
        elif command == "save":
            save_savefile(savefile_path, checklist)
        elif command == "clean":
            for item in checklist:
                if item.done:
                    item.hidden = True
        else:
            logger.error(f"ERROR: Unknown command '{command}'")
            continue

        # Print
        logger.debug(f"splitted_string: {splitted_string!r}")
        logger.debug(f"Checklist: {checklist!r}")

        save_checklist(checklist)
        save_savefile(savefile_path, checklist)


def main() -> None:
    parser = argparse.ArgumentParser()

    DEFAULT_LOGGING_LEVEL = "INFO"
    parser.add_argument(
        "--log-level",
        default=DEFAULT_LOGGING_LEVEL,
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help=f"Set console log output level (default: {DEFAULT_LOGGING_LEVEL})",
        type=str,
    )
    parser.add_argument("checklist", type=Path)

    args = parser.parse_args()

    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)  # has to be debug so the logger captures everything
    console_handler = logging.StreamHandler()
    console_handler.setLevel(
        getattr(
            logging,
            args.log_level.upper(),  # type: ignore # this is the actual level that the console uses
        )
        # this 'getattr' is the actual 'pythonic' way of doing it (as seen in https://docs.python.org/3/howto/logging.html#logging-to-a-file)
    )
    formatter = logging.Formatter(
        "%(levelname)s - %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    actual_main(args.checklist)  # type: ignore


if __name__ == "__main__":
    main()
