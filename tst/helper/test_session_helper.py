"""Unit tests for the default-bucket ownership checks in ``Session``.

The SDK-generated default bucket name ``sagemaker-{region}-{account}`` is predictable, so
another account can pre-create it. These tests cover the checks that reject such a bucket.
"""

from unittest.mock import Mock, patch

import pytest
from botocore.exceptions import ClientError

from sagemaker_core.helper.session_helper import Session

ACCOUNT = "222222222222"
REGION = "us-west-2"
DEFAULT_BUCKET = f"sagemaker-{REGION}-{ACCOUNT}"


def _client_error(code, message, operation="HeadBucket"):
    return ClientError({"Error": {"Code": code, "Message": message}}, operation)


@pytest.fixture
def session():
    boto_session = Mock()
    boto_session.region_name = REGION
    sess = Session(boto_session=boto_session, sagemaker_client=Mock())
    sess.s3_resource = Mock()
    sess.s3_client = Mock()
    with patch.object(sess, "account_id", return_value=ACCOUNT), patch.object(
        sess, "generate_default_sagemaker_bucket_name", return_value=DEFAULT_BUCKET
    ):
        yield sess


def _bucket_not_in_caller_list(sess):
    """Make ``s3.Bucket(...).creation_date`` None, as for a bucket owned by another account."""
    bucket = Mock()
    bucket.name = DEFAULT_BUCKET
    bucket.creation_date = None
    sess.s3_resource.Bucket.return_value = bucket
    return bucket


class TestDefaultBucketOwnership:
    def test_squatted_default_bucket_is_rejected(self, session):
        """A bucket owned by another account is absent from ListBuckets (creation_date None).

        The ownership probe must still run on that path and its 403 must propagate.
        """
        _bucket_not_in_caller_list(session)
        head_bucket = session.s3_resource.meta.client.head_bucket
        head_bucket.side_effect = _client_error("403", "Forbidden")

        with pytest.raises(ClientError):
            session.default_bucket()

        head_bucket.assert_called_once_with(Bucket=DEFAULT_BUCKET, ExpectedBucketOwner=ACCOUNT)
        session.s3_resource.create_bucket.assert_not_called()
        assert session._default_bucket is None

    def test_missing_default_bucket_is_created(self, session):
        _bucket_not_in_caller_list(session)
        head_bucket = session.s3_resource.meta.client.head_bucket
        head_bucket.side_effect = _client_error("404", "Not Found")

        assert session.default_bucket() == DEFAULT_BUCKET

        head_bucket.assert_called_once_with(Bucket=DEFAULT_BUCKET, ExpectedBucketOwner=ACCOUNT)
        session.s3_resource.create_bucket.assert_called_once_with(
            Bucket=DEFAULT_BUCKET, CreateBucketConfiguration={"LocationConstraint": REGION}
        )

    def test_own_existing_default_bucket_is_checked_with_owner(self, session):
        bucket = _bucket_not_in_caller_list(session)
        bucket.creation_date = "2026-01-01"
        head_bucket = session.s3_resource.meta.client.head_bucket

        assert session.default_bucket() == DEFAULT_BUCKET

        assert head_bucket.call_count == 2
        for call in head_bucket.call_args_list:
            assert call.kwargs == {"Bucket": DEFAULT_BUCKET, "ExpectedBucketOwner": ACCOUNT}

    def test_user_supplied_default_bucket_is_probed_without_owner(self, session):
        """A user-supplied default bucket may be cross-account and must keep working."""
        session._default_bucket_name_override = "shared-team-bucket"
        _bucket_not_in_caller_list(session)
        head_bucket = session.s3_resource.meta.client.head_bucket

        assert session.default_bucket() == "shared-team-bucket"

        head_bucket.assert_called_once_with(Bucket="shared-team-bucket")

    def test_user_supplied_default_bucket_forbidden_still_raises(self, session):
        session._default_bucket_name_override = "shared-team-bucket"
        _bucket_not_in_caller_list(session)
        session.s3_resource.meta.client.head_bucket.side_effect = _client_error("403", "Forbidden")

        with pytest.raises(ClientError):
            session.default_bucket()


