## parse_torch_table

### 描述

将 torch profiler 输出的 table字符串转成csv文件

torch profile 的table字符串如下：

```txt

-------------------------------------------------------  ------------  ------------  ------------  ------------  ------------  ------------  ------------  ------------  ------------  ------------  ------------  ------------  ------------  ------------  --------------------------------------------------------------------------------  
                                                   Name    Self CPU %      Self CPU   CPU total %     CPU total  CPU time avg     Self CUDA   Self CUDA %    CUDA total  CUDA time avg       CPU Mem  Self CPU Mem      CUDA Mem  Self CUDA Mem    # of Calls                                                                      Input Shapes  
-------------------------------------------------------  ------------  ------------  ------------  ------------  ------------  ------------  ------------  ------------  ------------  ------------  ------------  ------------  ------------  ------------  --------------------------------------------------------------------------------  
                                          ProfilerStep*         3.49%      11.301ms       100.00%     323.578ms     323.578ms       0.000us         0.00%     322.599ms     322.599ms           0 b    -256.01 Kb           0 b     -20.48 Gb             1                                                                                []  
                                           aten::conv2d         0.00%       7.000us         0.06%     196.000us     196.000us       0.000us         0.00%       1.965ms       1.965ms           0 b           0 b     512.00 Mb           0 b             1                       [[1, 3, 1024, 1024], [128, 3, 3, 3], [128], [], [], [], []]  
                                      aten::convolution         0.00%       7.000us         0.06%     189.000us     189.000us       0.000us         0.00%       1.965ms       1.965ms           0 b           0 b     512.00 Mb           0 b             1               [[1, 3, 1024, 1024], [128, 3, 3, 3], [128], [], [], [], [], [], []]  
                                     aten::_convolution         0.00%      13.000us         0.06%     182.000us     182.000us       0.000us         0.00%       1.965ms       1.965ms           0 b           0 b     512.00 Mb           0 b             1  [[1, 3, 1024, 1024], [128, 3, 3, 3], [128], [], [], [], [], [], [], [], [], [],   
                                aten::cudnn_convolution         0.03%      83.000us         0.05%     155.000us     155.000us     707.000us         0.22%     709.000us     709.000us           0 b           0 b     512.00 Mb     511.99 Mb             1                  [[1, 3, 1024, 1024], [128, 3, 3, 3], [], [], [], [], [], [], []]  
                                       aten::contiguous         0.00%       2.000us         0.02%      61.000us      61.000us       0.000us         0.00%       2.000us       2.000us           0 b           0 b      13.50 Kb           0 b             1                                                              [[128, 3, 3, 3], []]  
                                            aten::clone         0.00%      10.000us         0.02%      59.000us      59.000us       0.000us         0.00%       2.000us       2.000us           0 b           0 b      13.50 Kb           0 b             1                                                              [[128, 3, 3, 3], []]  
                                       aten::empty_like         0.01%      20.000us         0.01%      26.000us      26.000us       0.000us         0.00%       0.000us       0.000us           0 b           0 b      13.50 Kb           0 b             1                                              [[128, 3, 3, 3], [], [], [], [], []]  
                                            aten::empty         0.11%     372.000us         0.11%     372.000us       2.696us       0.000us         0.00%       0.000us       0.000us     256.02 Kb     256.02 Kb       6.42 Gb       6.42 Gb           138                                                          [[], [], [], [], [], []]  
                                            aten::copy_         0.00%      13.000us         0.01%      23.000us      23.000us       2.000us         0.00%       2.000us       2.000us           0 b           0 b           0 b           0 b             1                                              [[128, 3, 3, 3], [128, 3, 3, 3], []]  
-------------------------------------------------------  ------------  ------------  ------------  ------------  ------------  ------------  ------------  ------------  ------------  ------------  ------------  ------------  ------------  ------------  --------------------------------------------------------------------------------  

```

### 使用说明

```shell
python3 parse_torch_table.py --help                             
usage: parse_torch_table.py [-h] -s SRC -d DST

optional arguments:
  -h, --help         show this help message and exit
  -s SRC, --src SRC #只包含 torch profile 的txt 文件
  -d DST, --dst DST # 输出csv 文件的路径
```

### example

```shell
python3 parse_torch_table.py -s ./sample.txt -d ./test.csv
```

## [third analysis tool](./3rd_anal)

### 描述

