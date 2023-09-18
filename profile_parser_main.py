#!/usr/bin/env python3
import argparse
import os
import torch_profiler_parser as tpp

def get_args():
    parser=argparse.ArgumentParser()
    parser.add_argument("-s","--src",type=str,required=True,help="source json from torch profiler")
    parser.add_argument("-d","--dst",type=str,required=True,help="dist csv file ")
    parser.add_argument("-hc","--host_cat",type=str,required=False,default="cuda_runtime",help="the category for launch device kernel")
    parser.add_argument("-dc","--device_cat",type=str,default="kernel",required=False,help="device enveny catrgory")
    parser.add_argument("-mc","--monitor_cat",type=str,default="python_function",required=False,help="monitor evnet category")
    parser.add_argument("--max_depth",type=int,default=-1,required=False,help="max depth of output events")
    parser.add_argument("--min_depth",type=int,default=-1,required=False,help="min depth of output events")
    return parser.parse_args()

def main():
    args=get_args()

    dist_dir=os.path.dirname(args.dst)
    if not os.path.isdir(dist_dir):
        os.makedirs(dist_dir)
    if args.max_depth<args.min_depth:
        raise ValueError("invalid args for depth")
    
    parser=tpp.TorchProfilerParser(args.src,
                                    args.dst,
                                    args.device_cat,
                                    args.host_cat,
                                    args.monitor_cat,
                                    max_depth=args.max_depth,
                                    min_depth=args.min_depth)
    parser.process()


if __name__ == "__main__":
    main()