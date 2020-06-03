import os
import json
import time
import argparse
from index import *
import pickle as pkl
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
            
    def cards(self):
        files = list(
            filter(
                lambda x: x != "index.pkl", 
                [a for a in os.walk(self.config["folder"])][0][2]
            )
        )
        files = [op.join(self.config["folder"], a) for a in files]
        return(files)
        
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
        
    def index(self, cid):
        index_path = op.join(self.config["folder"], "index.pkl")
        if op.exists(index_path):
            with open(index_path, "rb") as ih:
                I = pkl.load(ih)
        else:
            I = CatIndex.empty()
        if cid == "renew":
            I.last = "None"
        elif cid != "None":
            I.last = cid
        files = self.cards()
        I.index(files)
        I.save(index_path)
        
    def links(self, cid, link_type):
        index_path = op.join(self.config["folder"], "index.pkl")
        if op.exists(index_path):
            with open(index_path, "rb") as ih:
                I = pkl.load(ih)
            edges = sum([list(a) for a in I.g.edges([cid])], [])
            sg = I.g.subgraph(edges)
            if link_type != "all":
                print(nx.get_edge_attributes(sg, link_type))
            else:
                print(nx.get_edge_attributes(sg, "explicits"))
                print(nx.get_edge_attributes(sg, "implicits"))
                print(nx.get_edge_attributes(sg, "source"))
                print(nx.get_edge_attributes(sg, "timeline"))
        else:
            print("The index is empty")
    
    def overview(self, use_implicits=False, open_output=True):
        index_path = op.join(self.config["folder"], "index.pkl")
        tempdir = "/tmp/exocat/"
        if not op.exists(tempdir):
            os.makedirs(tempdir)
        fn = op.join(tempdir, datetime.now().strftime("%d%m%Y%H%M%S")+".txt")
        if op.exists(index_path):
            with open(index_path, "rb") as ih:
                I = pkl.load(ih)
            explicits = nx.get_edge_attributes(I.g, "explicits")
            with open(fn, "w") as oh:
                for a in explicits:
                    oh.write(">\n")
                    oh.write(explicits[a]+"\n")
                    a_fn = op.join(self.config["folder"], a[0]+".md")
                    with open(a_fn, "r") as ih:
                        a_title = ih.read().lower().split("\n")[0]
                    b_fn = op.join(self.config["folder"], a[1]+".md")
                    with open(b_fn, "r") as ih:
                        b_title = ih.read().lower().split("\n")[0]
                    oh.write(a_title+"\n")
                    oh.write(b_title+"\n")
                if use_implicits:
                    for a in implicits:
                        a_fn = op.join(self.config["folder"], a[0]+".md")
                        with open(a_fn, "r") as ih:
                            a_title = ih.read().lower().split("\n")[0]
                        b_fn = op.join(self.config["folder"], a[1]+".md")
                        with open(b_fn, "r") as ih:
                            b_title = ih.read().lower().split("\n")[0]
                        oh.write(a_title+"\n")
                        oh.write(b_title+"\n")
            print(fn)
            if open_output:
                os.system(self.config["editor"]+" "+fn)
        else:
            print("The index is empty")
    
    def edit(self, cid):
        if cid == "None":
            cid = input("Enter the id of the card to edit: ")
        path = op.join(self.config["folder"], cid+".md")
        os.system(self.config["editor"]+" "+path)
        
    def view(self, cid):
        if cid == "None":
            cid = input("Enter the id of the card to view: ")
        path = op.join(self.config["folder"], cid+".md")
        command = self.config["viewer"]+" "+path
        os.system(command)
        
    def query(self, regex, section="full"):
        files = self.cards()
        texts = []
        for i,a in tqdm(list(enumerate(files))):
            with open(a) as oh:
                texts.append((i, oh.read().lower()))
        if section == "title":
            texts = [(a[0], a[1].split("\n")[0]) for a in texts]
        filtered = list(filter(lambda x: re.search(regex, x[1]), texts))
        filtered = [a[1].split("\n")[0] for a in filtered]
        print("\n")
        if len(filtered) > 0:
            for a in filtered:
                print(a)
        else:
            print("Not found")
        
        
def new_card(args):
    cat = ExoCat()
    cat.new(args.title, args.study)
    
def view_card(args):
    cat = ExoCat()
    cat.view(args.card_id)
    
def edit_card(args):
    cat = ExoCat()
    cat.edit(args.card_id)
    
def update_card(args):
    cat = ExoCat()
    cat.update(args.card_id)

def index_cards(args):
    cat = ExoCat()
    cat.index(args.card_id)
    
def query_cards(args):
    cat = ExoCat()
    if args.title != "None":
        cat.query(args.title, section="title")
    elif args.full != "None":
        cat.query(args.full)
        
def links_cards(args):
    cat = ExoCat()
    cat.links(args.card_id, args.type)
    
def overview(args):
    cat = ExoCat()
    cat.overview(args.implicits, args.open)
    
if __name__ == "__main__":
    print(THECAT) #new edit update index study search neighborhood 
    parser = argparse.ArgumentParser(description="A personal CLI exocortex assistant")
    subparsers = parser.add_subparsers()
    parser_overview = subparsers.add_parser(
        "overview", help="Give an overview of the included topics"
    )
    parser_overview.add_argument(
        "-i", "--implicits", help="Use implicit links",
        action="store_true", default=False
    )
    parser_overview.add_argument(
        "-o", "--open", help="Open the overview in editor",
        action="store_true", default=True
    )
    parser_overview.set_defaults(func=overview)
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
    parser_view = subparsers.add_parser("view", help="View an existing card")
    parser_view.add_argument(
        "-c", "--card-id", help="The id of the card to view",
        default="None"
    )
    parser_view.set_defaults(func=view_card)
    parser_update = subparsers.add_parser(
        "update", help="Update an old card with additional information"
    )
    parser_update.add_argument(
        "-c", "--card-id", help="The id of the card to edit",
        default="None"
    )
    parser_update.set_defaults(func=update_card)
    parser_index = subparsers.add_parser(
        "index", help="Index existing cards"
    )
    parser_index.add_argument(
        "-c", "--card-id", help="The id of the card to start index from",
        default="None"
    )
    parser_index.set_defaults(func=index_cards)
    parser_query = subparsers.add_parser(
        "query", help="Query the exocortex"
    )
    parser_query.add_argument(
        "-t", "--title", help="The regular expression for title",
        default="None"
    )
    parser_query.add_argument(
        "-f", "--full", help="The regular expression for full-text search",
        default="None"
    )
    parser_query.set_defaults(func=query_cards)
    parser_links = subparsers.add_parser(
        "links", help="Query the index for links"
    )
    parser_links.add_argument(
        "-c", "--card-id", help="The id of the card to show the links",
        default="None"
    )
    parser_links.add_argument(
        "-t", "--type", help="The link type",
        default="all", choices=["all", "explicit", "implicit", "source", "timeline"] 
    )
    parser_links.set_defaults(func=links_cards)
    args = parser.parse_args()
    args.func(args)
