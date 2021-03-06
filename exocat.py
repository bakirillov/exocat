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
        self.sections = {
            "title": "#", "description": "## description", 
            "contents": "## contents", "questions": "## questions",
            "answers": "## answers"
        }
        self.keycards_path = op.join(self.config["folder"], "keycards.pkl")
        if not op.exists(self.keycards_path):
            self.keycards = {}
        else:
            with open(self.keycards_path, "rb") as ih:
                self.keycards = pkl.load(ih)
                
    def write_keycards(self):
        with open(self.keycards_path, "wb") as oh:
            pkl.dump(self.keycards, oh)
        
    @staticmethod
    def to_ms(x):
        """needed this because strptime fails for some reason"""
        try:
            day = int(x[0:2])
            month = int(x[2:4])
            year = int(x[4:8])
            hour = int(x[8:10])
            minute = int(x[10:12])
            second = int(x[12:])
            dt = datetime(year, month, day, hour, minute, second)
        except Exception as E:
            return(0)
        else:
            return(dt.timestamp())
        
    def cards(self):
        files = list(
            filter(
                lambda x: ".md" in op.splitext(x)[-1], 
                [a for a in os.walk(op.join(self.config["folder"], "cards"))][0][2]
            )
        )
        files = list(sorted(files, key=lambda x: ExoCat.to_ms(x.split(".")[0])))
        files = [op.join(self.config["folder"], "cards", a) for a in files]
        return(files)
    
    def get_card_id(self, s):
        if s:
            u = re.search("\d+", s)
            if not u and s:
                if s in self.keycards:
                    return(self.keycards[s])
                else:
                    return(None)
            else:
                return(u[0])
        else:
            return(s)
    
    def load_card(self, cid, contents=True, as_is=False):
        path = op.join(self.config["folder"], "cards", cid+".md")
        if contents:
            with open(path, "r") as ih:
                if not as_is:
                    return(ih.read().lower())
                else:
                    return(ih.read())
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
        
    def new(self, title, run_editor=True, inherit=None):
        cid = datetime.now().strftime("%d%m%Y%H%M%S")
        if not op.exists(self.config["folder"]):
            os.makedirs(self.config["folder"])
            os.makedirs(op.join(self.config["folder"], "cards"))
        path = self.load_card(cid, False)
        if not inherit:
            tmpl = self.template.replace("ID", cid)
        else:
            tmpl = self.load_card(self.get_card_id(inherit), as_is=True).replace("ID", cid)
        if not title:
            title = input("Enter the title of the card: ")
        tmpl = tmpl.replace("TITLE", title)
        spl = tmpl.split("\n")
        tmpl = "\n".join(spl)
        with open(path, "w") as oh:
            oh.write(tmpl)
        print(cid+" "+title)
        if run_editor:
            self.run_program(path, "editor")
            self.new_wrap(cid)
        else:
            return(cid)
        
    def new_wrap(self, cid):
        card = self.load_card(cid, True)
        news = re.findall("\[\[.+\]\]", card)
        existing = [
            " ".join(self.load_card(a.replace(".md", "")).split("\n")[0].split(" ")[2:]) 
                for a in self.cards()
        ]
        n = 0
        for a in news:
            nc = a.replace("[[", "").replace("]]", "")
            if nc not in existing:
                time.sleep(1)
                n += 1
                self.new(nc, run_editor=False)
        print("Created "+str(n)+" additional cards")
        
    def index(self, do_implicits=False, do_explicits=True):
        index_path = op.join(self.config["folder"], "index.pkl")
        if op.exists(index_path):
            with open(index_path, "rb") as ih:
                I = pkl.load(ih)
        else:
            I = CatIndex.empty()
            I.zf = self.config["zipf_frequency"]
        files = self.cards()
        I.index(files, do_implicits, do_explicits)
        I.save(index_path)
        
    def write_down(self, oh, a, b, d):
        oh.write(">\n")
        oh.write(d+"\n")
        a_title = self.load_card(a).split("\n")[0]
        b_title = self.load_card(b).split("\n")[0]
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
    
    def overview(self, regex=None, return_list=False):
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
            if not return_list:
                self.run_program(fn, "text")
        else:
            print("The index is empty")
        if return_list:
            return(fn)
    
    def edit(self, cid):
        if not cid:
            cid = input("Enter the id of the card to edit: ")
        self.run_program(self.load_card(cid, False), "editor")
        self.new_wrap(cid)
        
    def view(self, cid):
        if cid:
            self.run_program(self.load_card(cid, False), "viewer")
        else:
            cs = self.cards()
            for a in cs:
                with open(a, "r") as ih:
                    print(ih.read().split("\n")[0])

    @staticmethod
    def get_media(s):
        media = re.findall("@.+", s)
        media = [a.replace("@", "") for a in media]
        other_media = re.findall("!\[\]\(\S+\)", s)
        other_media = [a.replace("![](", "").replace(")", "") for a in other_media]
        media.extend(other_media)
        return(media)
        
    def show_media(self, fn):
        extension = op.splitext(fn)[-1].lower()
        if extension in [".jpg", ".png", ".jpeg", ".giff", ".tiff"]:
            self.run_program(fn, "images")
        elif extension in [".mp3", ".wav"]:
            self.run_program(fn, "audios")
        elif extension in [".mp4", ".avi", ".mkv"]:
            self.run_program(fn, "videos")
        elif extension in [".pdf", ".djvu", ".md"]:
            self.run_program(fn, "docs")
        elif extension in [".doc", ".docx", ".odt"]:
            self.run_program(fn, "word")
        
    def view_media(self, cid):
        if not cid:
            cid = input("Enter the id of the card to view media from: ")
        card = self.load_card(cid, True, as_is=True)
        fns = ExoCat.get_media(card)
        for fn in fns:
            print(fn)
            self.show_media(fn)
            input()
            
    def extract_section(self, text, section):
        try:
            if section == "full":
                return("\n".join(text))
            elif section == "title":
                return(text[0])
            else:
                section_start_line = list(
                    filter(lambda x: x.startswith(self.sections[section]), text)
                )
                all_section_starts = list(
                    filter(lambda x: text[x].startswith("## "), np.arange(len(text)))
                )
                if len(section_start_line) > 0:
                    section_start_line = section_start_line[0]
                else:
                    return("No such section")
                section_start = text.index(section_start_line)
                section_end = list(
                    filter(lambda x: x > section_start, all_section_starts)
                )[0]
                return("\n".join(text[section_start:section_end]))
        except Exception as E:
            print(E)
        
    def query(self, regex, section="full", open_newest=True, view_newest=True):
        files = self.cards()
        texts = []
        for i,a in tqdm(list(enumerate(files))):
            with open(a) as oh:
                try:
                    texts.append((i, oh.read().lower().split("\n")))
                except Exception as E:
                    print(E, a)
        texts = [(a[0], self.extract_section(a[1], section), a[1][0]) for a in texts]
        filtered = list(filter(lambda x: re.search(regex.lower(), x[1]), texts))
        filtered = [a[2].split("\n")[0] for a in filtered]
        print("\n")
        if len(filtered) > 0:
            for a in filtered:
                print(a)
            if open_newest:
                cid = filtered[-1].split(" ")[1][:-1]
                self.run_program(
                    self.load_card(cid, False), "editor"
                )
                self.new_wrap(cid)
            if view_newest:
                self.run_program(
                    self.load_card(filtered[-1].split(" ")[1][:-1], False), "viewer"
                )
        else:
            print("Not found")
        
        
