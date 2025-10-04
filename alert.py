from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import yagmail

# -------------------------------
# Slack setup
# -------------------------------
SLACK_TOKEN = "xoxb-9664844337472-9630204501555-bgnK4kPHlW37Xl7ln9Adpygz"
SLACK_CHANNEL = "#alert"

slack_client = WebClient(token=SLACK_TOKEN)

# -------------------------------
# Email setup
# -------------------------------
EMAIL_USER = "sumitkumarbittuair@gmail.com"
EMAIL_PASS = "cdej wqzx feah uiav"

# -------------------------------
# Send Slack Alert (blocks)
# -------------------------------
def send_slack_alert(text, sentiment, score, urgency, recommendation):
    blocks = [
        {"type": "section",
         "text": {"type": "mrkdwn",
                  "text": "*🚨 Customer Sentiment Alert!*"}},
        {"type": "section",
         "fields": [
             {"type": "mrkdwn", "text": f"*Text:*\n{text}"},
             {"type": "mrkdwn", "text": f"*Sentiment:*\n{sentiment}"},
             {"type": "mrkdwn", "text": f"*Confidence:*\n{score:.2f}"},
             {"type": "mrkdwn", "text": f"*Urgency:*\n{urgency}"},
             {"type": "mrkdwn", "text": f"*Recommended Response:*\n{recommendation}"}
         ]}
    ]

    try:
        slack_client.chat_postMessage(channel=SLACK_CHANNEL, blocks=blocks)
        print("✅ Slack alert sent!")
    except SlackApiError as e:
        print(f"❌ Slack Error: {e.response['error']}")

# -------------------------------
# Send Email Alert
# -------------------------------
def send_email_alert(subject, text, sentiment, score, urgency, recommendation, recipient):
    try:
        yag = yagmail.SMTP(EMAIL_USER, EMAIL_PASS)
        email_body = f"""
        <h2>🚨 Customer Sentiment Alert</h2>
        <p><strong>Text:</strong> {text}</p>
        <p><strong>Sentiment:</strong> {sentiment}</p>
        <p><strong>Confidence:</strong> {score:.2f}</p>
        <p><strong>Urgency:</strong> {urgency}</p>
        <p><strong>Recommended Response:</strong> {recommendation}</p>
        """
        yag.send(to=recipient, subject=subject, contents=email_body)
        print("✅ Email alert sent!")
    except Exception as e:
        print(f"❌ Email Error: {e}")

# -------------------------------
# Unified Alert Function
# -------------------------------
def send_alert(text, sentiment, score, urgency, recommendation, recipient=EMAIL_USER):
    send_slack_alert(text, sentiment, score, urgency, recommendation)
    send_email_alert("Customer Sentiment Alert", text, sentiment, score, urgency, recommendation, recipient)