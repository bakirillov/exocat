import os
import json
import time
import argparse
import numpy as np
from index import *
import pandas as pd
import pickle as pkl
import os.path as op
from tqdm import tqdm
from leitner import *
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
                lambda x: ".md" in x, 
                [a for a in os.walk(self.config["folder"])][0][2]
            )
        )
        files = [op.join(self.config["folder"], a) for a in files]
        return(files)
    
    def load_card(self, cid, contents=True):
        path = op.join(self.config["folder"], cid+".md")
        if contents:
            with open(path, "r") as ih:
                return(ih.read().lower())
        else:
            return(path)
        
    def run_program(self, path, program):
        os.system(self.config[program]+" "+path)
        
    def make_tempfile(self):
        tempdir = "/tmp/exocat/"
        if not op.exists(tempdir):
            os.makedirs(tempdir)
        fn = op.join(tempdir, datetime.now().strftime("%d%m%Y%H%M%S")+".txt")
        return(fn)
        
    def new(self, title, study_mode, old=[]):
        cid = datetime.now().strftime("%d%m%Y%H%M%S")
        if not op.exists(self.config["folder"]):
            os.makedirs(self.config["folder"])
        path = self.load_card(cid, False)
        tmpl = self.template.replace("ID", cid)
        if not title:
            title = input("Enter the title of the card: ")
        tmpl = tmpl.replace("TITLE", title)
        spl = tmpl.split("\n")
        if len(old) == 0:
            whr = spl.index("## Questions" if not study_mode else "## Timeline")
        else:
            whr = spl.index("## Timeline") + 1
        spl = spl[0:whr]
        tmpl = "\n".join(spl)
        if len(old) > 0:
            tmpl += "\n"+"\n".join(old)
        with open(path, "w") as oh:
            oh.write(tmpl)
        self.run_program(path, "editor")
        
    def index(self, cid):
        index_path = op.join(self.config["folder"], "index.pkl")
        if op.exists(index_path):
            with open(index_path, "rb") as ih:
                I = pkl.load(ih)
        else:
            I = CatIndex.empty()
        if cid == "renew":
            I.last = None
        elif cid:
            I.last = cid
        files = self.cards()
        I.index(files)
        I.save(index_path)
        
    def write_down(self, oh, a, b, d):
        oh.write(">\n")
        oh.write(d+"\n")
        a_title = self.load_card(a).split("\n")[0]
        b_title = self.load_card(a).split("\n")[0]
        oh.write(a_title+"\n")
        oh.write(b_title+"\n")
        
    def filter_links(self, links, regex):
        links = {",".join(a): links[a] for a in links}
        if regex:       
            es = {}
            for a in links:
                if re.search(regex, links[a]):
                    es[a] = links[a]
            links = es
        return(links)
        
    def links(self, cid, link_type, regex=None):
        index_path = op.join(self.config["folder"], "index.pkl")
        fn = self.make_tempfile()
        if op.exists(index_path):
            with open(index_path, "rb") as ih:
                I = pkl.load(ih)
            edges = sum([list(a) for a in I.g.edges([cid])], [])
            sg = I.g.subgraph(edges)
            with open(fn, "w") as oh:
                link_types = [link_type]
                if link_type == "all":
                    link_types = ["explicits", "implicits", "source", "timeline"]
                for lt in link_types:
                    eas = self.filter_links(nx.get_edge_attributes(sg, lt), regex)
                    for a in eas:
                        self.write_down(
                            oh, a.split(",")[0], a.split(",")[1], eas[a]
                        )
            print(fn)
            self.run_program(fn, "editor")
        else:
            print("The index is empty")
    
    def overview(self, regex=None):
        index_path = op.join(self.config["folder"], "index.pkl")
        fn = self.make_tempfile()
        if op.exists(index_path):
            with open(index_path, "rb") as ih:
                I = pkl.load(ih)
            explicits = self.filter_links(
                nx.get_edge_attributes(I.g, "explicits"), regex
            )
            implicits = self.filter_links(
                nx.get_edge_attributes(I.g, "implicits"), regex
            )
            source = self.filter_links(
                nx.get_edge_attributes(I.g, "source"), regex
            )
            timeline = self.filter_links(
                nx.get_edge_attributes(I.g, "timeline"), regex
            )
            with open(fn, "w") as oh:
                for what in [explicits, implicits, source, timeline]:
                    for a in what:
                        self.write_down(
                            oh, a.split(",")[0], a.split(",")[1], what[a]
                        )
            print(fn)
            self.run_program(fn, "editor")
        else:
            print("The index is empty")
    
    def edit(self, cid):
        if not cid:
            cid = input("Enter the id of the card to edit: ")
        self.run_program(self.load_card(cid, False), "editor")
        
    def view(self, cid):
        if not cid:
            cid = input("Enter the id of the card to view: ")
        self.run_program(self.load_card(cid, False), "viewer")
        
    @staticmethod
    def get_media(s):
        media = re.findall("\(\(\w+\.\w+\)\)", s)
        media = [a.replace("((", "").replace("))", "").lower() for a in media]
        return(media)
        
    def view_media(self, cid):
        if not cid:
            cid = input("Enter the id of the card to view media from: ")
        card = self.load_card(cid, True)
        fns = ExoCat.get_media(card)
        for fn in fns:
            print(fn)
            full_fn = op.join(self.config["folder"], fn)
            extension = op.splitext(full_fn)[-1].lower()
            if extension in [".jpg", ".png", ".jpeg", ".giff", ".tiff"]:
                self.run_program(full_fn, "images")
            elif extension in [".mp3", ".wav"]:
                self.run_program(full_fn, "audios")
            elif extension in [".mp4", ".avi", ".mkv"]:
                self.run_program(full_fn, "videos")
            input()
        
    def query(self, regex, section="full", open_newest=True):
        files = self.cards()
        texts = []
        for i,a in tqdm(list(enumerate(files))):
            with open(a) as oh:
                texts.append((i, oh.read().lower()))
        if section == "title":
            texts = [(a[0], a[1].split("\n")[0]) for a in texts]
        filtered = list(filter(lambda x: re.search(regex.lower(), x[1]), texts))
        filtered = [a[1].split("\n")[0] for a in filtered]
        filtered = list(sorted(filtered, key=lambda x: int(x.split(" ")[1][:-1])))
        print("\n")
        if len(filtered) > 0:
            for a in filtered:
                print(a)
            if open_newest:
                self.run_program(
                    self.load_card(filtered[-1].split(" ")[1][:-1], False), "editor"
                )
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