def new_card(args):
    cat = ExoCat()
    cat.new(args.title, inherit=args.inherit)
    
def view_card(args):
    cat = ExoCat()
    cat.view(cat.get_card_id(args.card_id))
    
def edit_card(args):
    cat = ExoCat()
    cat.edit(cat.get_card_id(args.card_id))

def index_cards(args):
    cat = ExoCat()
    do_implicits = True if args.type in ["all", "implicits"] else False
    do_explicits = True if args.type in ["all", "implicits"] else False
    cat.index(do_implicits, do_explicits)
    
def query_cards(args):
    cat = ExoCat()
    cat.query(
        args.regex, section=args.section, 
        open_newest=args.open, view_newest=args.view
    )
    
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
    lb.study(args.catch_up, args.plot)
    lb.save(box_fn)

def random_card(args):
    cat = ExoCat()
    cards = cat.cards()
    random_card = np.random.choice(cards)
    print(random_card)
    cat.run_program(random_card, "editor")
    
def media_cards(args):
    cat = ExoCat()
    cat.view_media(cat.get_card_id(args.card_id))
    
def unfinished_cards(args):
    cat = ExoCat()
    unf_path = op.join(cat.config["folder"], "unfinished.pkl")
    if not op.exists(unf_path):
        with open(unf_path, "wb") as oh:
            pkl.dump({}, oh)
    with open(unf_path, "rb") as ih:
        unf_list = pkl.load(ih)
    if args.id:
        cid = cat.get_card_id(args.id)
        if cid not in unf_list:
            unf_list[cid] = args.comment if args.comment else ""
        else:
            del unf_list[cid]
        with open(unf_path, "wb") as oh:
            pkl.dump(unf_list, oh)
    else:
        for a in unf_list:
            print(cat.load_card(a, True).split("\n")[0]+" ==> "+unf_list[a])

def include_card(args):
    cat = ExoCat()
    if not args.merge:
        card_id = cat.new(args.file, run_editor=False)
        card = cat.load_card(card_id, contents=True, as_is=False)
        with open(args.file, "r") as ih:
            the_file = ih.read()
        out_card = card.replace(
                "## contents", 
                "## contents\n"+the_file.replace(
                    "# ", "### ",
                ).replace(
                    "## ", "#### "
                ).replace("### ", "##### ").replace("#### ", "###### ")
        )
        card_fn = cat.load_card(card_id, contents=False)
        with open(card_fn, "w") as oh:
            oh.write(out_card)
    else:
        card_id = cat.load_card(cat.get_card_id(args.merge), contents=False)
        tempfile = cat.make_tempfile()
        command = "diff -DVERSION1 "+card_id+" "+args.file+" > "+tempfile
        print(command)
        os.system(command)
        cat.run_program(tempfile, "editor")
        merge = False
        while not merge:
            r = input("Do the merge? [Y, n] ")
            if "Y" in r:
                merge = True
            elif "n" in r:
                break
        if merge:
            command2 = "cp "+tempfile+" "+card_id
            print(command2)
            os.system(command2)
            
