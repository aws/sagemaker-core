import datetime
import time
import unittest

from sagemaker_core.helper.session_helper import Session, get_execution_role
from sagemaker_core.main.resources import Experiment, Trial, TrialComponent
from sagemaker_core.main.shapes import RawMetricData, TrialComponentParameterValue
from sagemaker_core.main.utils import get_textual_rich_logger

logger = get_textual_rich_logger(__name__)

sagemaker_session = Session()
region = sagemaker_session.boto_region_name
role = get_execution_role()
bucket = sagemaker_session.default_bucket()


class TestExperimentAndTrial(unittest.TestCase):
    def test_experiment_and_trial(self):
        experiment_name = "local-pyspark-experiment-example-" + time.strftime(
            "%Y-%m-%d-%H-%M-%S", time.gmtime()
        )
        run_group_name = "Default-Run-Group-" + experiment_name
        run_name = "local-experiment-run-" + time.strftime("%Y-%m-%d-%H-%M-%S", time.gmtime())

        experiment = Experiment.create(experiment_name=experiment_name)
        trial = Trial.create(trial_name=run_group_name, experiment_name=experiment_name)

        created_after = datetime.datetime.now() - datetime.timedelta(days=5)
        experiments_iterator = Experiment.get_all(created_after=created_after)
        experiments = [exp.experiment_name for exp in experiments_iterator]

        assert len(experiments) > 0
        assert experiment.experiment_name in experiments

        trial_component_parameters = {
            "num_train_samples": TrialComponentParameterValue(number_value=5),
            "num_test_samples": TrialComponentParameterValue(number_value=5),
        }

        trial_component = TrialComponent.create(
            trial_component_name=run_name,
            parameters=trial_component_parameters,
        )
        trial_component.associate_trail(trial_name=trial.trial_name)

        training_parameters = {
            "device": TrialComponentParameterValue(string_value="cpu"),
            "data_dir": TrialComponentParameterValue(string_value="test"),
            "optimizer": TrialComponentParameterValue(string_value="sgd"),
            "epochs": TrialComponentParameterValue(number_value=5),
            "hidden_channels": TrialComponentParameterValue(number_value=10),
        }
        trial_component.update(parameters=training_parameters)

        metrics = []
        for i in range(5):
            accuracy_metric = RawMetricData(
                metric_name="test:accuracy",
                value=i / 10,
                step=i,
                timestamp=time.time(),
            )
            metrics.append(accuracy_metric)

        trial_component.batch_put_metrics(metric_data=metrics)

        time.sleep(10)
        trial_component.refresh()

        assert len(trial_component.parameters) == 7
        assert len(trial_component.metrics) == 1
        assert trial_component.metrics[0].count == 5

        trial_component.disassociate_trail(trial_name=trial.trial_name)
        trial_component.delete()
        trial.delete()
        experiment.delete()
