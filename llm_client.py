import json
import os

import requests
from dotenv import load_dotenv

from mock_llm import build_mock_result, validate_result
from prepare_llm_request import (
    OUTPUT_SCHEMA,
    SYSTEM_PROMPT,
    build_user_prompt,
)


load_dotenv()

LLM_MODE = (os.getenv("LLM_MODE") or "mock").strip().lower()
LLM_API_URL = (os.getenv("LLM_API_URL") or "").strip()
LLM_API_KEY = (os.getenv("LLM_API_KEY") or "").strip()
LLM_MODEL = (os.getenv("LLM_MODEL") or "").strip()


def build_llm_request(summary):
    return {
        "system_prompt": SYSTEM_PROMPT,
        "user_prompt": build_user_prompt(summary),
        "output_schema": OUTPUT_SCHEMA,
    }


def require_live_configuration():
    required = {
        "LLM_API_URL": LLM_API_URL,
        "LLM_API_KEY": LLM_API_KEY,
        "LLM_MODEL": LLM_MODEL,
    }
    missing = [
        name
        for name, value in required.items()
        if not value
    ]

    if missing:
        raise RuntimeError(
            "LLM_MODE=live，但缺少配置："
            + "、".join(missing)
        )


def parse_model_content(content):
    if not isinstance(content, str) or not content.strip():
        raise RuntimeError("模型没有返回有效文本")

    cleaned = content.strip()

    if cleaned.startswith("```json") and cleaned.endswith("```"):
        cleaned = cleaned[7:-3].strip()
    elif cleaned.startswith("```") and cleaned.endswith("```"):
        cleaned = cleaned[3:-3].strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as error:
        raise RuntimeError(
            f"模型没有返回有效 JSON：{error}"
        ) from error


def call_live_llm(request_data):
    require_live_configuration()

    response = requests.post(
        LLM_API_URL,
        headers={
            "Authorization": f"Bearer {LLM_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": LLM_MODEL,
            "messages": [
                {
                    "role": "system",
                    "content": request_data["system_prompt"],
                },
                {
                    "role": "user",
                    "content": request_data["user_prompt"],
                },
            ],
            "temperature": 0.2,
            "response_format": {"type": "json_object"},
        },
        timeout=90,
    )

    try:
        response_data = response.json()
    except ValueError as error:
        raise RuntimeError(
            f"模型接口返回非 JSON 内容：HTTP {response.status_code}"
        ) from error

    if response.status_code != 200:
        error_message = response_data.get("error", response_data)
        raise RuntimeError(
            f"模型接口失败：HTTP {response.status_code}，"
            f"错误：{error_message}"
        )

    try:
        content = response_data["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as error:
        raise RuntimeError(
            "模型接口响应中缺少 choices[0].message.content"
        ) from error

    result = parse_model_content(content)
    validate_result(result)
    return result


def analyze_summary(summary):
    request_data = build_llm_request(summary)

    if LLM_MODE == "mock":
        result = build_mock_result(summary)
        validate_result(result)
        return request_data, result, "mock"

    if LLM_MODE == "live":
        result = call_live_llm(request_data)
        return request_data, result, "live"

    raise RuntimeError(
        "LLM_MODE 只能是 mock 或 live"
    )