本三次分析工具基于[second_analysis](http://10.8.153.50:8081/customer_support/test_cases/blob/master/utils/calculate_second_analysis_result.py)的输出结果作为输入，根据 [config](./3rd_anal/config.json)进行数据统计,并生成相应的图表

### 使用说明

```shell

./3rd_anal/main.py --help                                                                               
usage: main.py [-h] -s SRC -d DST [-c CONFIG] [--keep_non_group_op] [--plot_per_op]

optional arguments:
  -h, --help            show this help message and exit
  -s SRC, --src SRC     the csv input file #输入csv文件，有二次分析脚本生成
  -d DST, --dst DST     the result folder path #输出文件夹（如果没有会自动创建）
  -c CONFIG, --config CONFIG 
                        the config file path #分析用的配置文件，默认为:3rd_anal/config.json
  --keep_non_group_op #flag 对于不在group中的算子，单独统计 （默认忽略）
  --plot_per_op #为统计目标绘制逐算子柱状图，默认不绘制

```

### 配置文件说明

```json

{   "op_groups":{ //算子分组，key为算子组别，value 为算子名称关键字列表，注意我们采用endsWith的方式进行关键字匹配

    "matmul&conv":["addmm", "matmul", "::mm", "$aten::bmm", "$aten::convolution"
        ],
    "reduce" : ["$aten::native_layer_norm",
                "$aten::layer_norm", 
                "$aten::native_group_norm", 
                "$aten::group_norm", 
                "mean", "cumsum"
            ],

    "index":["aten::index"],

    "attention":["_fmha", 
                "::flash_fwd", 
                "efficient_attention_forward_cutlass", 
                "$aten::scaled_dot_product_attention",
                "$aten::scaled_dot_product_attention"],

    "pointwise" :["aten::mul", 
                  "aten::add", 
                  "aten::sub", 
                  "add_", 
                  "aten::div", 
                  "aten::gelu", 
                  "aten::silu", 
                  "aten::relu", 
                  "$aten::softmax", 
                  "aten::sigmoid", 
                  "aten::exp", 
                  "tanh", 
                  "$aten::pow", 
                  "$aten::reciprocal", 
                  "aten::rsqrt", 
                  "$aten::abs", 
                  "aten::argmin"], 

    "memory" :["$aten::_to_copy", "$aten::clone",
                 "$aten::fill_",
                 "masked_fill_",
                 "new_ones", "$aten::zero_",
                 "$aten::contiguous",
                 "$aten::constant_pad_nd",
                 "aten::clamp",
                 "$aten::normal_", 
				 "aten::embedding",
				 "$aten::to"],

    "select_prefix":["aten::embedding"],

    "cast_prefix":["$aten::to"]     
    },
    "statistic_target":   //统计目标，即需要进行统计的，在输入的csv文件找哦你个存在的列
                    ["weight_shape",
                        "actual total latency",
                        "actual calcluate latency",
                        "actual memory latency",
                        "theoretical total latency(weight,parallel)",
                        "theoretical calcluate latency",
                        "theoretical memory latency(weight)",
                        "actual calcluate desity ratio(weight)",
                        "theoretical calcluate desity ratio(weight)",
                        "actual utilization(weight,parallel)",
                        "actual memory utilization(weight)"
                    ],
                    
    "group_draw_target": //需要按照算子分组绘制图（饼图）的统计目标
                    ["weight_shape", 
                    "actual total latency",
                    "theoretical total latency(weight,parallel)",
                    "actual calcluate desity ratio(weight)",
                    "theoretical calcluate desity ratio(weight)",
                    "actual utilization(weight,parallel)",
                    "actual memory utilization(weight)"],

    "per_op_draw_target":["weight_shape", //需要逐算子绘制图（柱状图）的统计目标
                            "actual total latency",
                            "theoretical total latency(weight,parallel)",
                            "actual calcluate desity ratio(weight)",
                            "theoretical calcluate desity ratio(weight)",
                            "actual utilization(weight,parallel)",
                            "actual memory utilization(weight)"]
}

```

:warning: 注意 *"per_op_draw_target"* 与 *"group_draw_target"* 应当为 *"statistic_target"* 的子集

### 结果文件说明

```shell
.
|-- group_<statistic_target>.png #针对需要按算子分组绘图的统计目标绘制的饼图
|-- group_count.png #当前模型算子分布情况（饼图）
|-- op_groups.csv #算子组统计目标的统计结果
|-- per_op.csv #从输入文件中根据统计目标筛选出的结果
|-- per_op_<statistic_target>.png #针对需要逐算子绘图的统计目标绘制的柱状图
`-- sorted_per_op_<statistic_target>.png #针对需要逐算子绘图的统计目标绘制的柱状图（按照从大到小排序）
```

### example

(绘制逐算子图)  

```shell
./3rd_anal/main.py -s ./3rd_anal/test_data/test_src.csv  -d  ./test_3rd/ --plot_per_op
```