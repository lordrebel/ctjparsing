import numpy as np
def calc_actual_weight_calcluate_desity_ratio(data):
    return np.divide(data["actual calcluate latency"] ,(data["actual memory latency"]))

def calc_theoretical_weight_calcluate_desity_ratio(data):
    return np.divide(data["theoretical calcluate latency"] , (data["theoretical memory latency(weight)"]))

def calc_actual_weight_parallel_utilization(data):
    return np.divide(data["theoretical total latency(weight,parallel)"],(data["actual total latency"]))

def calc_weight_actual_memory_utilization(data):
    return np.divide(data["theoretical memory latency(weight)"] , (data["actual memory latency"]))

special_target={
    "actual calcluate desity ratio(weight)":calc_actual_weight_calcluate_desity_ratio,
    "theoretical calcluate desity ratio(weight)":calc_theoretical_weight_calcluate_desity_ratio,
    "actual utilization(weight,parallel)":calc_actual_weight_parallel_utilization,
    "actual memory utilization(weight)":calc_weight_actual_memory_utilization,
}