import datetime

from dataclasses import dataclass
from typing import Optional


class Base:
    """TBA"""
    pass


class Unassigned:
    """A custom type used to signify an undefined optional argument."""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance


@dataclass
class ExperimentSource(Base):
    """TBA"""
    source_arn: str
    source_type: Optional[str] = Unassigned()


@dataclass
class IamIdentity(Base):
    """TBA"""
    arn: Optional[str] = Unassigned()
    principal_id: Optional[str] = Unassigned()
    source_identity: Optional[str] = Unassigned()


@dataclass
class UserContext(Base):
    """TBA"""
    user_profile_arn: Optional[str] = Unassigned()
    user_profile_name: Optional[str] = Unassigned()
    domain_id: Optional[str] = Unassigned()
    iam_identity: Optional[IamIdentity] = Unassigned()


@dataclass
class Experiment(Base):
    """TBA"""
    experiment_name: Optional[str] = Unassigned()
    experiment_arn: Optional[str] = Unassigned()
    display_name: Optional[str] = Unassigned()
    source: Optional[ExperimentSource] = Unassigned()
    description: Optional[str] = Unassigned()
    creation_time: Optional[datetime.datetime] = Unassigned()
    created_by: Optional[UserContext] = Unassigned()
    last_modified_time: Optional[datetime.datetime] = Unassigned()
    last_modified_by: Optional[UserContext] = Unassigned()
    tags: Optional[list] = Unassigned()


@dataclass
class ExperimentConfig(Base):
    """TBA"""
    experiment_name: Optional[str] = Unassigned()
    trial_name: Optional[str] = Unassigned()
    trial_component_display_name: Optional[str] = Unassigned()
    run_name: Optional[str] = Unassigned()


@dataclass
class ExperimentSummary(Base):
    """TBA"""
    experiment_arn: Optional[str] = Unassigned()
    experiment_name: Optional[str] = Unassigned()
    display_name: Optional[str] = Unassigned()
    experiment_source: Optional[ExperimentSource] = Unassigned()
    creation_time: Optional[datetime.datetime] = Unassigned()
    last_modified_time: Optional[datetime.datetime] = Unassigned()


@dataclass
class Tag(Base):
    """TBA"""
    key: str
    value: str

