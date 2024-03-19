from typing import Optional
import datetime


class Shape:
    """TBA"""
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


class CreateExperimentRequest(Shape):
    """TBA"""
    def __init__(
        self,
        experiment_name: str = None,
        display_name: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[list] = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.experiment_name = experiment_name,
        self.display_name = display_name,
        self.description = description,
        self.tags = tags,


class CreateExperimentResponse(Shape):
    """TBA"""
    def __init__(
        self,
        experiment_arn: Optional[str] = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.experiment_arn = experiment_arn,


class DeleteExperimentRequest(Shape):
    """TBA"""
    def __init__(
        self,
        experiment_name: str = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.experiment_name = experiment_name,


class DeleteExperimentResponse(Shape):
    """TBA"""
    def __init__(
        self,
        experiment_arn: Optional[str] = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.experiment_arn = experiment_arn,


class DescribeExperimentRequest(Shape):
    """TBA"""
    def __init__(
        self,
        experiment_name: str = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.experiment_name = experiment_name,


class ExperimentSource(Shape):
    """TBA"""
    def __init__(
        self,
        source_arn: str = None,
        source_type: Optional[str] = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.source_arn = source_arn,
        self.source_type = source_type,


class IamIdentity(Shape):
    """TBA"""
    def __init__(
        self,
        arn: Optional[str] = None,
        principal_id: Optional[str] = None,
        source_identity: Optional[str] = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.arn = arn,
        self.principal_id = principal_id,
        self.source_identity = source_identity,


class UserContext(Shape):
    """TBA"""
    def __init__(
        self,
        user_profile_arn: Optional[str] = None,
        user_profile_name: Optional[str] = None,
        domain_id: Optional[str] = None,
        iam_identity: Optional[IamIdentity] = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.user_profile_arn = user_profile_arn,
        self.user_profile_name = user_profile_name,
        self.domain_id = domain_id,
        self.iam_identity = iam_identity,


class DescribeExperimentResponse(Shape):
    """TBA"""
    def __init__(
        self,
        experiment_name: Optional[str] = None,
        experiment_arn: Optional[str] = None,
        display_name: Optional[str] = None,
        source: Optional[ExperimentSource] = None,
        description: Optional[str] = None,
        creation_time: Optional[datetime.datetime] = None,
        created_by: Optional[UserContext] = None,
        last_modified_time: Optional[datetime.datetime] = None,
        last_modified_by: Optional[UserContext] = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.experiment_name = experiment_name,
        self.experiment_arn = experiment_arn,
        self.display_name = display_name,
        self.source = source,
        self.description = description,
        self.creation_time = creation_time,
        self.created_by = created_by,
        self.last_modified_time = last_modified_time,
        self.last_modified_by = last_modified_by,


class Experiment(Shape):
    """TBA"""
    def __init__(
        self,
        experiment_name: Optional[str] = None,
        experiment_arn: Optional[str] = None,
        display_name: Optional[str] = None,
        source: Optional[ExperimentSource] = None,
        description: Optional[str] = None,
        creation_time: Optional[datetime.datetime] = None,
        created_by: Optional[UserContext] = None,
        last_modified_time: Optional[datetime.datetime] = None,
        last_modified_by: Optional[UserContext] = None,
        tags: Optional[list] = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.experiment_name = experiment_name,
        self.experiment_arn = experiment_arn,
        self.display_name = display_name,
        self.source = source,
        self.description = description,
        self.creation_time = creation_time,
        self.created_by = created_by,
        self.last_modified_time = last_modified_time,
        self.last_modified_by = last_modified_by,
        self.tags = tags,


class ExperimentConfig(Shape):
    """TBA"""
    def __init__(
        self,
        experiment_name: Optional[str] = None,
        trial_name: Optional[str] = None,
        trial_component_display_name: Optional[str] = None,
        run_name: Optional[str] = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.experiment_name = experiment_name,
        self.trial_name = trial_name,
        self.trial_component_display_name = trial_component_display_name,
        self.run_name = run_name,


class ExperimentSummary(Shape):
    """TBA"""
    def __init__(
        self,
        experiment_arn: Optional[str] = None,
        experiment_name: Optional[str] = None,
        display_name: Optional[str] = None,
        experiment_source: Optional[ExperimentSource] = None,
        creation_time: Optional[datetime.datetime] = None,
        last_modified_time: Optional[datetime.datetime] = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.experiment_arn = experiment_arn,
        self.experiment_name = experiment_name,
        self.display_name = display_name,
        self.experiment_source = experiment_source,
        self.creation_time = creation_time,
        self.last_modified_time = last_modified_time,


class Tag(Shape):
    """TBA"""
    def __init__(
        self,
        key: str = None,
        value: str = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.key = key,
        self.value = value,


class UpdateExperimentRequest(Shape):
    """TBA"""
    def __init__(
        self,
        experiment_name: str = None,
        display_name: Optional[str] = None,
        description: Optional[str] = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.experiment_name = experiment_name,
        self.display_name = display_name,
        self.description = description,


class UpdateExperimentResponse(Shape):
    """TBA"""
    def __init__(
        self,
        experiment_arn: Optional[str] = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.experiment_arn = experiment_arn,

