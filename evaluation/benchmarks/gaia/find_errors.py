import argparse
import json
import os
import shutil


def main(input_path):
    # Create temp file in the same directory as input file
    input_dir = os.path.dirname(input_path)
    temp_output_path = os.path.join(input_dir, 'temp.jsonl')

    remove_ids = set()
    with open(input_path, 'r') as f:
        for line in f:
            data = json.loads(line.strip())
            if (
                len(data['test_result']) == 0
                or 'no_answer' in data['test_result']['model_answer_raw']
            ):
                remove_ids.add(data['instance_id'])
                continue

    # Write filtered data to temporary output file
    with open(temp_output_path, 'w') as f_out:
        with open(input_path, 'r') as f_in:
            for line in f_in:
                data = json.loads(line.strip())
                if data['instance_id'] not in remove_ids:
                    f_out.write(json.dumps(data) + '\n')

    # Replace input file with temp file
    shutil.copy2(temp_output_path, input_path)

    # Delete the temp file
    os.remove(temp_output_path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Filter JSONL files by removing entries with empty test results or "no_answer".'
    )
    parser.add_argument('input_file', type=str, help='Path to the output.jsonl file')
    args = parser.parse_args()

    main(args.input_file)
