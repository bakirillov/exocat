import os
import json
import time
import argparse
import numpy as np
import pandas as pd
import pickle as pkl
from tqdm import tqdm
from datetime import datetime


class LeitnerBox():
    
    @classmethod
    def empty(C):
        pairs = {}
        return(C(pairs))
    
    @staticmethod
    def load(fn):
        with open(fn, "rb") as ih:
            return(pkl.load(ih))
        
    def save(self, fn):
        with open(fn, "wb") as oh:
            pkl.dump(self, oh)
    
    @staticmethod
    def schedule(level):
        return(2**level)
    
    def __init__(self, pairs):
        self.pairs = pairs
        
    @staticmethod
    def get_questions(file_contents):
        cs = file_contents.split("\n")
        if "## Questions" in cs:
            qna = cs.index("## Questions")
            cs = cs[qna+1:]
            ai = cs.index("## Answers")
            q_s = list(filter(lambda x: len(x) > 0, cs[:ai]))
            a_s = list(filter(lambda x: len(x) > 0, cs[ai+1:]))
            return({q:a for q,a in zip(q_s, a_s)})
        else:
            return({})
        
    def index(self, files):
        for file in files:
            with open(file, "r") as ih:
                qa = LeitnerBox.get_questions(ih.read())
                qa = {a: (qa[a], 0, datetime.now(), 0) for a in qa}
                intersecting_keys = set(self.pairs.keys()) & set(qa.keys())
                noint_qa = {}
                for a in qa:
                    if a not in intersecting_keys:
                        noint_qa[a] = qa[a]
                self.pairs.update(noint_qa)
                
    def study_one(self, question):
        _ = input(question)
        answer = self.pairs[question][0]
        print(answer+"\n")
        level = 0
        times = self.pairs[question][-1]
        tm = datetime.now()
        while True:
            correct = input("Is the answer correct? (Y,n)\n")
            if correct in ["Y", "n"]:
                level += 1
                break
        return(answer, level, tm, times)
    
    def today(self):
        t = datetime.now()
        suitable = {}
        for question in self.pairs:
            answer, lv, qt, times = self.pairs[question]
            td = t-qt
            if td.days > 0:
                self.pairs[question] = (answer, lv, qt, 0)
            if td.days % 2**lv == 0:
                if times == 0:
                    suitable[question] = (answer, lv, qt, times)
            self.pairs[question] = (answer, lv, qt, times+1)
        return(suitable)
    
    def study(self):
        suitable = self.today()
        keys = np.random.permutation(list(suitable.keys()))
        print(str(len(keys))+" questions to study today.")
        for i,k in enumerate(keys):
            print("Question#"+str(i+1))
            self.pairs[k] = self.study_one(k)
            print(suitable)