def manage_ideas(args):
    cat = ExoCat()
    ideas_path = op.join(cat.config["folder"], "ideas.pkl")
    if not op.exists(ideas_path):
        with open(ideas_path, "wb") as oh:
            pkl.dump([], oh)
    with open(ideas_path, "rb") as ih:
        ideas_list = pkl.load(ih)
    if args.new:
        ideas_list.append(args.new)
        print("Added "+str(ideas_list.index(args.new))+": "+args.new)
    elif args.solve:
        print("Solved "+ideas_list.pop(int(args.solve)))
    else:
        for i,a in enumerate(ideas_list):
            print(str(i)+": "+a)
    with open(ideas_path, "wb") as oh:
        pkl.dump(ideas_list, oh)

def manage_orphans(args):
    cat = ExoCat()
    cards = [op.splitext(op.split(a)[-1])[0] for a in cat.cards()]
    overview = cat.overview(return_list=True)
    with open(overview, "r") as ih:
        linked = list(map(lambda x: re.findall("#\s[0-9]+", x), [a for a in ih]))
        linked = [a[0].split(" ")[-1] for a in list(filter(lambda x: len(x) == 1, linked))]
    orphans = set(cards) - set(linked)
    for a in orphans:
        fn = cat.load_card(a, contents=False)
        with open(fn, "r") as ih:
            print(ih.read().split("\n")[0])

def manage_keycards(args):
    cat = ExoCat()
    if args.keyword and args.card_id:
        if args.keyword not in cat.keycards:
            cat.keycards[args.keyword] = cat.get_card_id(args.card_id)
        else:
            del cat.keycards[args.keyword]
        cat.write_keycards()
    elif args.keyword and not args.card_id:
        del cat.keycards[args.keyword]
        cat.write_keycards()
    else:
        for a in cat.keycards:
            print(a+" --> "+cat.keycards[a])


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
        "-i", "--inherit", help="Inherit from a template card",
        default=None
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
        "-t", "--type", help="The link type",
        default="all", choices=["all", "explicits", "implicits"] 
    )
    parser_index.set_defaults(func=index_cards)
    parser_query = subparsers.add_parser(
        "query", help="Query the exocortex"
    )
    parser_query.add_argument(
        "-r", "--regex", help="The regular expression for the search"
    )
    parser_query.add_argument(
       "-s", "--section", help="This restricts the search for a certain section",
        choices=["title", "description", "contents", "questions", "answers", "full"],
        default="title"
    )
    parser_query.add_argument(
        "-o", "--open", help="Open the newest suitable file in the editor",
        action="store_true", default=False
    )
    parser_query.add_argument(
        "-v", "--view", help="Open the newest suitable file in the viewer",
        action="store_true", default=False
    )
    parser_query.set_defaults(func=query_cards)
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
    parser_study.add_argument(
        "-p", "--plot", help="Use the app to plot pictures",
        action="store", default=None
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
    parser_unfinished = subparsers.add_parser(
        "unfinished", help="Add or remove from the list of unfinished cards"
    )
    parser_unfinished.add_argument(
        "-i", "--id", help="The id of the card to work on",
        default=None
    )
    parser_unfinished.add_argument(
        "-c", "--comment", help="The comments",
        default=None
    )
    parser_unfinished.set_defaults(func=unfinished_cards)
    parser_include = subparsers.add_parser(
        "include", help="Include a suitable Markdown file into the exocortex",
    )
    parser_include.add_argument(
        "-f", "--file", help="The name of the file", default=None
    )
    parser_include.add_argument(
        "-m", "--merge", help="Merge with this card", default=None
    )
    parser_include.set_defaults(func=include_card)
    parser_idea = subparsers.add_parser(
        "idea", help="Manage ideas",
    )
    parser_idea.add_argument(
        "-n", "--new", help="Add a new idea to list"
    )
    parser_idea.add_argument(
        "-s", "--solve", help="Solve the idea"
    )
    parser_idea.set_defaults(func=manage_ideas)
    parser_orphan = subparsers.add_parser(
        "orphans", help="List orphan cards",
    )
    parser_orphan.set_defaults(func=manage_orphans)
    parser_keycard = subparsers.add_parser(
        "keycard", help="Manage keycard"
    )
    parser_keycard.add_argument(
        "-k", "--keyword", help="A keyword for a card", default=None
    )
    parser_keycard.add_argument(
        "-c", "--card-id", help="A card id for a keyword", default=None
    )
    parser_keycard.set_defaults(func=manage_keycards)
    args = parser.parse_args()
    args.func(args)
