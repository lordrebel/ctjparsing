from abc import abstractmethod
import json
import os
import logging
from collections import defaultdict
from typing import Any
depth=0
class DeviceInfos:

    def __init__(self,raw:dict):
        self.id=raw["id"]
        self.name=raw["name"]
        self.totalGlobalMem=raw["totalGlobalMem"]
        self.computeCapability=f"{raw['computeMajor']}.{raw['computeMinor']}"
        self.maxThreadsPerBlock=raw["maxThreadsPerBlock"]
        self.maxThreadsPerMultiprocessor=raw["maxThreadsPerMultiprocessor"]
        self.regsPerBlock=raw["regsPerBlock"]
        self.regsPerMultiprocessor=raw["regsPerMultiprocessor"]
        self.warpsize=raw["warpSize"]
        self.sharedMemPerBlock=raw["sharedMemPerBlock"]
        self.sharedMemPerMultiprocessor=raw["sharedMemPerMultiprocessor"]
        self.numSms=raw["numSms"]
        self.sharedMemPerBlockOptin=raw["sharedMemPerBlockOptin"]

def print_dvice_infos(deviceInfo:DeviceInfos):
    attrs=[item for item in dir(deviceInfo) if not item.startswith("_")]
    for attr in attrs:
        print(f"{attr}:\t{getattr(deviceInfo,attr)}")


class TraceEvent:
    def __init__(self,data:dict) -> None:
        self.timestamp=data["ts"]
        self.duration=data["dur"]
        self.name=data["name"]
        self.timestamp_end=self.timestamp+self.duration
        self.infos=data
        self.subGroup=[]
        self.direct_corelations_idx=defaultdict(list)
        self.lower_cat_event_idx={}
    
    def accept(self,visitor:"VisitorBase",**kwargs):
        visitor.visit_event(self,**kwargs)

    def is_in(self,event:"TraceEvent"):
        if event.timestamp>=self.timestamp and self.timestamp_end>=event.timestamp_end:
            return True

    def add_to_subGroup(self,event:"TraceEvent")->bool:
        global depth
        depth+=1
        #print("depth:",depth,"name:",self.name," sub:",event.name)
        if not self.is_in(event):
            return False
        else:
            if len(self.subGroup)==0:
                self.subGroup.append(event)
            else:
                if not self.subGroup[-1].add_to_subGroup(event):
                    self.subGroup.append(event)
            return True
    
    def add_to_lower_cat_event_idx(self,cat_name,cat:list,idx:int)->bool:
        if not self.is_in(cat[idx]):
            return False
        else:
            if cat_name in self.lower_cat_event_idx:
                self.lower_cat_event_idx[cat_name].append(idx)
            else:
                self.lower_cat_event_idx[cat_name]=[idx]

            if len(self.subGroup)!=0:
                for sub_idx in range(len(self.subGroup)):
                    self.subGroup[sub_idx].add_to_lower_cat_event_idx(cat_name,cat,idx)
            return True

    def is_direct_corelation(self,cat_name,cat:list,idx:int):
        if "correlation"  not in cat[idx].infos["args"]:
            raise ValueError(f"cat:{cat_name},event:{cat[idx].infos} not correlationable!")
        if "correlation" in self.infos["args"]:
            return self.infos["args"]["correlation"] == cat[idx].infos["args"]["correlation"]
        else:
            return False
        
    def add_direct_corelations_idx(self,cat_name:str,cat:list,idx:int)->bool:
        if self.is_direct_corelation(cat_name,cat,idx):
            self.direct_corelations_idx[cat_name].append(idx)
            return True
        else:
            return False
    def get_duration(self):
        return self.duration

    def get_lower_cat_duration(self,cat:list,cat_name:str):
        if cat_name in self.lower_cat_event_idx:
            return sum([cat[idx].duration for idx in self.lower_cat_event_idx[cat_name]])
        else: return 0
        
    
    def get_corelations_durations(self,cat_name:str,cat:list,corelation_with_name:str = None,corelation_with:list=None):
        if  self.direct_corelations_idx[cat_name]:
            return sum( [cat[idx].duration for idx in self.direct_corelations_idx[cat_name]])
        else:
            if corelation_with is None or corelation_with_name is None:
                return 0

            if corelation_with_name in self.lower_cat_event_idx:
                return sum([ corelation_with[idx].get_corelations_durations(cat_name,cat) for idx in self.lower_cat_event_idx[corelation_with_name]])
            else:
                return 0

class EventFilterBase:
    def __init__(self) -> None:
        pass
    
    def __call__(self, cat_name:str,event:TraceEvent) -> bool:
        return True


