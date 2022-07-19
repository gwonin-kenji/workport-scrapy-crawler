import slackweb
import os

class SlackNotify:
    """
    スラック通知
    """

    def __init__(self) -> None:
        self.slack_hook_url = os.getenv("SLACK_WEBHOOK_URL")
        self.prefix = '[Workport]\t'
        assert self.slack_hook_url is not None, "環境変数にSLACK_URLが設定されていません。"

    def slack_notify(self, message: str) -> None:
        """
        スラック通知
        """
        data = {'text': self.prefix + str(message)}
        slack = slackweb.Slack(url=self.slack_hook_url)
        slack.notify(text=data['text'])