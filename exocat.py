import os
import json
import time
import argparse
import os.path as op
from tqdm import tqdm
from datetime import datetime


class ExoCat():
    
    def __init__(self):
        with open("TEMPLATE.md", "r") as ih:
            self.template = ih.read()
        with open("config.json", "r") as ih:
            self.config = json.loads(ih.read())
        
    def new(self):
        cid = datetime.now().strftime("%d%m%Y%H%M%S")
        
        
    def index(self):
        pass
        


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-c", "--config",
        dest="config",
        action="store", 
        help="set config file", 
        default="default.json"
    )
    parser.add_argument(
        "-s", "--statistics",
        dest="statistics",
        action="store", 
        help="set destination for statistics", 
        default="statistics"
    )
    args = parser.parse_args()
    if not op.exists(args.statistics):
        os.makedirs(args.statistics)
    
    with open(args.config, "r") as ih:
        config = json.load(ih)