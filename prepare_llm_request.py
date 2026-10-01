import json
from pathlib import Path


SUMMARY_FILE = Path("daily_summary.json")
OUTPUT_FILE = Path("llm_request.json")


SYSTEM_PROMPT = """
你是一个工作日志分析助手。

必须遵守以下规则：
1. 只能使用用户提供的记录，不能编造事实。
2. 没有查询到记录，不等于人员没有提交。
3. 如果材料不足，必须明确写入 missing_materials。
4. 每项成果、问题或风险必须保留对应的 source_record_id。
5. 分析结果只是待确认结果，不能标记为正式结果。
6. 必须只输出 JSON，不得输出 Markdown 或额外说明。
""".strip()


OUTPUT_SCHEMA = {
    "type": "object",
    "required": [
        "overall_summary",
        "achievements",
        "risks",
        "missing_materials",
        "confirmation_status",
    ],
    "properties": {
        "overall_summary": {
            "type": "string",
            "description": "对现有材料的整体概括",
        },
        "achievements": {
            "type": "array",
            "items": {
                "type": "object",
                "required": [
                    "description",
                    "source_record_ids",
                ],
                "properties": {
                    "description": {
                        "type": "string",
                    },
                    "source_record_ids": {
                        "type": "array",
                        "items": {"type": "string"},
                    },
                },
            },
        },
        "risks": {
            "type": "array",
            "items": {
                "type": "object",
                "required": [
                    "description",
                    "source_record_ids",
                ],
                "properties": {
                    "description": {
                        "type": "string",
                    },
                    "source_record_ids": {
                        "type": "array",
                        "items": {"type": "string"},
                    },
                },
            },
        },
        "missing_materials": {
            "type": "array",
            "items": {"type": "string"},
        },
        "confirmation_status": {
            "type": "string",
            "enum": ["pending_confirmation"],
        },
    },
}


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


def build_user_prompt(summary):
    material_json = json.dumps(
        summary,
        ensure_ascii=False,
        indent=2,
    )
    schema_json = json.dumps(
        OUTPUT_SCHEMA,
        ensure_ascii=False,
        indent=2,
    )

    return f"""
请分析下面的工作日志材料。

分析要求：
1. 概括目前已经完成的工作。
2. 找出材料中明确出现的问题和风险。
3. 不推测没有提供的信息。
4. 引用成果或风险时，填写对应的 source_record_id。
5. 输出结果必须符合指定 JSON Schema。
6. confirmation_status 必须是 pending_confirmation。

必须严格按照下面的 JSON Schema 输出，所有 required 字段都必须出现；
没有成果或风险时，对应字段也要返回空数组：

{schema_json}

工作日志材料：

{material_json}
""".strip()


def main():
    summary = load_summary()

    request_data = {
        "system_prompt": SYSTEM_PROMPT,
        "user_prompt": build_user_prompt(summary),
        "output_schema": OUTPUT_SCHEMA,
    }

    with OUTPUT_FILE.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            request_data,
            file,
            ensure_ascii=False,
            indent=2,
        )

    print("LLM 请求材料生成成功！")
    print("输入材料：", SUMMARY_FILE)
    print("输出文件：", OUTPUT_FILE)
    print("确认状态要求：pending_confirmation")
    print("尚未调用任何模型，也没有产生费用。")


if __name__ == "__main__":
    main()
