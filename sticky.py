import json
import argparse
import logging
from pathlib import Path
from dataclasses import dataclass

@dataclass(kw_only=True)
class Item:
    title: str
    done: bool = False


def actual_main(checklistPath):
    logger = logging.getLogger("main")

    checklist = []

    if Path(checklistPath).exists():
        with open(checklistPath, "r", encoding="utf-8") as f:
            deserialized = json.load(f)

            for thing in deserialized:
                checklist.append(Item(done=thing["done"], title=thing["title"]))


    # Loop
    while (True):
        for index, item in enumerate(checklist):
            # TODO: maybe make a function that converts a item to string
            if item.done:
                mark = "x"
            else:
                mark = " "
            print(f"{index}  [{mark}] {item.title}")
    
        # Read
        print()
        s = input("> ")
        logger.info(repr(s))

        # Evaluate
        if s.strip() == "exit":
            break

        lst = s.split()
        popped = lst.pop(0)

        if popped == "add":
            logger.info("ADD COMMAND")
            joined = " ".join(lst)
            checklist.append(Item(done=False, title=joined))
            logger.info(f"rest: {repr(joined)}")
        elif popped == "mark":
            # what if the user didnt supply anything after mark, and or if it isnt an int
            index = int(lst.pop(0))
            checklist[index].done = True
        elif popped == "delete":
            # what if the user didnt supply anything after mark, and or if it isnt an int
            index = int(lst.pop(0))
            del checklist[index]
        else:
            logger.error(f"ERROR: Unknown command '{popped}'")
            continue

        # Print
        logger.info(repr(lst))
        logger.info(f"Checklist: {repr(checklist)}")


        # Save the text file
        filename = "checklist.txt"
        with open(filename, "w", encoding="utf-8") as f:
            f.write("=== CHECKLIST ===\n")
            
            for item in checklist:        
                if item.done:
                    mark = "x"
                else:
                    mark = " "

                f.write(f"[{mark}] {item.title}\n")
                
        logger.info(f"Written file '{filename}'")



        with open(checklistPath, "w", encoding="utf-8") as f:
            new_list = []
            for item in checklist:
                new_list.append(vars(item))
                
            json.dump(new_list, f, indent=4)




def main():
    parser = argparse.ArgumentParser()

    DEFAULT_LOGGING_LEVEL = "INFO"
    parser.add_argument(
        "--log-level",
        default=DEFAULT_LOGGING_LEVEL,
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help=f"Set console log output level (default: {DEFAULT_LOGGING_LEVEL})",
        type=str,
    )
    parser.add_argument(
        "checklist",
        type=Path
    )

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
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    actual_main(args.checklist)    


if __name__ == "__main__":
    main()