class TraceCategories:
    def __init__(self,data:dict) -> None:
        for key in data.keys():
            setattr(self,key,data[key])
        self._cats=list(data.keys())
        self._merge_group_per_cat()

    def _merge_group_per_cat(self):
        for cat_name in self._cats:
            
            cat=getattr(self,cat_name)
            res=[cat[0]]
            i=1
            while(i<len(cat)):
                global depth
                depth=0
                if res[-1].add_to_subGroup(cat[i]):
                    pass
                else:
                    res.append(cat[i])
                i+=1
            setattr(self,cat_name,res)

    def add_direct_corelation(self,cat_name:str,corelation_with_name:str):
        cat=getattr(self,cat_name)
        corelation_with=getattr(self,corelation_with_name)
        cat_idx_total=0
        for idx in range(len(corelation_with)):
            cat_idx=cat_idx_total
            while(cat_idx<len(cat)):
                if corelation_with[idx].add_direct_corelations_idx(cat_name,cat,cat_idx):
                    cat_idx_total=cat_idx
                    break
                cat_idx+=1

        setattr(self,corelation_with_name,corelation_with)

    def add_lower_cat_event_idx(self,cat_name,lower_cat_name):
        cat=getattr(self,cat_name)
        lower_cat=getattr(self,lower_cat_name)
        lower_idx_total=0
        for idx in range(len(cat)):
            lower_idx=lower_idx_total
            while(lower_idx<len(lower_cat)):
                if cat[idx].add_to_lower_cat_event_idx(lower_cat_name,lower_cat,lower_idx):
                    lower_idx_total=lower_idx
                lower_idx+=1
        
def _parse_data_by_categroy(path:str,ignored_cats=[],ignored_phs=[],event_filter:EventFilterBase =None):
    devices=[]
    category=defaultdict(list)

    if not os.path.isfile(path):
        raise ValueError(f"path:{path} not a regular file")
    with open(path,"rt") as f:
        raw=json.load(f)
        devices=[DeviceInfos(item) for item in raw["deviceProperties"]]
        raw=[item for item in raw["traceEvents"] if item["ph"] not in ignored_phs]
        categories=set([item["cat"] for item in raw])
        categories=[item for item in categories if item not in ignored_cats]
        logging.info(f"total category:{categories}")
       
        for item in raw:
            if event_filter :
                candidate=TraceEvent(item)
                if event_filter(item["cat"],candidate):
                    category[item["cat"]].append(candidate)
            else:    
                category[item["cat"]].append(TraceEvent(item))
    return devices, TraceCategories(category)

class VisitorBase:
    def __init__(self) -> None:
        pass
    @abstractmethod
    def visit_cat(self,cat:list,cat_name:str,*args,**kwargs):
        pass
    
    @abstractmethod
    def visit_event(self,event:TraceEvent,*args,**kwargs):
        pass

class _DebugShowCatGroupTree(VisitorBase):
    def __init__(self,cats:TraceCategories) -> None:
        super().__init__()
        self._cats=cats
    def visit_event(self, event: TraceEvent, prefix=""):
        duration=event.duration
        cuda_comput_duration=event.get_corelations_durations("kernel",self._cats.kernel,"cuda_runtime",self._cats.cuda_runtime)
        print(f"name:{prefix+event.name}, wall duration:{duration/1000}ms, device duration:{cuda_comput_duration/1000}ms")
        if("cuda_runtime" in event.lower_cat_event_idx):
            cuda_apis={self._cats.cuda_runtime[idx].timestamp:self._cats.cuda_runtime[idx].name for idx in event.lower_cat_event_idx['cuda_runtime']}
            print(f"\t cuda apis:{cuda_apis}")
            kernel_called=[]
            for idx in event.lower_cat_event_idx['cuda_runtime']:
                for cidx in self._cats.cuda_runtime[idx].direct_corelations_idx["kernel"]:
                    kernel_called.append(self._cats.kernel[cidx].name)
            print(f"\t kernel:{kernel_called}")

        if event.subGroup:
            for item in event.subGroup:
                prefix+=event.name+"$$"
                item.accept(self,prefix=prefix)
    def visit_cat(self, cat: list, cat_name: str, *args, **kwargs):
        for event in cat:
            self.visit_event(event)
            print("-"*80)
    
class TraceDataHandler:
    def __init__(self,path:str,ignored_cats=[],ignored_phs=[],event_filter:EventFilterBase =None):
        self.devices,self.cats=_parse_data_by_categroy(path,ignored_cats,ignored_phs,event_filter)

class _DebugFilter(EventFilterBase):
    def __init__(self) -> None:
        super().__init__()
    def __call__(self, cat_name:str, event:TraceEvent) -> bool:
        if cat_name =="python_function":
            if str(event.name).startswith("nn.Module"):
                return True
            return False
        return True


if __name__ == "__main__":
    test=TraceDataHandler("/home/bigDisk2/jiahao/research/4PaModelTest/ocr_transformer_decode_parlance_batch_1/trace.json",
    ignored_cats=["Trace","async_cpu_to_gpu","user_annotation"],ignored_phs=["M","i","s","f","e"],event_filter=_DebugFilter())
    visitor=_DebugShowCatGroupTree(test.cats)
    test.cats.add_direct_corelation("kernel","cuda_runtime")
    test.cats.add_lower_cat_event_idx("cpu_op","cuda_runtime")
    visitor.visit_cat(test.cats.cpu_op,"cpu_op")
    

    