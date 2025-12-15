from __future__ import annotations
from typing import Dict, List, Any
from dataclasses import dataclass

@dataclass
class QAResponse:
    answer_text: str
    confidence: str  # "high" or "low"
    references: List[str]
    suggested_actions: List[str]

# キーワード辞書ベースのQAエンジン
QA_KNOWLEDGE: Dict[str, Dict[str, Any]] = {
    "attendance": {
        "keywords": ["勤怠", "出勤", "退勤", "attendance", "clock", "time", "work hours"],
        "answer": "勤怠管理について：\n• 出勤時間: 9:00-10:00の間で柔軟\n• 退勤時間: 18:00以降（8時間労働）\n• 遅刻・早退は事前にマネージャーに連絡\n• システム: [勤怠管理システム](https://example.com/attendance)",
        "references": [
            "[勤怠規程](https://example.com/attendance-policy)",
            "[勤怠管理システム](https://example.com/attendance)"
        ],
        "confidence": "high"
    },
    "leave": {
        "keywords": ["休暇", "有休", "年休", "leave", "vacation", "holiday", "PTO"],
        "answer": "休暇申請について：\n• 有給休暇: 入社日から付与（初年度10日）\n• 申請方法: [休暇申請システム](https://example.com/leave)から申請\n• 事前申請: 原則1週間前まで\n• 緊急時: 当日でも可（マネージャー承認必要）",
        "references": [
            "[休暇規程](https://example.com/leave-policy)",
            "[休暇申請システム](https://example.com/leave)"
        ],
        "confidence": "high"
    },
    "address": {
        "keywords": ["住所", "転居", "引っ越し", "address", "move", "relocation"],
        "answer": "住所変更について：\n• 変更手続き: [人事システム](https://example.com/hr)の「個人情報変更」から申請\n• 必要書類: 住民票の写しまたは運転免許証\n• 提出期限: 変更後1週間以内\n• 影響: 給与明細の送付先が更新されます",
        "references": [
            "[人事システム](https://example.com/hr)",
            "[個人情報管理規程](https://example.com/privacy)"
        ],
        "confidence": "high"
    },
    "onboarding": {
        "keywords": ["オンボーディング", "入社", "初日", "onboarding", "first day", "new hire"],
        "answer": "オンボーディングについて：\n• 初日: 9:00に本社受付で集合\n• 持ち物: 身分証明書、銀行口座情報\n• 初日スケジュール: HRオリエンテーション → デスクセットアップ → チーム紹介\n• 詳細: マネージャーから事前に連絡があります",
        "references": [
            "[オンボーディングガイド](https://example.com/onboarding)",
            "[初日チェックリスト](https://example.com/first-day)"
        ],
        "confidence": "high"
    },
    "training": {
        "keywords": ["研修", "トレーニング", "教育", "training", "education", "course"],
        "answer": "研修について：\n• 必須研修: セキュリティ研修、コンプライアンス研修（入社後1ヶ月以内）\n• 選択研修: [研修カタログ](https://example.com/training)から選択可能\n• 申請方法: マネージャー承認後、[研修システム](https://example.com/training)から申請\n• 費用: 会社負担（業務関連のみ）",
        "references": [
            "[研修カタログ](https://example.com/training)",
            "[研修システム](https://example.com/training)"
        ],
        "confidence": "high"
    },
    "benefits": {
        "keywords": ["福利厚生", "ベネフィット", "benefits", "insurance", "health"],
        "answer": "福利厚生について：\n• 健康保険: 社会保険完備\n• 退職金制度: あり（3年以上勤務）\n• 各種手当: 交通費、住宅手当（条件あり）\n• 詳細: [福利厚生ガイド](https://example.com/benefits)を参照",
        "references": [
            "[福利厚生ガイド](https://example.com/benefits)"
        ],
        "confidence": "high"
    }
}

def process_question(question: str) -> QAResponse:
    """
    質問を処理して回答を生成（ルールベース）
    
    Args:
        question: ユーザーの質問テキスト
    
    Returns:
        QAResponse: 回答、信頼度、参照元、推奨アクション
    """
    question_lower = question.lower()
    
    # キーワードマッチング
    matched_topics = []
    for topic, data in QA_KNOWLEDGE.items():
        for keyword in data["keywords"]:
            if keyword.lower() in question_lower:
                matched_topics.append(topic)
                break
    
    # マッチしたトピックがある場合
    if matched_topics:
        # 最初にマッチしたトピックを使用
        topic = matched_topics[0]
        data = QA_KNOWLEDGE[topic]
        
        # 例外キーワードチェック（低信頼度トリガー）
        exception_keywords = ["例外", "特別", "特殊", "例外", "exception", "special", "unusual", "complex"]
        has_exception = any(kw in question_lower for kw in exception_keywords)
        
        # 複雑な条件分岐を示すキーワード
        complex_keywords = ["場合", "条件", "if", "when", "depending", "case"]
        has_complex = any(kw in question_lower for kw in complex_keywords)
        
        confidence = "low" if (has_exception or has_complex) else data["confidence"]
        
        return QAResponse(
            answer_text=data["answer"],
            confidence=confidence,
            references=data["references"],
            suggested_actions=["escalate"] if confidence == "low" else []
        )
    
    # マッチしない場合（低信頼度）
    return QAResponse(
        answer_text="申し訳ございませんが、ご質問の内容について確実な回答を提供できません。\n\n人事部門にエスカレートして、適切な対応をさせていただきます。",
        confidence="low",
        references=[],
        suggested_actions=["escalate"]
    )

