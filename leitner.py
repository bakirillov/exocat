import os
import json
import time
import argparse
import numpy as np
import pandas as pd
import pickle as pkl
import os.path as op
from tqdm import tqdm
from copy import deepcopy
from datetime import datetime


class LeitnerBox():
    
    @classmethod
    def empty(C):
        pairs = {}
        ignore = []
        return(C(pairs, ignore))
    
    @staticmethod
    def load(fn):
        if op.splitext(fn)[-1] == ".pkl":
            with open(fn, "rb") as ih:
                o = pkl.load(ih)
                try:
                    len(o.ignore)
                except Exception as E:
                    print(E)
                    o.ignore = []
                return(o)
        else:
            c = LeitnerBox.empty()
            with open(fn, "r") as oh:
                for a in oh:
                    line = a.split("\t")
                    ans = line[1]
                    n = int(line[2])
                    time = datetime.fromtimestamp(int(line[3]))
                    c.pairs[line[0]] = (ans, n, time)
            return(c)
        
    def save(self, fn):
        if op.splitext(fn)[-1] == ".pkl":
            with open(fn, "wb") as oh:
                pkl.dump(self, oh)
        else:
            with open(fn, "w") as oh:
                for a in self.pairs:
                    line = a+"\t"+self.pairs[a][0]+"\t"+str(self.pairs[a][1])
                    line += "\t"+str(int(self.pairs[a][2].timestamp()))+"\n"
                    oh.write(line)
    
    @staticmethod
    def schedule(level):
        return(2**level)
    
    def __init__(self, pairs, ignore):
        self.pairs = pairs
        self.ignore = ignore
        
    @staticmethod
    def get_questions(file_contents):
        cs = [a.strip().lower() for a in file_contents.split("\n")]
        title = cs[0]
        try:
            if "## questions" in cs:
                qna = cs.index("## questions")
                cs = cs[qna+1:]
                ai = cs.index("## answers")
                q_s = list(filter(lambda x: len(x) > 0, cs[:ai]))
                a_s = list(filter(lambda x: len(x) > 0, cs[ai+1:]))
            else:
                return({})
        except Exception as e:
            return({})
        else:
            q2a = {q+" FROM "+title:a for q,a in zip(q_s, a_s)}
            a2q = {a+" FROM "+title:q for q,a in zip(q_s, a_s)}
            q2a.update(a2q)
            return(q2a)
                
    def index(self, files):
        for file in files:
            with open(file, "r") as ih:
                qa = LeitnerBox.get_questions(ih.read())
                qa = {a: (qa[a], 0, datetime.now()) for a in qa}
                intersecting_keys = set(self.pairs.keys()) & set(qa.keys())
                noint_qa = {}
                for a in qa:
                    if a not in intersecting_keys and a not in self.ignore:
                        noint_qa[a] = qa[a]
                self.pairs.update(noint_qa)
                
    def study_one(self, question):
        level = self.pairs[question][1]
        print("Your current level is "+str(level))
        if self.plot and "@" in question:
            os.system(self.plot+" "+question.split("@")[-1])
        a_hat = input(question+"\n")
        answer = self.pairs[question][0]
        print(answer+"\n")
        if self.plot and "@" in answer:
            os.system(self.plot+" "+answer.split("@")[-1])
        tm = datetime.now()
        while True:
            correct = input("Is the answer correct? (Y,n)\n").lower()
            if correct in ["y", "n"]:
                if correct == "y":
                    level += 1
                else:
                    level = 0
                print("Your current level is "+str(level)+"\n\n")
                break
        return(answer, level, tm, a_hat)
    
    def today(self):
        t = datetime.now()
        suitable = {}
        for question in self.pairs:
            answer, lv, qt = self.pairs[question]
            td = t-qt
            # print(td.seconds//3600, lv, times)
            if lv == 0:
                suitable[question] = (answer, lv, qt)
            else:
                # print(td.days % 2**lv, 2**lv, td.days+1, qt)
                if td.seconds//3600 > 10 and (td.days + 1) % 2**lv == 0:
             #       print(td.days % 2**lv)
                    suitable[question] = (answer, lv, qt)
        return(suitable)
    
    def study(self, catch_up=False, plot=None):
        suitable = self.today()
        keys = np.random.permutation(list(suitable.keys()))
        all_keys = len(keys)
        self.plot = plot
        if catch_up:
            keys = keys[0:25]
        print(str(len(keys))+" questions to study today. (Total is "+str(all_keys)+")\n\n")
        for i,k in enumerate(keys):
            print("Question#"+str(i+1))
            out = self.study_one(k)
            if out[3][0:2] == "D:":
                del self.pairs[k]
                print("Deleted "+k+"\n\n")
            elif out[3][0:2] == "I:":
                self.ignore.append(k)
                print("The following questions are ignored during the reindex and deleted:\n")
                for a in self.ignore:
                    print(a)
                del self.pairs[k]
                print("\n\n")
            elif out[3][0:2] == "A:":
                ans = deepcopy(self.pairs[k])
                self.pairs[k] = (out[3][2:], ans[1], ans[2])
                print("New answer is set\n")
                print(self.pairs[k])
            elif out[3][0:2] == "Q:":
                ans = deepcopy(self.pairs[k])
                del self.pairs[k]
                self.pairs[out[3][2:]] = ans
                print("New question is set\n")
                print(self.pairs[out[3][2:]], out[3][2:])
            else:
                self.pairs[k] = (out[0], out[1], out[2])
        
