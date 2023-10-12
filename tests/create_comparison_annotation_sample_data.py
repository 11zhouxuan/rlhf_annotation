import pandas as pd
import json

path = "/Users/zhouxuan93/Documents/2023-08-24-35_questions_ziya_human_preferences/全部结果-35_questions_ziya_human_preferences.csv"
df = pd.read_csv(path)
data =  df.to_json(orient='records', lines=True)

to_save = [
    {
        'prompt':i['prompt'],
        'outputs':[i['system_52_2_iter_0'],i['system_52_2_iter_160']]
    } 
    for i in data
    ]

with open('/Users/zhouxuan93/projects/rlhf_annotation/data_sample/comparison_annotation.jsonl','w') as f:
    s = [json.dumps(d,ensure_ascii=False) for d in to_save]
    f.write('\n'.join(s))