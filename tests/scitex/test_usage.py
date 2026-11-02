"""Usage text is both returned and emitted as an exact prefix-free result."""

from scitex.usage import show


def test_rendered_usage_stdout_matches_returned_template(capsys):
    # Arrange — a real installed code template, not a synthetic result.
    topic = "session-minimal"
    # Act
    text = show(topic)
    captured = capsys.readouterr()
    # Assert
    assert (captured.out, captured.err) == (text + "\n", "")


def test_unknown_topic_stdout_matches_returned_guidance(capsys):
    # Arrange
    topic = "missing-output-contract-topic"
    # Act
    text = show(topic)
    captured = capsys.readouterr()
    # Assert
    assert (captured.out, captured.err) == (text + "\n", "")
