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
        
    def new(self, title, study_mode, old=[]):
        cid = datetime.now().strftime("%d%m%Y%H%M%S")
        if not op.exists(self.config["folder"]):
            os.makedirs(self.config["folder"])
        path = op.join(self.config["folder"], cid+".md")
        tmpl = self.template.replace("ID", cid)
        if title == "None":
            title = input("Enter the title of the card: ")
        tmpl = tmpl.replace("TITLE", title)
        spl = tmpl.split("\n")
        if len(old) == 0:
            whr = spl.index("## Study" if not study_mode else "## Timeline")
        else:
            whr = spl.index("## Timeline") + 1
        spl = spl[0:whr]
        tmpl = "\n".join(spl)
        if len(old) > 0:
            tmpl += "\n"+"\n".join(old)
        with open(path, "w") as oh:
            oh.write(tmpl)
        os.system(self.config["editor"]+" "+path)
    
    def update(self, cid):
        if cid == "None":
            cid = input("Enter the id of the card to edit: ")
        path = op.join(self.config["folder"], cid+".md")
        with open(path, "r") as ih:
            old = ih.read()
        title = old.split("\n")[0].replace("# ", "").split(": ")[-1]
        self.new(title, False, old = [cid])
        
    def index(self):
        pass
    
    def edit(self, cid):
        if cid == "None":
            cid = input("Enter the id of the card to edit: ")
        path = op.join(self.config["folder"], cid+".md")
        os.system(self.config["editor"]+" "+path)
        
        
def new_card(args):
    cat = ExoCat()
    cat.new(args.title, args.study)
    
def edit_card(args):
    cat = ExoCat()
    cat.edit(args.card_id)
    
def update_card(args):
    cat = ExoCat()
    cat.update(args.card_id)

    
if __name__ == "__main__":
    print(THECAT)
    parser = argparse.ArgumentParser(description="A personal CLI exocortex assistant")
    subparsers = parser.add_subparsers()
    parser_new = subparsers.add_parser("new", help="Make a new card")
    parser_new.add_argument(
        "-t", "--title", help="The title of the card",
        default="None"
    )
    parser_new.add_argument(
        "-s", "--study", help="Create the card in study mode",
        action="store_true"
    )
    parser_new.set_defaults(func=new_card)
    parser_edit = subparsers.add_parser("edit", help="Edit an old card")
    parser_edit.add_argument(
        "-c", "--card-id", help="The id of the card to edit",
        default="None"
    )
    parser_edit.set_defaults(func=edit_card)
    parser_update = subparsers.add_parser(
        "update", help="Update an old card with additional information"
    )
    parser_update.add_argument(
        "-c", "--card-id", help="The id of the card to edit",
        default="None"
    )
    parser_update.set_defaults(func=update_card)
    args = parser.parse_args()
    args.func(args)
