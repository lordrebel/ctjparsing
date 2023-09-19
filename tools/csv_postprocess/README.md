## ctj parser  (chrome tracing json Parser)工具集

### [keep_next_depth.py](./keep_next_depth.py)

#### 说明

对于有子级的event只保留子级event,对于没有子级的event保留当前event

#### 用法：

```shell

./tools/csv_postprocess/keep_next_depth.py --help     
usage: keep_next_depth.py [-h] -s SOURCE

optional arguments:
  -h, --help            show this help message and exit
  -s SOURCE, --source SOURCE
```

`-s`    输入由 [profile_parser_main.py](../../profile_parser_main.py) 生成的csv路径

处理完后会在 `-s` 输入的路径的文件夹下生成结果文件，文件命名格式为 “knd_res_<source文件名>.csv”

#### example

```
python ../../../ctjparsing/tools/csv_postprocess/keep_next_depth.py -s ./test_raw_blip2_bf16.csv
```