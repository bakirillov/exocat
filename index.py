import re
import os
import json
import time
import nltk
import argparse
import wordfreq
import pymorphy2
import pickle as pkl
import os.path as op
import networkx as nx
from tqdm import tqdm
from copy import deepcopy
from stop_words import get_stop_words


class CatIndex():
    
    ru = pymorphy2.MorphAnalyzer()
    en_linkable = ["NN", "VB"]
    ru_linkable = ["NOUN", "VERB"]
    en_stops = get_stop_words('en')
    ru_stops = get_stop_words('ru')
    
    @classmethod
    def empty(C):
        g = nx.Graph()
        last = None
        zf = 3
        return(C(g, last, zf))
    
    @staticmethod
    def load(fn):
        with open(fn, "rb") as ih:
            return(pkl.load(ih))
        
    def __init__(self, g, last, zipf_frequency):
        self.g = g
        self.last = last
        self.zf = zipf_frequency
    
    @staticmethod
    def examine(s, szf, do_implicits=False, do_explicits=True):
        explicits = []
        if do_explicits:
            explicits = re.findall("#\w+", s)
            explicits = [a.replace("#", "").lower() for a in explicits]
        implicits = []
        if do_implicits:
            ss = "\n".join(
                list(
                    filter(
                        lambda x: "#" not in x and "_" not in x and not re.match("'.+'", x), 
                        s.split("\n")
                    )
                )
            )
            spl = list(
                filter(
                    lambda x: re.match(
                        "\w+", x
                    ) and x not in CatIndex.en_stops and x not in CatIndex.ru_stops and len(x) > 2, 
                    re.split("\s", ss)
                )
            )
            for a in spl:
                ru = CatIndex.ru.parse(a)
                for b in ru:
                    for c in CatIndex.ru_linkable:
                        if str(b.tag).startswith(c):
                            zf = wordfreq.zipf_frequency(a, 'ru')
                            if zf <= szf:
                                implicits.append(a)
                try:
                    en = nltk.pos_tag([a])
                except:
                    pass
                else:
                    for b in en:
                        for c in CatIndex.en_linkable:
                            if b[1].startswith(c):
                                zf = wordfreq.zipf_frequency(a, 'en')
                                if zf <= szf:
                                    implicits.append(a)
        r = {
            "explicits": explicits, "implicits": implicits
        }
        return(r)
    
    def save(self, fn):
        with open(fn, "wb") as oh:
            pkl.dump(self, oh)
    
    def index(self, list_of_files, do_implicits=False, do_explicits=True):
        lst = sorted(
            deepcopy(list_of_files), 
            key=lambda x: int(op.split(x)[-1].replace(".md", ""))
        )
        if self.last:
            lst = lst[lst.index(self.last):]
        for a in tqdm(list_of_files):
            with open(a, "r") as ih:
                a_file = ih.read().lower()
            a_linkables = CatIndex.examine(a_file, self.zf, do_implicits, do_explicits)
            a_cid = op.split(a)[-1].replace(".md", "")
            for b in lst:
                if a != b:
                    with open(b, "r") as ih:
                        b_file = ih.read()
                    b_linkables = CatIndex.examine(b_file, self.zf, do_implicits, do_explicits)
                    ebunch = {}
                    add_edge = False
                    for c in b_linkables:
                        ints = list(
                            set(a_linkables[c]).intersection(set(b_linkables[c]))
                        )
                        if len(ints) > 0:
                            add_edge = True
                            ebunch[c] = ",".join(ints)
                        else:
                            add_edge = False
                        if add_edge:
                            b_cid = op.split(b)[-1].replace(".md", "")
                            self.g.add_edges_from([(a_cid, b_cid, ebunch)])
