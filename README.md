<!--
 * @Author: jiahao.wang jiahao.wang@montage-tech.com
 * @Date: 2023-09-07 10:14:01
 * @LastEditors: jiahao.wang
 * @LastEditTime: 2023-09-18 16:34:11
 * @Description: file content
-->
# profile_parser_main 使用说明

## 简介

本脚本用于解析 chrome-tracing 格式的json， 根据输入指定的需要监控的host侧event类别，host触发device 任务的event类别，device 侧执行任务的event 类别，输出解析结果（csv 格式）

## 输出格式

输出一共有这些 schema：   

1. name 监控的event的具体任务，注意由于host侧的同类别任务有调用栈的关系，因此会用`$$`表示层级的概念。 如：

  ```txt

    aten::conv2d
    aten::conv2d$$aten::convolution //aten::conv2d 的子任务，也就是在aten::conv2d执行过程中执行的任务
    aten::conv2d$$aten::convolution$$aten::_convolution //aten::convolution 的子任务
    aten::conv2d$$aten::convolution$$aten::_convolution$$aten::cudnn_convolution //aten::_convolution 的子任务
    aten::conv2d$$aten::convolution$$aten::_convolution$$aten::cudnn_convolution$$aten::empty //aten::cudnn_convolution 的子任务
  ```

  2. host duration(ms) 当前host 侧执行的任务的时间单位为毫秒
  3. device duration(ms) 当前event 根据 匹配上的`host触发device 任务的event` 找到的所有device 侧任务执行的时间和（注： 这里匹配指`host触发device 任务的event` 的 时间区间 包含于当前event）
  4. cuda launch duration(ms) :当前event 根据 匹配上的`host触发device 任务的event` 的所有执行时间
  5. cuda_runtime 当前event匹配上的 `host触发device 任务的event`以及其执行时间（匹配的定义见 3.）  
  6. kernels 当前event 根据 `host触发device 任务的event` 找到的 device侧触发的event以及其执行时间
  7. kernel infos：当前event 根据 `host触发device 任务的event` 找到的 device侧触发的event 的相关参数

## 使用方法：

```shell

 ./profile_parser_main.py -h
usage: profile_parser_main.py [-h] -s SRC -d DST [-hc HOST_CAT]
                              [-dc DEVICE_CAT] [-mc MONITOR_CAT]

optional arguments:
  -h, --help            show this help message and exit //输出帮助信息
  -s SRC, --src SRC     source json from torch profiler //profiler 产生的json文件路径
  -d DST, --dst DST     dist csv file //输出的csv 文件路径
  -hc HOST_CAT, --host_cat HOST_CAT
                        the category for launch device kernel //host侧launch device侧任务的 event 类别，默认是 cuda_runtime
  -dc DEVICE_CAT, --device_cat DEVICE_CAT 
                        device event catrgory //device 侧event 类别，默认为 kernel
  -mc MONITOR_CAT, --monitor_cat MONITOR_CAT  //host 侧需要监控的event 类别，默认为 python_function, 想输出aten 算子的相关信息的话需要 用 cpu_op
                        monitor evnet category
  --max_depth MAX_DEPTH
                        max depth of output events //输出的最大深度 默认为 -1 即都输出
  --min_depth MIN_DEPTH
                        min depth of output events //输出的最小深度 默认为 -1

```

## 例子

```shell
./profile_parser_main.py -s /home/bigDisk2/jiahao/research/4PaModelTest/ocr_transformer_decode_parlance_batch_1/trace.json -d ./aten_transformer.csv -mc cpu_op
```

## 建议

1. 建议用profiler 只record一次，这样的话会比较清晰

## :warning: 注意

1. :warning: 本脚本建立在这样一个假设下：`host触发device 任务的event` 都是独立的，没有子event或者调用栈，违反这一假设可能没法得到预期数据
2. :warning: device duration 时间没有包括device空闲时间
3. :warning: `host触发device 任务的event` 触发 的device侧任务的结束时间可能会超出当前监控的host侧event的时间区间，我们不会去检查和约束
4. :warning: 设置的`输出最大深度/最小深度`(max_depth/min_depth) 是闭区间


