'''
Author: jiahao.wang jiahao.wang@montage-tech.com
Date: 2023-09-06 17:38:07
LastEditors: jiahao.wang
LastEditTime: 2023-09-13 11:40:40
Description: file content
'''
import csv
from .profilerBase import VisitorBase,TraceDataHandler,TraceCategories,EventFilterBase,TraceEvent,print_dvice_infos

class TorchFilter(EventFilterBase):
    def __init__(self) -> None:
        super().__init__()
    def __call__(self, cat_name:str, event:TraceEvent) -> bool:
        if cat_name =="python_function":
            if str(event.name).startswith("nn.Module"):
                return True
            return False
        return True

class CsvWriterVisitor(VisitorBase):
    def __init__(self,
                 f,
                 cats:TraceCategories,
                 host_launch_cat_name:str,
                 device_cat_name:str,
                 max_depth:int =-1,
                 min_depth:int=-1) -> None:
        super().__init__() 
        self.header=["name","args","host duration(ms)","device duration(ms)","cuda launch duration(ms)","cuda_runtime","kernels","kernel infos"]
        self.writer=csv.writer(f,quoting=csv.QUOTE_ALL)
        self.writer.writerow(self.header)
        self._cats=cats
        self.host_launch_cat_name=host_launch_cat_name
        self.device_cat_name=device_cat_name
        self.max_depth=max_depth
        self.min_depth=min_depth

        
    def visit_event(self, event: TraceEvent, prefix="",current_depth=-1):
        
        row=["","","","","","","",""]
        row[0]=prefix+event.name
        row[1]=str(event.infos["args"]) if "args" in event.infos else ""
        row[2]=event.duration/1000
        
        row[3]=event.get_corelations_durations(
                            self.device_cat_name,
                            getattr(self._cats,self.device_cat_name),
                            self.host_launch_cat_name,getattr(self._cats,self.host_launch_cat_name))/1000
        
        row[4]=event.get_lower_cat_duration(getattr(self._cats,self.host_launch_cat_name),self.host_launch_cat_name)/1000
        
        if(self.host_launch_cat_name in event.lower_cat_event_idx):
            host_launch_idxs=event.lower_cat_event_idx[self.host_launch_cat_name]
            host_launch_events=[getattr(self._cats,self.host_launch_cat_name)[idx] for idx in host_launch_idxs]
            host_launch_time=[str({item.name:item.duration/1000}) for item in host_launch_events]
            row[5]=",".join(host_launch_time)
            kernel_called=[]
            kernel_infos=[]
            device_total_events=getattr(self._cats,self.device_cat_name)
            for launch_event in host_launch_events:
                for cidx in launch_event.direct_corelations_idx[self.device_cat_name]:
                    kernel_called.append(str({device_total_events[cidx].name:
                                        device_total_events[cidx].duration/1000}))
                    kernel_infos.append(str({device_total_events[cidx].name:
                                        device_total_events[cidx].infos["args"]}))
            row[6]=",".join(kernel_called)
            row[7]=",".join(kernel_infos)
        
        if self.max_depth!=-1 :
            if current_depth<self.min_depth or current_depth>self.max_depth:
                pass
            else:
                self.writer.writerow(row)
        else:
            self.writer.writerow(row)

        if event.subGroup:
            for item in event.subGroup:
                cur_prefix= prefix+event.name+"$$"
                item.accept(self,prefix=cur_prefix,current_depth=current_depth+1)
    
    def visit_cat(self, cat: list, cat_name: str, *args, **kwargs):
        for event in cat:
            self.visit_event(event,current_depth=1)

class TorchProfilerParser:
    def __init__(self,
                src_path:str,
                dist_path:str,
                device_cat_name:str ="kernel",
                host_launch_cat_name:str ="cuda_runtime",
                profiler_cat="python_function",
                ignored_cats=["Trace","async_cpu_to_gpu","user_annotation"],
                ignored_phs=["M","i","s","f","e"],
                max_depth=-1,
                min_depth=-1
                ) -> None:
        self.data=TraceDataHandler(src_path,
                                    ignored_cats,
                                    ignored_phs,
                                    event_filter=TorchFilter())
        
        self.dist_path=dist_path
        self.device_cat_time=device_cat_name
        self.host_launch_time=host_launch_cat_name
        self.profilter_cat_name=profiler_cat
        self.data.cats.add_direct_corelation(self.device_cat_time,self.host_launch_time)
        self.data.cats.add_lower_cat_event_idx(self.profilter_cat_name,self.host_launch_time)
        self.max_depth=max_depth
        self.min_depth=min_depth

    def process(self):
        print("-"*80)
        for device in self.data.devices:
            print_dvice_infos(device)
        print("-"*80)

        with open(self.dist_path,"wt",newline="") as f:
            visitor=CsvWriterVisitor(f,self.data.cats,self.host_launch_time,self.device_cat_time,self.max_depth,self.min_depth)
            profiler_cat=getattr(self.data.cats,self.profilter_cat_name)
            visitor.visit_cat(profiler_cat,self.profilter_cat_name)
            
            
    