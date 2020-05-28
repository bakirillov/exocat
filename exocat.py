import os
import json
import time
import argparse
import os.path as op
from tqdm import tqdm
from datetime import datetime

THECAT = """ _._     _,-'""`-._
(,-.`._,'(       |\`-/|
    `-.-' \ )-`( , o o)
          `-    \`_`"'-
"""


class ExoCat():
    
    def __init__(self):
        with open("TEMPLATE.md", "r") as ih:
            self.template = ih.read()
        with open("config.json", "r") as ih:
            self.config = json.loads(ih.read())
        
    def new(self, title):
        cid = datetime.now().strftime("%d%m%Y%H%M%S")
        if not op.exists(self.config["folder"]):
            os.makedirs(self.config["folder"])
        path = op.join(self.config["folder"], cid+".md")
        tmpl = self.template.replace("ID", cid)
        if title == "None":
            title = input("Enter the title of the card: ")
        tmpl = tmpl.replace("TITLE", title)
        with open(path, "w") as oh:
            oh.write(tmpl)
        os.system(self.config["editor"]+" "+path)
        
    def index(self):
        pass
        

if __name__ == "__main__":
    print(THECAT)
    parser = argparse.ArgumentParser(description="A personal CLI exocortex assistant")
    parser.add_argument(
        "command", action="store", help="What should the ExoCat do?", metavar="command",
        choices=["new", "index", "update", "search", "move", "study"]
    )
    parser.add_argument(
        "-t", "--title", help="The title of the card",
        default="None"
    )
    args = parser.parse_args()
    cat = ExoCat()
    if args.command == "new" or args.command == "n":
        cat.new(args.title)