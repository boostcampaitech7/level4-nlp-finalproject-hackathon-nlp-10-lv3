import os
import re
import json
import time

import pandas as pd
from openai import OpenAI

from utils.util import load_yaml


class CourseEvaulator():
    def __init__(
            self,
            api_key,
            model="gpt-4o",
            max_tokens=512,
            temperature=0,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
            stop=None,
            logprobs=True,
            top_logprobs=10,
            n=1,
    ):
        self.api_key = api_key
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.top_p = top_p
        self.frequency_penalty = frequency_penalty
        self.presence_penalty = presence_penalty
        self.stop = stop
        self.logprobs = logprobs
        self.top_logprobs = top_logprobs
        self.n = n

    def make_request(self, id, sys_prmpt, usr_prmpt):
        return {
            'custom_id': f"{id}",
            'method': 'POST',
            'url': "/v1/chat/completions",
            'body': {
                'model': self.model,
                'messages': [
                    {"role": "system", "content": sys_prmpt},
                    {"role": "user", "content": usr_prmpt}
                ],
                'max_tokens': self.max_tokens,
                'temperature': self.temperature,
                'top_p': self.top_p,
                'frequency_penalty': self.frequency_penalty,
                'presence_penalty': self.presence_penalty,
                'stop': self.stop,
                'logprobs': self.logprobs,
                'top_logprobs': self.top_logprobs,
                'n': self.n,
            }
        }

    def make_requests(self, sys_prmpt, usr_prmpts):
        return [self.make_request(id, sys_prmpt, usr_prmpt) for id, usr_prmpt in enumerate(usr_prmpts)]

    def save_requests(self, sys_prmpt, usr_prmpts, file_path):
        self.file_path = file_path
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        requests = self.make_requests(sys_prmpt, usr_prmpts)
        with open(file_path, "w") as f:
            for request in requests:
                f.write(json.dumps(request) + "\n")

    def create_batch(self):
        if not os.path.exists(self.file_path):
            print("Requests does not exists.")
            print("You need to do '.save_requests()' first.")
            return False

        self.client = OpenAI(api_key=self.api_key)
        batch_input_file = self.client.files.create(
            file=open(self.file_path, "rb"),
            purpose="batch"
        )
        self.batch_job = self.client.batches.create(
            input_file_id=batch_input_file.id,
            endpoint="/v1/chat/completions",
            completion_window="24h"
        )
        return True
    
    def evaluate(self):
        fail_cnt = 0
        if not self.create_batch():
            return
        while True:
            batches = self.client.batches.list().data[0]
            status = batches.status
            if status == "validating":
                print("Validating the inputs")
                while status == "validating":
                    time.sleep(5)
                    status = self.client.batches.list().data[0].status
            elif status == "in_progress":
                print(f"{batches.request_counts.completed}/{batches.request_counts.total}")
                while status == "in_progress":
                    time.sleep(60)
                    status = self.client.batches.list().data[0].status
            elif status == "finalizing":
                print("Finalizing the process")
                while status == "in_progress":
                    time.sleep(30)
                    status = self.client.batches.list().data[0].status
            elif status == "completed":
                print(f"{batches.request_counts.completed}/{batches.request_counts.total}")
                print("Request is successfully done")
                break
            elif status == "failed":
                print(f"The API calling is failed {fail_cnt}-times")
                if fail_cnt > 5:
                    print("[STOP] More than 5 failure.")
                    break
                print("Try again after 1-min")
                time.sleep(60)
                print("Try")
                self.create_batch()
            elif status == "expired":
                print("The process is expired, because it is not finished in 24hours")
                break
            else:
                print("The process is canceled")
                break

    def get_raw_results(self):
        result_file_id = self.client.batches.retrieve(self.batch_job.id).output_file_id
        results = self.client.files.content(result_file_id).content.decode('utf-8')
        return [json.loads(line)["response"]["body"]["choices"][0]["message"]["content"]
                for line in results.split('\n') if line]

    def get_results(self):
        raw_results = self.get_raw_results()
        evaluated_outputs = []
        parsing_failed = []
        for result in raw_results:
            evaluated_output = re.search(r"\$\$\$\$\d+\$\$\$\$", result)
            if evaluated_output == None:
                evaluated_outputs.append(None)
                parsing_failed.append(result)
            else:
                evaluated_outputs.append(evaluated_output.group().replace("$", ""))  

        tot_sum = sum(filter(None, evaluated_outputs))
        tot_len = len(list(filter(None, evaluated_outputs)))
        suitability = tot_sum/tot_len
        print("\n**********************************************************************************")
        print(f"The Suitability Score: {suitability}")
        print("**********************************************************************************")
        return evaluated_outputs, raw_results, parsing_failed
    
def process_course(x):
    trans_table = str.maketrans({"[": "", "]": "", "'": "", " ": ""})
    result = x.translate(trans_table)
    result = result.split(",")
    return "-".join(result)
    

if __name__=="__main__":
    # Loading&Processing dataframe
    df = pd.read_csv(os.path.join("..", "db", "origin_fewshot_1.csv"))
    df["generated_route"] = df["generated_route"].map(process_course)
    df.head()

    # Loading environmental variable - Clova Studio API key
    api_key = os.getenv("OPENAI_API_KEY")

    # Loading prompt templates for generating reasoning
    PROMPT_DIR = os.path.join("..", "prompts", "cate_crs_eval_prmpt.yaml")
    prompts = load_yaml(PROMPT_DIR)

    sys_prmpt = prompts["sys_prmpt"]
    usr_prmpt_template = prompts["usr_prmpt_template"]
    usr_prmpts = [
        usr_prmpt_template.format(
            age=row.age,
            gender=row.gender,
            query=row.query,
            time=row.time,
            course=row.course,
        ) for _, row in df.iterrows()
    ]

    # call generation configuration
    CONFIG_DIR = os.path.join("..", "evaluation", "configs.yaml")
    gen_configs = load_yaml(CONFIG_DIR)

    file_path = os.path.join("..", "db", "requests.jsonl")

    course_evaluator = CourseEvaulator(api_key=api_key, **gen_configs)
    course_evaluator.save_requests(sys_prmpt, usr_prmpts, file_path)
    course_evaluator.evaluate()

    results, raw_results, parsing_failed = course_evaluator.get_results()
    df["evaluation"] = results
    df.to_csv(os.paht.join("..", "db", "evaluated.csv"), index=False)

    with open(os.path.join("..", "db", "evaluation", 'raw_results.txt'), 'w') as f:
        for item in raw_results:
            f.write(str(item) + '\n')

    with open(os.path.join("..", "db", "evaluation", 'parsing_failed.txt'), 'w') as f:
        for item in parsing_failed:
            f.write(str(item) + '\n')