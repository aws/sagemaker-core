import json


def main():
    json_file = 'data.json'

    with open(json_file, 'r') as f:
        data = json.load(f)
        print(data['files']['src/sagemaker_core/generated/resources.py']['percent_covered'])

if __name__ == "main":
    main()
