import pytest
from repositories.queue_repository import QueueRepository


@pytest.mark.asyncio
async def test_insert_review_submission(mock_db):
    repo = QueueRepository(mock_db)

    mock_db.run_query.return_value = 1  # Simulate inserted submission ID
    result = await repo.insert_review_submission("OL123M", "Amazing book!", username="jdoe")

    mock_db.run_query.assert_called_once_with(
        "insert_review_submission", openlib_id="OL123M", review="Amazing book!", username="jdoe"
    )
    assert result == 1


@pytest.mark.asyncio
async def test_insert_review_submission_defaults_to_anon(mock_db):
    repo = QueueRepository(mock_db)

    await repo.insert_review_submission("OL999M", "Default user test")
    mock_db.run_query.assert_called_once_with(
        "insert_review_submission", openlib_id="OL999M", review="Default user test", username="anon"
    )


@pytest.mark.asyncio
async def test_read_form_submission(mock_db):
    repo = QueueRepository(mock_db)

    mock_record = {"id": 1, "review": "Great!", "username": "jdoe"}
    mock_db.run_query.return_value = mock_record

    result = await repo.read_form_submission(submission_id=1)

    mock_db.run_query.assert_called_once_with("read_form_submission", submission_id=1)
    assert result == mock_record


@pytest.mark.asyncio
async def test_complete_form_submission(mock_db):
    repo = QueueRepository(mock_db)

    mock_db.run_query.return_value = True
    result = await repo.complete_form_submission(submission_id=2)

    mock_db.run_query.assert_called_once_with("complete_form_submission", submission_id=2)
    assert result is True
