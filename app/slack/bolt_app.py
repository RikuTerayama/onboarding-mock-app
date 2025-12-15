"""
Slack Bolt App統合
FastAPIと同居できる形で実装
"""
import os
import logging
from typing import Any, Dict

from slack_bolt import App
from slack_bolt.adapter.fastapi import SlackRequestHandler

from app.services.qa_engine import process_question
from app.db.repo import create_ticket

logger = logging.getLogger(__name__)

# Slack環境変数
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN", "")
SLACK_SIGNING_SECRET = os.getenv("SLACK_SIGNING_SECRET", "")
SLACK_HR_CHANNEL_ID = os.getenv("SLACK_HR_CHANNEL_ID", "")

# Slack Bolt App初期化
if SLACK_BOT_TOKEN and SLACK_SIGNING_SECRET:
    slack_app = App(
        token=SLACK_BOT_TOKEN,
        signing_secret=SLACK_SIGNING_SECRET
    )
    handler = SlackRequestHandler(slack_app)
else:
    logger.warning("SLACK_BOT_TOKEN or SLACK_SIGNING_SECRET not set. Slack integration disabled.")
    slack_app = None
    handler = None

def create_slack_blocks(qa_response) -> list:
    """QA応答をSlack Block Kit形式に変換"""
    blocks = []
    
    # Section block（メインメッセージ）
    blocks.append({
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": qa_response.answer_text
        }
    })
    
    # Context block（参照元）
    if qa_response.references:
        ref_text = "📚 *References:*\n" + "\n".join(f"• {ref}" for ref in qa_response.references)
        blocks.append({
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": ref_text
                }
            ]
        })
    
    # Actions block（Escalateボタン）
    if qa_response.confidence == "low" or len(qa_response.suggested_actions) > 0:
        blocks.append({
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Escalate to HR"
                    },
                    "action_id": "escalate_to_hr",
                    "style": "danger"
                }
            ]
        })
    
    return blocks

if slack_app:
    @slack_app.event("app_mention")
    def handle_app_mention(event: Dict[str, Any], say, client):
        """@bot メンションで質問を処理"""
        question = event.get("text", "").replace(f"<@{event.get('user')}>", "").strip()
        if not question:
            say("Please ask a question after mentioning me.")
            return
        
        # QAエンジンで処理
        qa_response = process_question(question)
        
        # Slack Block Kit形式で返答
        blocks = create_slack_blocks(qa_response)
        say(blocks=blocks)

    @slack_app.command("/hrhelp")
    def handle_hrhelp_command(ack, respond, command):
        """スラッシュコマンド /hrhelp を処理"""
        ack()
        
        question = command.get("text", "").strip()
        if not question:
            respond("Usage: /hrhelp <your question>\nExample: /hrhelp How do I request time off?")
            return
        
        # QAエンジンで処理
        qa_response = process_question(question)
        
        # Slack Block Kit形式で返答
        blocks = create_slack_blocks(qa_response)
        respond(blocks=blocks)

    @slack_app.action("escalate_to_hr")
    def handle_escalate_action(ack, body, respond, client):
        """Escalate to HRボタン押下時の処理"""
        ack()
        
        # 元のメッセージから質問を取得
        question = ""
        if "message" in body:
            message = body["message"]
            if "blocks" in message:
                for block in message["blocks"]:
                    if block.get("type") == "section" and "text" in block:
                        # 最初のsection blockから質問を推測（実際には前のメッセージから取得すべき）
                        text = block["text"].get("text", "")
                        if text:
                            question = text.replace("*HR Bot:*\n", "").strip()
        
        # イベント情報から質問を取得（簡易版）
        event = body.get("event", {})
        channel_id = event.get("channel", "") or body.get("channel", {}).get("id", "")
        user_id = body.get("user", {}).get("id", "") or event.get("user", "")
        
        # チケット作成
        ticket_id = create_ticket(
            source="slack",
            question=question or "Escalated from Slack",
            user_ref=user_id,
            channel_ref=channel_id
        )
        
        # ユーザーに応答
        respond(
            text=f"✅ Escalated to HR. Ticket #{ticket_id[:8]} created. HR will follow up soon.",
            replace_original=False
        )
        
        # HRチャンネルに通知（オプション）
        if SLACK_HR_CHANNEL_ID:
            try:
                client.chat_postMessage(
                    channel=SLACK_HR_CHANNEL_ID,
                    text=f"🚨 New HR ticket from Slack",
                    blocks=[
                        {
                            "type": "section",
                            "text": {
                                "type": "mrkdwn",
                                "text": f"*Ticket ID:* {ticket_id[:8]}\n*User:* <@{user_id}>\n*Channel:* <#{channel_id}>\n*Question:* {question or 'Escalated from Slack'}"
                            }
                        },
                        {
                            "type": "context",
                            "elements": [
                                {
                                    "type": "mrkdwn",
                                    "text": f"View all tickets: <http://localhost:8000/tickets|Web Dashboard>"
                                }
                            ]
                        }
                    ]
                )
            except Exception as e:
                logger.error(f"Failed to post to HR channel: {e}")
        else:
            logger.info(f"HR channel not configured. Ticket created: {ticket_id}")

