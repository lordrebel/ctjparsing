#!/usr/bin/env python3
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(os.path.realpath(__file__))))
import base
import plot

def main():
    args=base.get_args()
    config= base.parse_config(args.config)
    data_processor=base.DataStatisticser(base.read_csv(args.src),
                                        config.statistic_targets,
                                        list(config.op_group.keys()))
    data_processor.process(config.op_group,args.keep_non_group_op)
    #write per op csv
    base.write_csv(os.path.join(args.dst,"per_op.csv"),
                    data_processor.datas,
                    [base.OP_NAME_HEAD]+data_processor.statistic_targets)
    #write group csv
    base.write_csv(os.path.join(args.dst,"op_groups.csv"),
                    data_processor.statistic_group,
                    [base.OP_NAME_HEAD,"count"]+data_processor.statistic_targets)

    #draw group plots
    for key in config.group_draw_targets+["count"]:
        file_name="group_"+str(key).replace(" ","_")+".png"
        labels=[]
        datas=[]
        for group in data_processor.statistic_group.keys():
            labels.append(group)
            datas.append(data_processor.statistic_group[group][key])
        plot.draw_pie(datas,labels,os.path.join(args.dst,file_name),key)
    
    #draw per op plots
    if args.plot_per_op:
        for key in config.per_op_draw_targets:
            file_name="per_op_"+str(key).replace(" ","_")+".png"
            labels=[]
            datas=[]
            for data in data_processor.datas:
                if key in data:
                    labels.append(data["name"].replace("$$","/")[-10:])
                    datas.append(data[key])
            if len(labels)>0:
                plot.draw_bins(datas,labels,os.path.join(args.dst,file_name),key)
        
        for key in config.per_op_draw_targets:
            file_name="sorted_per_op_"+str(key).replace(" ","_")+".png"
            labels=[]
            datas=[]
            if key  in data_processor.datas[0]:
                sorted_datas=sorted(data_processor.datas,key=lambda x:x[key],reverse=True)
                for data in sorted_datas:
                    if key in data:
                        labels.append(data["name"].replace("$$","/")[-10:])
                        datas.append(data[key])
                
                if len(labels)>0:
                    plot.draw_bins(datas,labels,os.path.join(args.dst,file_name),key)
        

if __name__ == "__main__":
    main()