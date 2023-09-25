import os
import argparse
import csv
from typing import List
head_spliter="--------------------------------------------"
line_spliter="  "
def get_args():
    parser=argparse.ArgumentParser()
    parser.add_argument("-s","--src",required=True)
    parser.add_argument("-d","--dst",required=True)
    return parser.parse_args()

def line_filter(lines:List[str]):
    #find table
    min_idx=None
    max_idx=None
    lines=[item.strip() for item in lines if item.strip()]

    for idx,line in enumerate(lines):
        if line.startswith(head_spliter):
            if min_idx is None:
                min_idx=idx
            else:
                max_idx=idx
    return lines[min_idx+1:max_idx]

def write_results(file_path,head,lines):
    if not os.path.isdir(os.path.dirname(file_path)):
        os.makedirs(os.path.dirname(file_path))
    with open(file_path,"wt",newline="") as f:
        writer=csv.writer(f,quoting=csv.QUOTE_ALL)
        writer.writerow(head)
        for line in lines:
            writer.writerow(line)
    

def parse_line(line:str):
    line_list=line.split(line_spliter)
    line_list=[item.strip() for item in line_list if item.strip()]
    return line_list
def main():
    args=get_args()
    lines=None
    with open(args.src,"rt") as f:
        lines=f.read().split("\n")

    lines=line_filter(lines)
    head=None
    result_content=[]
    for item in lines:
        if item.startswith(head_spliter):
            continue
        if not head:
            head=parse_line(item)
        else:
            result_content.append(parse_line(item))
    write_results(args.dst,head,result_content)

if __name__ == "__main__":
    main()