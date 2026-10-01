import json
from pathlib import Path


SUMMARY_FILE = Path("daily_summary.json")
OUTPUT_FILE = Path("llm_result_mock.json")

REQUIRED_FIELDS = {
    "overall_summary",
    "achievements",
    "risks",
    "missing_materials",
    "confirmation_status",
}

RISK_KEYWORDS = [
    "异常",
    "失败",
    "超时",
    "风险",
    "错误",
    "未完成",
]


def load_summary():
    if not SUMMARY_FILE.exists():
        raise RuntimeError(
            "没有找到 daily_summary.json，"
            "请先运行 build_summary.py"
        )

    with SUMMARY_FILE.open(
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


def build_mock_result(summary):
    overall = summary.get("overall", {})
    records = summary.get("records", [])

    achievements = []
    risks = []

    for record in records:
        source_id = record.get("source_record_id")
        result_source = record.get("成果出处")
        log_content = record.get("日志内容") or ""

        if result_source:
            achievements.append(
                {
                    "description": (
                        f"{record.get('姓名')}：{result_source}"
                    ),
                    "source_record_ids": [source_id],
                }
            )

        if any(
            keyword in log_content
            for keyword in RISK_KEYWORDS
        ):
            risks.append(
                {
                    "description": log_content,
                    "source_record_ids": [source_id],
                }
            )

    return {
        "overall_summary": (
            f"当前材料共涉及 "
            f"{overall.get('人数', 0)} 人、"
            f"{overall.get('人次', 0)} 人次，"
            f"其中已交记录 "
            f"{overall.get('已交记录数', 0)} 条。"
        ),
        "achievements": achievements,
        "risks": risks,
        "missing_materials": [
            "缺少完整人员名单，无法判断哪些人员未提交",
        ],
        "confirmation_status": "pending_confirmation",
    }


def validate_result(result):
    missing_fields = REQUIRED_FIELDS - set(result.keys())

    if missing_fields:
        raise RuntimeError(
            "输出缺少字段："
            + "、".join(sorted(missing_fields))
        )

    if result["confirmation_status"] != "pending_confirmation":
        raise RuntimeError(
            "confirmation_status 必须是 "
            "pending_confirmation"
        )

    if not isinstance(result["achievements"], list):
        raise RuntimeError("achievements 必须是数组")

    if not isinstance(result["risks"], list):
        raise RuntimeError("risks 必须是数组")

    for item in result["achievements"] + result["risks"]:
        source_ids = item.get("source_record_ids")

        if not isinstance(source_ids, list):
            raise RuntimeError(
                "每项分析必须包含 source_record_ids 数组"
            )


def main():
    summary = load_summary()
    result = build_mock_result(summary)
    validate_result(result)

    with OUTPUT_FILE.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            result,
            file,
            ensure_ascii=False,
            indent=2,
        )

    print("模拟 LLM 输出生成成功！")
    print("结构校验：通过")
    print("成果数量：", len(result["achievements"]))
    print("风险数量：", len(result["risks"]))
    print(
        "确认状态：",
        result["confirmation_status"],
    )
    print("结果文件：", OUTPUT_FILE)
    print()
    print("注意：这是模拟结果，不是真实模型分析。")


if __name__ == "__main__":
    main()