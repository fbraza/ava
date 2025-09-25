from pydantic import BaseModel


class SlackChatPostMessageParams(BaseModel):
    channel: str
    text: str
