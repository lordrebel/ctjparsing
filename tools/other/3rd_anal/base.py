
import argparse
import os
import csv
import json
from collections import defaultdict
from typing import Dict, List, Union
from algo import special_target
CURRENT_ROOT=os.path.dirname(os.path.abspath(os.path.realpath(__file__)))
OP_NAME_HEAD="name"


def select_op_group(op_groups:Dict[str,List[str]],data):
    for group in op_groups.keys():
        group_ops=op_groups[group]
        for candidate_op in group_ops:
            if str(data[OP_NAME_HEAD]).strip().lower().endswith(candidate_op.strip().lower()):
                return group
    return data[OP_NAME_HEAD]
  
def get_args():
    parser=argparse.ArgumentParser()
    parser.add_argument("-s","--src",
                            required=True,
                            type=str,
                            help="the csv input file")
    parser.add_argument("-d","--dst",
                            required=True,
                            type=str,
                            help="the result folder path")
    parser.add_argument("-c","--config",
                            required=False,
                            type=str,
                            default=os.path.join(CURRENT_ROOT,"config.json"),
                            help="the config file path")
    parser.add_argument("--keep_non_group_op",action="store_true",default=False)
    parser.add_argument("--plot_per_op",action="store_true",default=False)

    args=parser.parse_args()
    if not os.path.isdir(args.dst):
        os.makedirs(args.dst)
    return args


class ParserConfig:
    def __init__(self,path:str):
        with open(path,"rt") as f:
            raw=json.load(f)
            self.op_group=raw["op_groups"]
            self.statistic_targets=raw["statistic_target"]
            self.group_draw_targets=raw["group_draw_target"]
            self.per_op_draw_targets=raw["per_op_draw_target"]

class DataStatisticser:
    def __init__(self,datas,statistic_targets:list,groups:list) -> None:
        self.statistic_targets=statistic_targets
        self.datas=self.__handle_datas(datas)
        self.statistic_group={item:defaultdict(float) for item in groups}
    def __handle_datas(self,datas):
        res=[]
        for data in datas:
            tmp={}
            tmp[OP_NAME_HEAD]=data[OP_NAME_HEAD]
            for target in self.statistic_targets:
                #for the target that need we calc
                if target not in data and target in special_target:
                    continue
                tmp[target]=eval(data[target])
            res.append(tmp)
        return res


    def process(self,group_infos:Dict[str,List[str]],keep_non_group_op=False):
        for data in self.datas:
            group_name=select_op_group(group_infos,data)
            if group_name == data[OP_NAME_HEAD]:
                if not keep_non_group_op:
                    continue
            
            if group_name in self.statistic_group:
                for key in self.statistic_targets:
                    #for the target that need we calc
                    if key not in data and key in special_target:
                        continue
                    self.statistic_group[group_name][key]+=data[key]
                self.statistic_group[group_name]["count"]+=1
            else:
                self.statistic_group[group_name]={}
                for key in self.statistic_targets:
                    #for the target that need we calc
                    if key not in data and key in special_target:
                        continue
                    self.statistic_group[group_name][key]=data[key]
                self.statistic_group[group_name]["count"]+=1
        
        #handle special target:
        for spec in special_target.keys():
            handle_func=special_target[spec]
            for group in self.statistic_group.keys():
                    self.statistic_group[group][spec]=handle_func(self.statistic_group[group])
        
                
def parse_config(path):
    return ParserConfig(path)
    

def read_csv(file_path:str):
    with open(file_path,"rt") as f:
        res=[]
        reader=csv.DictReader(f)
        for data in reader:
            res.append(data)
    return res

def write_csv(file_path:str,datas:Union[Dict[str,Dict],List[Dict]],heads:list):
    with open(file_path,"wt",newline="") as f:
        writer=csv.writer(f,quoting=csv.QUOTE_ALL)
        writer.writerow(heads)

        if isinstance(datas,list):
            for data in datas:
                row=[]
                for key in heads:
                    if key in data.keys():
                        row.append(data[key])
                    else:
                        row.append("N/A")
                writer.writerow(row)

        elif isinstance(datas,dict):
            for group_name in datas.keys():
                row=[]
                for key in heads[1:]:
                    row.append(datas[group_name][key])
                row=[group_name]+row

                writer.writerow(row)

