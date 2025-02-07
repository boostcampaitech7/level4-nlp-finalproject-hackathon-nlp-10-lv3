import os
import re
import json
import time
import argparse
from tqdm import tqdm

import pandas as pd
import openai
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
        
        self.client = OpenAI(api_key=self.api_key)
    
    def create_completion(self, sys_prmpt, usr_prmpt):
        return self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": sys_prmpt},
                {"role": "user", "content": usr_prmpt},
            ],
            max_tokens = self.max_tokens,
            temperature = self.temperature,
            top_p = self.top_p,
            frequency_penalty = self.frequency_penalty,
            presence_penalty = self.presence_penalty,
            stop = self.stop,
            logprobs = self.logprobs,
            top_logprobs = self.top_logprobs,
            n = self.n,
        )
    
    def evaluate(self, sys_prmpt, usr_prmpts):
        raw_results = []
        evaluated_outputs = []
        parsing_failed = []
        failure_index = []
        used_tokens = {
            "cached_prompt_tokens": 0,
            "uncached_prompt_tokens": 0,
            "completion_tokens": 0,
        }
        for i, usr_prmpt in tqdm(
            enumerate(usr_prmpts),
            desc="API calling",
            unit="request",
            total=len(usr_prmpts),
        ):
            fail_cnt = 0
            while fail_cnt<=5:
                try:
                    completion = self.create_completion(sys_prmpt, usr_prmpt)
                    break
                except openai.APIError as e:
                    fail_cnt +=1
                    print(f"Fail-{fail_cnt}")
                    print(f"OpenAI API returned an API Error: {e}")
                except openai.APIConnectionError as e:
                    fail_cnt +=1
                    print(f"Fail-{fail_cnt}")
                    print(f"Failed to connect to OpenAI API: {e}")
                except openai.RateLimitError as e:
                    fail_cnt = 6
                    print(f"OpenAI API request exceeded rate limit: {e}")
                    break
                except Exception as e:
                    fail_cnt +=1
                    print(f"Fail-{fail_cnt}")
                    print(f"An unexpected error occurred: {e}")

            if fail_cnt==6:
                raw_results.append("Fail")
                failure_index.append(i)
                continue

            raw_result = completion.choices[0].message.content
            raw_results.append(raw_result)

            evaluated_output = re.search(r"\$\$\$\$\d+\$\$\$\$", raw_result)
            if evaluated_output == None:
                parsing_failed.append(raw_result)
            else:
                evaluated_outputs.append(int(evaluated_output.group().replace("$", "")))
                time.sleep(5)
            
            usage = completion.usage
            cached_prompt_tokens = usage.prompt_tokens_details.cached_tokens
            uncached_prompt_tokens = usage.prompt_tokens - cached_prompt_tokens
            completion_tokens = usage.completion_tokens
            used_tokens["cached_prompt_tokens"] += cached_prompt_tokens
            used_tokens["uncached_prompt_tokens"] += uncached_prompt_tokens
            used_tokens["completion_tokens"] += completion_tokens

        return {
            "raw_results": raw_results,
            "evaluated_outputs": evaluated_outputs,
            "parsing_failed": parsing_failed,
            "failure_index": failure_index,
            "used_tokens": used_tokens,
        }

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
    
    def batch_evaluate(self):
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
                fail_cnt += 1
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

    def get_raw_results_batch(self):
        result_file_id = self.client.batches.retrieve(self.batch_job.id).output_file_id
        results = self.client.files.content(result_file_id).content.decode('utf-8')
        return [json.loads(line)["response"]["body"]["choices"][0]["message"]["content"]
                for line in results.split('\n') if line]

    def get_results_batch(self):
        raw_results = self.get_raw_results_batch()
        evaluated_outputs = []
        parsing_failed = []
        for result in raw_results:
            evaluated_output = re.search(r"\$\$\$\$\d+\$\$\$\$", result)
            if evaluated_output == None:
                evaluated_outputs.append(None)
                parsing_failed.append(result)
            else:
                evaluated_outputs.append(int(evaluated_output.group().replace("$", "")))
        
        return {
            "evaluated_outputs": evaluated_outputs,
            "parsing_failed": parsing_failed,
            "raw_results": raw_results,
        }
    
def process_course(x):
    trans_table = str.maketrans({"[": "", "]": "", "'": "", " ": ""})
    result = x.translate(trans_table)
    result = result.split(",")
    return "-".join(result)
    

if __name__=="__main__":
    args = argparse.ArgumentParser()
    args.add_argument(
        "-f",
        "-file_name",
        default=None,
        type=str,
        help="The file name which has the generated route",
    )
    arg = args.parse_args()

    # Loading&Processing dataframe
    df = pd.read_csv(os.path.join("..", "db", f"{arg.file_name}.csv"))
    df["generated_route"] = df["generated_route"].map(process_course)
    
    data_size = df.shape[0]
    idx_1 = df["generated_route"]=="0"
    idx_2 = df["generated_route"]== 0
    cnt_0 = sum(idx_1 | idx_2)
    df = df[~(idx_1 | idx_2)]
    print(f"Count for zero: {cnt_0}/{data_size}\n")

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
            request=row.request,
            start_time=row.start_time,
            generated_route=row.generated_route,
        ) for _, row in df.iterrows()
    ]

    # call generation configuration
    CONFIG_DIR = os.path.join("..", "evaluation", "configs.yaml")
    gen_configs = load_yaml(CONFIG_DIR)

    course_evaluator = CourseEvaulator(api_key=api_key, **gen_configs)
    results = course_evaluator.evaluate(sys_prmpt, usr_prmpts)
    df["evaluation"] = results["evaluated_outputs"]

    tot_sum = sum(results["evaluated_outputs"])
    tot_len = len(results["evaluated_outputs"])
    failure_len = len(results["parsing_failed"])
    suitability = tot_sum/tot_len
    failure_ratio = failure_len/tot_len

    cached_prompt_tokens = results["used_tokens"]["cached_prompt_tokens"]
    uncached_prompt_tokens = results["used_tokens"]["uncached_prompt_tokens"]
    completion_tokens = results["used_tokens"]["completion_tokens"]
    cost = (1.25*cached_prompt_tokens + 2.5*uncached_prompt_tokens + 10*completion_tokens)/1e+6
    print("\n**********************************************************************************")
    print("***Results***")
    print(f"The Suitability Score: {suitability:.4f} ({tot_sum}/{tot_len})")
    print(f"The Failure Ratio: {failure_ratio:.4f} ({failure_len}/{tot_len})")
    print(f"The Parsing Failure Ratio: {failure_ratio:.4f} ({failure_len}/{tot_len})\n")
    print("***Token Usage***")
    print(f"Uncached Input Tokens: {uncached_prompt_tokens}")
    print(f"Cached Input Tokens: {cached_prompt_tokens}")
    print(f"Output Tokens: {completion_tokens}")
    print(f"Cost: {cost:4f}$")
    print("**********************************************************************************")

    df.to_csv(os.path.join("..", "db", "evaluation", f"{arg.file_name}", "evaluated.csv"), index=False)

    with open(os.path.join("..", "db", "evaluation", f"{arg.file_name}", 'raw_results.txt'), 'w') as f:
        for item in results["raw_results"]:
            f.write(str(item) + '\n')

    with open(os.path.join("..", "db", "evaluation", f"{arg.file_name}", 'parsing_failed.txt'), 'w') as f:
        for item in results["parsing_failed"]:
            f.write(str(item) + '\n')