import re
import os
import json
import time
import argparse
import pickle as pkl
import os.path as op
import networkx as nx
from tqdm import tqdm
from copy import deepcopy


class CatIndex():
    
    @classmethod
    def empty(C):
        g = nx.Graph()
        last = None
        return(C(g, last))
    
    @staticmethod
    def load(fn):
        with open(fn, "rb") as ih:
            return(pkl.load(ih))
        
    def __init__(self, g, last):
        self.g = g
        self.last = last
    
    @staticmethod
    def examine(s):
        explicits = re.findall("\[\[\w+\]\]", s)
        explicits = [a.replace("[[", "").replace("]]", "").lower() for a in explicits]
        s = {
            "explicits": explicits
        }
        return(s)
    
    def save(self, fn):
        with open(fn, "wb") as oh:
            pkl.dump(self, oh)
    
    def index(self, list_of_files):
        lst = sorted(
            deepcopy(list_of_files), 
            key=lambda x: int(op.split(x)[-1].replace(".md", ""))
        )
        if self.last:
            lst = lst[lst.index(self.last):]
        for a in tqdm(list_of_files):
            with open(a, "r") as ih:
                a_file = ih.read().lower()
            a_linkables = CatIndex.examine(a_file)
            a_cid = op.split(a)[-1].replace(".md", "")
            for b in lst:
                if a != b:
                    with open(b, "r") as ih:
                        b_file = ih.read()
                    b_linkables = CatIndex.examine(b_file)
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