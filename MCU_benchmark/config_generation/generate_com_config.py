import random
import os
import argparse
import numpy as np
import pdb
import json
import shutil
import copy
import time
import datetime
import asyncio
import re
import copy
import glob 
from openai import OpenAI

import yaml


def fetch_gpt4(query):
    print('fetching gpt4 ...')
    client = OpenAI(api_key='')
    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[query],
        temperature=0.7
    )
    res = completion.choices[0].message.content
    return res

def process_task_list(task_list):
            
    if len(task_list) == 3:
        connector1 = random.choice([' and ', ' or '])
        connector2 = random.choice([' and ', ' or '])
        result = task_list[0] + connector1 + task_list[1] + connector2 + task_list[2]
    elif len(task_list) == 2:
        # connector = random.choice([' and ', ' or '])
        connector = random.choice([' or '])
        result = task_list[0] + connector + task_list[1]
    else:
        result = task_list[0]
    
    
    
    return result


def generate_config(task_list):
    with open('composition_system_prompt.txt', 'r', encoding='utf-8') as file:  
        content = file.read()

    task_name = process_task_list(task_list)
    if not task_name:
        return 0, 0

    query = {
        "role": "user", "content": 
        content + 
        f'The task I want to complete: ' + task_name
        }

    ans = fetch_gpt4(query)
    print(ans)
    answer = {"role": "assistant", "content": f'{ans}'}

    return ans, task_name
    

with open('atomic_task_list.txt', 'r', encoding='utf-8') as f:
    lines = f.readlines()
keywords = ['circuit', 'redstone', 'repair', 'rename', 'combine']
tasks = [line.strip() for line in lines if line.strip() and not any(keyword in line.lower() for keyword in keywords)]

n = 10
for _ in range(n):
    sampled_tasks = random.sample(tasks, 2)

    print(sampled_tasks)

    res = {}
    ans, task_name = generate_config(sampled_tasks) 
    if ans==0:
        continue

    res['task'] = task_name
    res['ans'] = ans



    task_name = res['task'].replace(' ', '_').lower()
    init_commands = res.get('ans', [])  
    

    start_index = init_commands.find('- custom_init_commands:\n  -') 
    describe_index = init_commands.find('- Task description: ')
    thingking_index =  init_commands.find('- In order to')

    if start_index != -1:  
        custom_init_commands_text = init_commands[start_index + len('- custom_init_commands:\n  -'):].strip()  
        commands_list = [line.strip() for line in custom_init_commands_text.split('\n  -') if line.strip()] 
        print(commands_list) 
        print('\n')
    else:
        print('${task_name} can not find init_commands')

    config_dict = {}
    config_dict['text'] = init_commands[describe_index + len('- Task description: '):].strip().split('\n- ')[0]
    config_dict['custom_init_commands'] = commands_list
    config_dict['thinking'] = init_commands[thingking_index:].strip().split('\n- ')[0]

    save_path = './compose_config_new/'
    with open(save_path + f"{task_name}.yaml", 'w') as file:  
        yaml.dump(config_dict, file)











