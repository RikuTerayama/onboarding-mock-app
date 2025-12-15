from __future__ import annotations
from dataclasses import dataclass
from datetime import date, timedelta
from typing import List, Dict, Any

# Embedded templates for executive mock (replace with YAML later)
# Structure: {template_key: {lang: {tasks: [...], plan: {...}}}}
TEMPLATES: Dict[str, Dict[str, Dict[str, Any]]] = {
    "general_newgrad": {
        "en": {
            "tasks": [
                {"owner": "employee", "title": "Complete HR paperwork", "desc": "Fill in onboarding forms and submit required documents.", "offset": 0},
                {"owner": "employee", "title": "Read company handbook", "desc": "Review key policies and working norms.", "offset": 2},
                {"owner": "manager", "title": "Set up first-week agenda", "desc": "Align meetings, buddy assignment, and access requests.", "offset": -3},
            ],
            "plan": {
                "employee": {
                    "day30": "Understand team mission, tools, and workflows. Deliver a small starter task.",
                    "day60": "Own a scoped workstream end-to-end. Start proposing improvements.",
                    "day90": "Operate independently on core responsibilities. Identify growth goals with manager."
                },
                "manager": {
                    "day30": "Set weekly 1:1 cadence; ensure environment setup; clarify expectations.",
                    "day60": "Review progress vs role expectations; assign a medium-sized project.",
                    "day90": "Performance checkpoint and growth plan; calibrate responsibilities."
                }
            }
        },
        "ja": {
            "tasks": [
                {"owner": "employee", "title": "人事書類を完了", "desc": "オンボーディングフォームに記入し、必要な書類を提出してください。", "offset": 0},
                {"owner": "employee", "title": "会社ハンドブックを読む", "desc": "重要なポリシーと業務規範を確認してください。", "offset": 2},
                {"owner": "manager", "title": "初週のアジェンダを設定", "desc": "ミーティング、バディ割り当て、アクセスリクエストを調整してください。", "offset": -3},
            ],
            "plan": {
                "employee": {
                    "day30": "チームのミッション、ツール、ワークフローを理解する。小さなスタートタスクを提供する。",
                    "day60": "スコープ付きワークストリームをエンドツーエンドで所有する。改善を提案し始める。",
                    "day90": "コア責任において独立して運用する。マネージャーと成長目標を特定する。"
                },
                "manager": {
                    "day30": "週次1対1のリズムを設定; 環境セットアップを確保; 期待値を明確にする。",
                    "day60": "役割期待値に対する進捗を確認; 中規模プロジェクトを割り当てる。",
                    "day90": "パフォーマンスチェックポイントと成長計画; 責任を調整する。"
                }
            }
        }
    },
    "general_mid": {
        "en": {
            "tasks": [
                {"owner": "employee", "title": "Confirm role expectations", "desc": "Align your 30/60/90-day objectives with the manager.", "offset": 0},
                {"owner": "manager", "title": "Introduce key stakeholders", "desc": "Arrange introductions to cross-functional partners.", "offset": 3},
            ],
            "plan": {
                "employee": {
                    "day30": "Map stakeholders, understand current projects, deliver quick wins.",
                    "day60": "Lead a key initiative and share progress updates.",
                    "day90": "Drive measurable impact and propose next-quarter roadmap."
                },
                "manager": {
                    "day30": "Clarify authority/decision boundaries; provide context and priorities.",
                    "day60": "Remove blockers and validate impact metrics.",
                    "day90": "Set next goals and confirm long-term ownership areas."
                }
            }
        },
        "ja": {
            "tasks": [
                {"owner": "employee", "title": "役割期待値を確認", "desc": "30/60/90日の目標をマネージャーと調整してください。", "offset": 0},
                {"owner": "manager", "title": "主要ステークホルダーを紹介", "desc": "クロスファンクショナルパートナーへの紹介を手配してください。", "offset": 3},
            ],
            "plan": {
                "employee": {
                    "day30": "ステークホルダーをマッピングし、現在のプロジェクトを理解し、クイックウィンを提供する。",
                    "day60": "主要なイニシアチブをリードし、進捗更新を共有する。",
                    "day90": "測定可能な影響を推進し、次四半期のロードマップを提案する。"
                },
                "manager": {
                    "day30": "権限/決定の境界を明確にする; コンテキストと優先順位を提供する。",
                    "day60": "ブロッカーを削除し、影響指標を検証する。",
                    "day90": "次の目標を設定し、長期的な所有領域を確認する。"
                }
            }
        }
    },
    "eng_newgrad": {
        "en": {
            "tasks": [
                {"owner": "employee", "title": "Set up dev environment", "desc": "Install required tools, access repos, run the project locally.", "offset": 0},
                {"owner": "employee", "title": "Complete security training", "desc": "Finish required security modules and acknowledge policies.", "offset": 7},
                {"owner": "manager", "title": "Assign onboarding starter ticket", "desc": "Pick a well-scoped ticket suitable for first 2 weeks.", "offset": 1},
            ],
            "plan": {
                "employee": {
                    "day30": "Ship first small PR and understand the deployment flow.",
                    "day60": "Own a feature slice and participate in code reviews.",
                    "day90": "Become dependable on a component; contribute to design discussions."
                },
                "manager": {
                    "day30": "Ensure access + environment; set mentorship plan.",
                    "day60": "Expand responsibilities; ensure feedback loop.",
                    "day90": "Evaluate readiness for deeper ownership if applicable."
                }
            }
        },
        "ja": {
            "tasks": [
                {"owner": "employee", "title": "開発環境をセットアップ", "desc": "必要なツールをインストールし、リポジトリにアクセスし、プロジェクトをローカルで実行してください。", "offset": 0},
                {"owner": "employee", "title": "セキュリティ研修を完了", "desc": "必要なセキュリティモジュールを完了し、ポリシーを承認してください。", "offset": 7},
                {"owner": "manager", "title": "オンボーディング開始チケットを割り当て", "desc": "最初の2週間に適した適切にスコープされたチケットを選択してください。", "offset": 1},
            ],
            "plan": {
                "employee": {
                    "day30": "最初の小さなPRを出荷し、デプロイフローを理解する。",
                    "day60": "機能スライスを所有し、コードレビューに参加する。",
                    "day90": "コンポーネントで信頼できるようになる; 設計ディスカッションに貢献する。"
                },
                "manager": {
                    "day30": "アクセス + 環境を確保; メンターシップ計画を設定する。",
                    "day60": "責任を拡大; フィードバックループを確保する。",
                    "day90": "該当する場合、より深い所有権の準備状況を評価する。"
                }
            }
        }
    },
    "cs_mid": {
        "en": {
            "tasks": [
                {"owner": "employee", "title": "Review support playbook", "desc": "Learn escalation policies and standard response templates.", "offset": 0},
                {"owner": "manager", "title": "Shadow sessions", "desc": "Set up 3 shadowing sessions for the first 2 weeks.", "offset": 1},
            ],
            "plan": {
                "employee": {
                    "day30": "Handle common tickets with supervision; learn product basics.",
                    "day60": "Own a queue segment; improve macros/templates.",
                    "day90": "Lead complex cases; propose CS process improvements."
                },
                "manager": {
                    "day30": "Set quality bar and review loop.",
                    "day60": "Calibrate performance metrics and ownership.",
                    "day90": "Confirm long-term focus area and growth track."
                }
            }
        },
        "ja": {
            "tasks": [
                {"owner": "employee", "title": "サポートプレイブックを確認", "desc": "エスカレーションポリシーと標準応答テンプレートを学習してください。", "offset": 0},
                {"owner": "manager", "title": "シャドウセッション", "desc": "最初の2週間で3つのシャドウセッションを設定してください。", "offset": 1},
            ],
            "plan": {
                "employee": {
                    "day30": "監督下で一般的なチケットを処理; 製品の基本を学習する。",
                    "day60": "キューセグメントを所有; マクロ/テンプレートを改善する。",
                    "day90": "複雑なケースをリード; CSプロセスの改善を提案する。"
                },
                "manager": {
                    "day30": "品質基準とレビーループを設定する。",
                    "day60": "パフォーマンス指標と所有権を調整する。",
                    "day90": "長期的な焦点領域と成長トラックを確認する。"
                }
            }
        }
    }
}

DEFAULT_TEMPLATE = "general_newgrad"

@dataclass
class GeneratedTask:
    owner: str
    title: str
    description: str
    due_date: date

def generate(role: str, grade: str, start_date: date, lang: str = "en") -> tuple[List[GeneratedTask], Dict[str, Dict[str, str]], str]:
    key = f"{role}_{grade}"
    template_data = TEMPLATES.get(key) or TEMPLATES.get(DEFAULT_TEMPLATE)
    
    # Get language-specific data, fallback to 'en' if lang not available
    lang_data = template_data.get(lang) or template_data.get("en")
    chosen = key if key in TEMPLATES else DEFAULT_TEMPLATE

    tasks: List[GeneratedTask] = []
    for t in lang_data["tasks"]:
        due = start_date + timedelta(days=int(t["offset"]))
        tasks.append(GeneratedTask(owner=t["owner"], title=t["title"], description=t["desc"], due_date=due))

    plan = lang_data["plan"]
    return tasks, plan, chosen
