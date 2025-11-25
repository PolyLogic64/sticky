import json
from pathlib import Path

class Item:
    def __init__(self, done, title):
        self.done = done
        self.title = title

    def __repr__(self):
        return f"Item(done: {self.done}, title: {self.title})"


checklist = []

if Path("savefile.json").exists():
    with open("savefile.json", "r", encoding="utf-8") as f:
        deserialized = json.load(f)

        for thing in deserialized:
            checklist.append(Item(thing["done"], thing["title"]))


# Loop
while (True):
    # Read
    s = input("> ")
    print(repr(s))

    # Evaluate
    if s.strip() == "exit":
        break

    lst = s.split()
    popped = lst.pop(0)

    if popped == "add":
        print("ADD COMMAND")
        joined = " ".join(lst)
        checklist.append(Item(False, joined))
        print(f"rest: {repr(joined)}")
    else:
        print(f"ERROR: Unknown command '{popped}'")
        continue

    # Print
    print(repr(lst))
    print(f"Checklist: {repr(checklist)}")


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

    print(f"Written file '{filename}'")

    filename = "savefile.json"
    with open(filename, "w", encoding="utf-8") as f:
        new_list = []
        for item in checklist:
            new_list.append(vars(item))
            
        json.dump(new_list, f, indent=4)



