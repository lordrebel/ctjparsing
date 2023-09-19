#!/usr/bin/env python3
import os
import csv
import argparse

def get_args():
    parser=argparse.ArgumentParser()
    parser.add_argument("-s","--source",type=str,required=True)
    return parser.parse_args()

def main():
    args=get_args()
    if not os.path.isfile(args.source):
        raise ValueError(f"error! cannot found file named:{args.source}")
    
    res_file=os.path.join(os.path.dirname(args.source),"knd_res_"+os.path.basename(args.source))
    raw=[]
    head=None
    with open(args.source,"rt") as source:
        reader=csv.reader(source)
        for row in reader:
            raw.append(row)
        head=raw[0]
        raw=raw[1:]
    
    res=[]

    line_idx=0
    while(line_idx<len(raw)):
        res.append(raw[line_idx])
        offset=1
        tmp=[]
        while(line_idx+offset<len(raw)):
            if(str(raw[line_idx+offset][0]).strip().startswith(res[-1][0]+"$$")):
                tmp.append(raw[line_idx+offset]) 
                offset+=1   
            else:
                break
        if tmp:
            res=res[:-1]
            res.extend(tmp)

        line_idx+=len(tmp)+1
    
    with open(res_file,"wt",newline="") as dst:
        writer=csv.writer(dst)
        writer.writerow(head)
        for line in res:
            writer.writerow(line)
            
if __name__ == "__main__":
    main()




        