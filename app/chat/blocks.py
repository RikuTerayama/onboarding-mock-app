from __future__ import annotations
from typing import List, Dict, Any, Optional

# Block Kit風の構造を定義（Web表示用）
# Slack Block Kitの構造を参考にしつつ、Web表示用に簡略化

def create_section(text: str, accessory: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Section blockを作成"""
    block: Dict[str, Any] = {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": text
        }
    }
    if accessory:
        block["accessory"] = accessory
    return block

def create_context(elements: List[str]) -> Dict[str, Any]:
    """Context blockを作成"""
    return {
        "type": "context",
        "elements": [
            {"type": "mrkdwn", "text": elem} for elem in elements
        ]
    }

def create_divider() -> Dict[str, Any]:
    """Divider blockを作成"""
    return {"type": "divider"}

def create_actions(buttons: List[Dict[str, str]]) -> Dict[str, Any]:
    """Actions blockを作成（ボタン付き）"""
    return {
        "type": "actions",
        "elements": [
            {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": btn["text"]
                },
                "action_id": btn.get("action_id", ""),
                "value": btn.get("value", ""),
                "style": btn.get("style", "default")
            }
            for btn in buttons
        ]
    }

def create_user_message(text: str) -> List[Dict[str, Any]]:
    """ユーザーメッセージ用のblocks"""
    return [
        create_section(f"*You:*\n{text}")
    ]

def create_bot_response(
    text: str,
    confidence: str = "high",
    references: Optional[List[str]] = None,
    escalate: bool = False
) -> List[Dict[str, Any]]:
    """ボット応答用のblocks"""
    blocks: List[Dict[str, Any]] = []
    
    # メインメッセージ
    blocks.append(create_section(f"*HR Bot:*\n{text}"))
    
    # 参照元
    if references:
        ref_text = "📚 *References:*\n" + "\n".join(f"• {ref}" for ref in references)
        blocks.append(create_context([ref_text]))
    
    # 信頼度が低い場合はEscalateボタンを表示
    if escalate or confidence == "low":
        blocks.append(create_actions([
            {
                "text": "Escalate to HR",
                "action_id": "escalate",
                "value": "escalate",
                "style": "danger"
            }
        ]))
    
    return blocks

