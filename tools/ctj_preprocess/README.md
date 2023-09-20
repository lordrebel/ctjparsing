## ctj parser  (chrome tracing json Parser)工具集

### [filter_ctg.py](./filter_ctj.py)

过滤 ctj（chrome tracing json） 中的event。

#### 用法：

```shell

usage: filter_ctj.py [-h] [-s SOURCE] [-d DST] [-ic IGNORE_CAT] [-ip IGNORE_PHASE]

optional arguments:
  -h, --help            show this help message and exit
  -s SOURCE, --source SOURCE
                        the source json file
  -d DST, --dst DST     the destination json file
  -ic IGNORE_CAT, --ignore_cat IGNORE_CAT #需要删除的category 用 , 隔开
                        ignored category in json,using ',' to split
  -ip IGNORE_PHASE, --ignore_phase IGNORE_PHASE #需要删除的event phase 用 , 隔开
                        ignored event phase in json,using ',' to split
```

#### example

```shell

 ./filter_ctj.py  -s ../../../zhenqi_codes/code/blipv2_f16_batchsize16_batch_16.json/trace.json -d ./test_trace.json -ic "python_function,user_annotation" -ip "i,m"

```
