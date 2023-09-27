import matplotlib.pyplot as plt
import matplotlib as mtl
import math

def filter_illegal_data(datas,labels):
    res_datas=[]
    res_labels=[]
    for idx,data in enumerate(datas):
        if math.isnan(data) or math.isinf(data):
            continue
        else:
            res_datas.append(data)
            res_labels.append(labels[idx])
    return res_datas,res_labels
def draw_pie(datas,labels,file_path,title=None):

    datas,labels=filter_illegal_data(datas,labels)
    plt.rcParams['axes.unicode_minus']=False
    plt.figure(figsize=(20, 20))
    persent=[item*100./sum(datas) for item in datas]
    show_labels = ['{0} - {1:1.2f} %'.format(i,j) for i,j in zip(labels, persent)]
    
    patches,texts=plt.pie(
                x=datas,   # 值
                shadow=True,
                explode = [0.2]+[0.1]*(len(datas)-1)
                )
    patches, show_labels, _ =  zip(*sorted(zip(patches, show_labels, datas),
                                          key=lambda x: x[2],
                                          reverse=True))
    if title: plt.title(title,fontsize=28,fontweight="heavy")
    plt.legend(patches, show_labels, loc='center left', bbox_to_anchor=(-0.1, 1.),
           fontsize=18)
    plt.savefig(file_path)

def draw_bins(datas,labels,file_path,title=None,xlabel=None,ylabel=None):
    datas,labels=filter_illegal_data(datas,labels)
    plt.rcParams['axes.unicode_minus']=False
    plt.figure(figsize=(max(min(len(labels)/100,20.48),6.4), 6.4),dpi=100)
    plt.bar(labels,datas, width=0.8,align="center")
    plt.xticks(size="small",rotation=60)
    if title: plt.title(title,fontsize=16,fontweight="heavy")
    if xlabel: plt.xlabel(xlabel)
    if ylabel: plt.ylabel(ylabel)

    plt.savefig(file_path)
    



