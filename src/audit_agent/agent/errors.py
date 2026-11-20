"""Errors shared by the tool modules."""


class ToolError(Exception):
    """A tool call that cannot be answered; the message goes back to the model."""
