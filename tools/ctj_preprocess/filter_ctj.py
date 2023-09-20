#!/usr/bin/env python3
import json
import argparse
import os

def get_args():
    parser=argparse.ArgumentParser()
    parser.add_argument("-s","--source",type=str,help="the source json file")
    parser.add_argument("-d","--dst",type=str, help="the destination json file ")
    parser.add_argument("-ic","--ignore_cat",type=str,default="",help="ignored category in json,using ',' to split")
    parser.add_argument("-ip","--ignore_phase",type=str,default="",help="ignored event phase in json,using ',' to split")
    return parser.parse_args()

def check_args(args):
    if not os.path.isfile(args.source):
        raise ValueError(f"cannot find file path:{args.source}")
    
    dist_dir=os.path.dirname(args.dst)
    if not os.path.isdir(dist_dir):
        os.makedirs(dist_dir)
    
    args.ignore_cat=args.ignore_cat.split(",")
    args.ignore_cat=[item.strip() for item in args.ignore_cat if len(item.strip())>0]

    args.ignore_phase=args.ignore_phase.split(",")
    args.ignore_phase=[item.strip() for item in args.ignore_phase if len(item.strip())>0]
    return args

def main():
    args=check_args(get_args())
    raw={}
    with open(args.source,"rt") as f:
        raw=json.load(f)
    
    events=raw["traceEvents"]
    events=[item for item in events if item["ph"] not in args.ignore_phase ]
    events=[item for item in events if "cat" not in item or item["cat"] not in args.ignore_cat ]
    raw["traceEvents"]=events
    with open(args.dst,"wt") as f:
        json.dump(raw,f)

if __name__ == "__main__":
    main()