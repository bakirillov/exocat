import re
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
from copy import deepcopy
from datetime import datetime

def version_0_5(f):
    with open(f, "r") as ih:
        data = ih.read()
    data = data.replace("[[", "#").replace("]]", "")
    with open(f, "w") as oh:
        oh.write(data)
                        
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="An Exocat migration script")
    parser.add_argument(
        "-p", "--path", help="path to the exocortex",
        default=None
    )
    parser.add_argument(
        "-v", "--version", help="version of exocat specification",
        default="0.5"
    )
    args = parser.parse_args()
    specifications = {"0.5": version_0_5}
    files = [op.join(args.path, "cards", a) for a in [a for a in os.walk(op.join(args.path, "cards"))][0][2]]
    files = list(filter(lambda x: op.splitext(x)[-1] == ".md", files))
    for a in files:
        specifications[args.version](a)