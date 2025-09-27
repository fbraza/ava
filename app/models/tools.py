from pydantic import BaseModel


class SlackChatPostMessageParams(BaseModel):
    """
    Parameters for the slack.chat.postMessage tool
    """

    channel: str
    text: str
