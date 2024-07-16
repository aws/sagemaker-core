import json


def main():
    json_file = 'coverage.json'

    with open(json_file, 'r') as f:
        data = json.load(f)
        print(data['files']['src/sagemaker_core/generated/resources.py']['summary']['percent_covered'])

if __name__ == "__main__":
    main()