def index_cards(args):
    cat = ExoCat()
    cat.index(args.card_id)
    
def query_cards(args):
    cat = ExoCat()
    if args.title:
        cat.query(args.title, section="title", open_newest=args.open)
    elif args.full:
        cat.query(args.full, open_newest=args.open)
        
def links_cards(args):
    cat = ExoCat()
    cat.links(args.card_id, args.type, args.regex)
    
def overview(args):
    cat = ExoCat()
    cat.overview(args.regex)

def study_cards(args):
    cat = ExoCat()
    box_fn = op.join(cat.config["folder"], "box.pkl")
    if not op.exists(box_fn):
        lb = LeitnerBox.empty()
        lb.index(cat.cards())
    else:
        lb = LeitnerBox.load(box_fn)
    if args.reindex:
        lb.index(cat.cards())
    lb.study(args.catch_up)
    lb.save(box_fn)

def random_card(args):
    cat = ExoCat()
    cards = cat.cards()
    random_card = np.random.choice(cards)
    print(random_card)
    cat.run_program(random_card, "editor")
    
def media_cards(args):
    cat = ExoCat()
    cat.view_media(args.card_id)
    
    

if __name__ == "__main__":
    print(THECAT)
    parser = argparse.ArgumentParser(description="A personal CLI exocortex assistant")
    subparsers = parser.add_subparsers()
    parser_overview = subparsers.add_parser(
        "overview", help="Give an overview of the included topics"
    )
    parser_overview.add_argument(
        "-r", "--regex", help="Filter the links by regex",
        action="store", default=None
    )
    parser_overview.set_defaults(func=overview)
    parser_new = subparsers.add_parser("new", help="Make a new card")
    parser_new.add_argument(
        "-t", "--title", help="The title of the card",
        default=None
    )
    parser_new.add_argument(
        "-s", "--study", help="Create the card in study mode",
        action="store_true"
    )
    parser_new.set_defaults(func=new_card)
    parser_random = subparsers.add_parser("random", help="Edit a random card")
    parser_random.set_defaults(func=random_card)
    parser_edit = subparsers.add_parser("edit", help="Edit an old card")
    parser_edit.add_argument(
        "-c", "--card-id", help="The id of the card to edit",
        default=None
    )
    parser_edit.set_defaults(func=edit_card)
    parser_view = subparsers.add_parser("view", help="View an existing card")
    parser_view.add_argument(
        "-c", "--card-id", help="The id of the card to view",
        default=None
    )
    parser_view.set_defaults(func=view_card)
    parser_index = subparsers.add_parser(
        "index", help="Index existing cards"
    )
    parser_index.add_argument(
        "-c", "--card-id", help="The id of the card to start index from",
        default=None
    )
    parser_index.set_defaults(func=index_cards)
    parser_query = subparsers.add_parser(
        "query", help="Query the exocortex"
    )
    parser_query.add_argument(
        "-t", "--title", help="The regular expression for title",
        default=None
    )
    parser_query.add_argument(
        "-f", "--full", help="The regular expression for full-text search",
        default=None
    )
    parser_query.add_argument(
        "-o", "--open", help="Open the newest suitable file",
        action="store_true", default=False
    )
    parser_query.set_defaults(func=query_cards)
    parser_links = subparsers.add_parser(
        "links", help="Query the index for links"
    )
    parser_links.add_argument(
        "-c", "--card-id", help="The id of the card to show the links",
        default=None
    )
    parser_links.add_argument(
        "-t", "--type", help="The link type",
        default="all", choices=["all", "explicits", "implicits", "source", "timeline"] 
    )
    parser_links.add_argument(
        "-r", "--regex", help="Filter the links by regex",
        action="store", default=None
    )
    parser_links.set_defaults(func=links_cards)
    parser_study = subparsers.add_parser(
        "study", help="Study the materials through the Leitner box system"
    )
    parser_study.add_argument(
        "-r", "--reindex", help="Reindex the Leitner box",
        action="store_true"
    )
    parser_study.add_argument(
        "-c", "--catch-up", help="Limits the number of cards reviewed to 25",
        action="store_true"
    )
    parser_study.set_defaults(func=study_cards)
    parser_media = subparsers.add_parser(
        "media", help="View media files associated with the card"
    )
    parser_media.add_argument(
        "-c", "--card-id", help="The id of the card to show the media files",
        default=None
    )
    parser_media.set_defaults(func=media_cards)
    args = parser.parse_args()
    args.func(args)
