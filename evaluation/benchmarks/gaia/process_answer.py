import json
import os
from argparse import ArgumentParser

import litellm
from scorer import question_scorer

SYSTEM_PROMPT = """You are an answer extraction AI assistant. Your task is to:
1. Analyse the task description and the final thought of another AI Agent that attempts to solve this task.
2. Extract the correct answer from the final thought STRICTLY ensuring that it follows the output formatting instructions given in the task and the general output formatting rules given below.
3. If the AI agent's final answer contradicts their reasoning, you MUST infer the answer from AI agent's reasoning.
4. You MUST generate your response ONLY as a JSON object with the below structure:
```json
{
    "answer": "your final answer here"
}
```

General Output Formatting Rules:
1. The final answer should be a number OR as few words as possible OR a comma separated list of numbers and/or strings.
2. If the task asks for a number or numerical answer, express it numerically (i.e., with digits rather than words), do not use commas, and do not include units such as $ or percent signs unless specified otherwise.
3. If the task asks for a string, don't use articles, neither abbreviations (e.g. for cities) and express the digits in words.
4. If you are asked for a comma separated list, apply the above rules depending of whether the element to be put in the list is a number or a string.
5. The output formatting instructions given in the task MUST be given HIGHER priority as compared the above general rules.

CRITICAL INSTRUCTIONS:
1. In some cases the AI agent's final answer contradicts their reasoning, ALWAYS favor the reasoning to infer the correct answer.
2. When in doubt, preserve the agent's intended answer rather than reformatting it incorrectly.
3. If task-specific formatting conflicts with general rules, always follow task-specific instructions.

Your role is to refine and present the agent's answer correctly, NOT to solve the task independently or introduce new information
"""


def query_llm(task: str, model_answer_raw: str, finish_thought: str, model: str):
    agent_output = finish_thought + '\n' + model_answer_raw
    agent_output = agent_output.strip()
    if agent_output == '':
        return ''
    prompt = f"""
Task description: {task}
Final thought of AI Agent: {agent_output}

Please respond in JSON format as mentioned in the SYSTEM prompt.
""".strip()

    response = litellm.completion(
        model=model,
        messages=[
            {'role': 'system', 'content': SYSTEM_PROMPT},
            {'role': 'user', 'content': prompt},
        ],
        max_tokens=2048,
        base_url=os.environ.get('LITELLM_BASE_URL'),
        temperature=0,
        api_key=os.environ.get('LITELLM_API_KEY'),
    )

    return response.choices[0].message.content.strip()


def extract_model_anwer(filename):
    with open(filename, 'r') as f:
        output_list = []
        for line in f:
            op = {}
            data = json.loads(line.strip())
            op['task_id'] = data['instance_id']
            op['result'] = int(data['test_result']['score'])
            op['model_answer_raw'] = data['test_result']['model_answer_raw']
            op['model_answer'] = data['test_result']['model_answer']
            op['ground_truth'] = data['test_result']['ground_truth']
            for i, action_observation in enumerate(data['history']):
                assert len(action_observation) == 2
                action = action_observation[0]
                if action['source'] == 'user' and 'task' not in op:
                    thought = (
                        action['args']['content']
                        .split('Here is the task:')[-1]
                        .split('IMPORTANT: When seeking information from a website')[0]
                        .strip()
                    )
                    op['task'] = thought
                elif action['source'] == 'agent':
                    # assert action['source'] == 'agent'
                    thought = action['args'].get('thought', '')
                    content = action['args'].get('content', '')
                    assert thought == content or thought == '' or content == ''
                    thought_content = thought + ' ' + content
                    if 'tool_call_metadata' in action:
                        assert (
                            len(
                                action['tool_call_metadata']['model_response'][
                                    'choices'
                                ][0]['message']['tool_calls']
                            )
                            == 1
                        )
                        tool_call = action['tool_call_metadata']['model_response'][
                            'choices'
                        ][0]['message']['tool_calls'][0]['function']
                        if tool_call['name'] == 'finish':
                            op['finish_thought'] = thought_content
                            break
            output_list.append(op)
    return output_list


def process_answer(output_list, model):
    final_data = []
    score = 0
    for item in output_list:
        task = item['task']
        model_answer_raw = item['model_answer_raw']
        finish_thought = item.get('finish_thought', '')
        llm_output = query_llm(task, model_answer_raw, finish_thought, model)
        # print(llm_output)
        if llm_output.startswith('```'):
            llm_output = llm_output[len('```json') :].strip()
        if llm_output.endswith('```'):
            llm_output = llm_output[: -len('```')].strip()
        try:
            llm_output = json.loads(llm_output)
            ans = str(llm_output['answer']).strip()
        except Exception as _:
            if '"answer":' in llm_output:
                try:
                    llm_output = llm_output.split('"answer":')[-1].strip()[:-1]
                    if llm_output[0] in '"\'':
                        llm_output = llm_output[1:]
                    if llm_output[-1] in '"\'':
                        llm_output = llm_output[:-1]
                    llm_output = str(llm_output)
                except Exception as _:
                    llm_output = ''
            ans = llm_output
        new_item = {}
        new_item['task_id'] = item['task_id']
        new_item['model_answer'] = ans
        new_item['reasoning_trace'] = ''
        final_data.append(new_item)
        score += question_scorer(ans, item['ground_truth'])
    print(f'Average score: {score} / {len(output_list)} = {score / len(output_list)}')
    return final_data


def main(args):
    input_filename = args.input_filename
    output_filename = args.output_filename

    # Extract raw model answers from the input file
    raw_outputs = extract_model_anwer(input_filename)

    # Process the extracted answers using an LLM
    final_outputs = process_answer(raw_outputs, args.model)
    with open(output_filename, 'w') as f:
        for item in final_outputs:
            json_line = json.dumps(item)
            f.write(json_line + '\n')
    print(f'Processed outputs saved to {output_filename}')


if __name__ == '__main__':
    # use argument parser to get the filename
    parser = ArgumentParser(description='Extract model answer from output file')
    parser.add_argument(
        '--input-filename',
        type=str,
        help='Path to the output.jsonl file',
        required=True,
    )
    parser.add_argument(
        '--output-filename',
        type=str,
        help='Path to the JSON-lines file containing processed outputs',
        default='./model_outputs_test_processed.jsonl',
    )
    parser.add_argument(
        '--model',
        type=str,
        help='Model to use for processing. We use claude-3.7-sonnet for all our experiments',
        default='claude-3-7-sonnet-20250219',
    )
    args = parser.parse_args()
    main(args)
