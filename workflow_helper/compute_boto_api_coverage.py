import ast
import csv
import importlib
import json


def main():
    """
    This function computes the ratio percentage of APIs covered by sagemaker core to the ones in boto.
    """
    additional_operations_json_path = "src/sagemaker_core/tools/additional_operations.json"
    with open(additional_operations_json_path, mode='r') as json_file:
        additional_operations_json = json.load(json_file)

    resource_csv_path = "resource_plan.csv"

    with open(resource_csv_path, mode='r') as file:
        csv_reader = csv.reader(file)
        module_name = "sagemaker_core.generated.resources"
        module = importlib.import_module(module_name)
        boto_methods = 0
        sagemaker_core_methods = 0

        next(csv_reader)

        for row in csv_reader:
            resource_name = row[0]
            standard_methods = ast.literal_eval(row[2]) + ast.literal_eval(row[3])
            additional_methods = ast.literal_eval(row[5])
            ResourceClass = getattr(module, resource_name)
            for standard_method in standard_methods:
                boto_methods = boto_methods + 1
                if hasattr(ResourceClass, standard_method) and callable(getattr(ResourceClass, standard_method)):
                    sagemaker_core_methods = sagemaker_core_methods + 1

            for additional_method in additional_methods:
                boto_methods = boto_methods + 1
                if additional_method in additional_operations_json:
                    sagemaker_core_methods = sagemaker_core_methods + 1

        print(sagemaker_core_methods * 100 / boto_methods)

if __name__ == "__main__":
    main()