class TestGetAccountIdIfDefaultBucket:
    def test_returns_account_for_sdk_default_bucket(self, session):
        session._default_bucket = DEFAULT_BUCKET
        session._default_bucket_set_by_sdk = True
        assert session._get_account_id_if_default_bucket(DEFAULT_BUCKET) == ACCOUNT

    @pytest.mark.parametrize("bucket", [None, "", "other-bucket"])
    def test_returns_none_for_other_buckets(self, session, bucket):
        session._default_bucket = DEFAULT_BUCKET
        session._default_bucket_set_by_sdk = True
        assert session._get_account_id_if_default_bucket(bucket) is None

    def test_returns_none_for_user_supplied_default_bucket(self, session):
        session._default_bucket = "shared-team-bucket"
        session._default_bucket_set_by_sdk = False
        assert session._get_account_id_if_default_bucket("shared-team-bucket") is None

    def test_does_not_resolve_default_bucket(self, session):
        session._default_bucket_set_by_sdk = True
        with patch.object(session, "default_bucket") as default_bucket:
            assert session._get_account_id_if_default_bucket(DEFAULT_BUCKET) is None
        default_bucket.assert_not_called()


class TestUploadDataOwnership:
    def _upload(self, session, tmp_path, **kwargs):
        local_file = tmp_path / "train.csv"
        local_file.write_text("x")
        s3_object = Mock()
        session.s3_resource.Object.return_value = s3_object
        session.upload_data(path=str(local_file), **kwargs)
        return s3_object.upload_file.call_args.kwargs["ExtraArgs"]

    def test_upload_to_default_bucket_sets_expected_owner(self, session, tmp_path):
        session._default_bucket = DEFAULT_BUCKET
        session._default_bucket_set_by_sdk = True
        assert self._upload(session, tmp_path) == {"ExpectedBucketOwner": ACCOUNT}

    def test_upload_to_default_bucket_keeps_caller_extra_args(self, session, tmp_path):
        session._default_bucket = DEFAULT_BUCKET
        session._default_bucket_set_by_sdk = True
        caller_args = {"ServerSideEncryption": "AES256"}

        extra_args = self._upload(session, tmp_path, extra_args=caller_args)

        assert extra_args == {"ServerSideEncryption": "AES256", "ExpectedBucketOwner": ACCOUNT}
        assert caller_args == {"ServerSideEncryption": "AES256"}

    def test_upload_to_other_bucket_omits_expected_owner(self, session, tmp_path):
        session._default_bucket = DEFAULT_BUCKET
        session._default_bucket_set_by_sdk = True
        assert self._upload(session, tmp_path, bucket="partner-bucket") is None


class TestReadS3FileOwnership:
    def _read(self, session, bucket):
        body = Mock()
        body.read.return_value = b"content"
        session.s3_client.get_object.return_value = {"Body": body}
        assert session.read_s3_file(bucket, "key") == "content"

    def test_read_from_default_bucket_sets_expected_owner(self, session):
        session._default_bucket = DEFAULT_BUCKET
        session._default_bucket_set_by_sdk = True
        self._read(session, DEFAULT_BUCKET)
        session.s3_client.get_object.assert_called_once_with(
            Bucket=DEFAULT_BUCKET, Key="key", ExpectedBucketOwner=ACCOUNT
        )

    def test_read_from_other_bucket_omits_expected_owner(self, session):
        session._default_bucket = DEFAULT_BUCKET
        session._default_bucket_set_by_sdk = True
        self._read(session, "jumpstart-cache-prod-us-west-2")
        session.s3_client.get_object.assert_called_once_with(
            Bucket="jumpstart-cache-prod-us-west-2", Key="key"
        )
