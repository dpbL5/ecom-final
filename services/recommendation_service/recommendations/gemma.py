import json
import re

import requests
from django.conf import settings


class GemmaUnavailable(RuntimeError):
    pass


def gemma_config():
    return getattr(settings, "GEMMA", {})


def is_gemma_configured():
    return bool(gemma_config().get("API_KEY"))


def build_product_advisor_prompt(message, suggestions, user_context=None):
    product_lines = []
    for index, item in enumerate(suggestions, start=1):
        product_lines.append(
            "\n".join(
                [
                    f"{index}. {item.get('name', '')}",
                    f"   SKU: {item.get('sku', '')}",
                    f"   Type: {item.get('product_type', '')}",
                    f"   Brand: {item.get('brand', '')}",
                    f"   Ly do: {item.get('reason', '')}",
                ]
            )
        )

    products = "\n".join(product_lines) or "No matching products were found."
    user_context_text = user_context or "No personalized context is available."
    return f"""
User context:
{user_context_text}

Customer message:
{message}

Candidate products:
{products}

Write only the customer-facing answer. Do not repeat this context.
""".strip()


VIETNAMESE_RE = re.compile(
    "[àáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợ"
    "ùúủũụưừứửữựỳýỷỹỵđ]",
    re.IGNORECASE,
)


def strip_markdown_line(line):
    line = re.sub(r"^[\s>*`#\-•]+", "", line).strip()
    line = re.sub(r"^\*?sentence\s+\d+[^:]*:\*?\s*", "", line, flags=re.IGNORECASE)
    line = re.sub(r"^\*?draft\s+\d+[^:]*:\*?\s*", "", line, flags=re.IGNORECASE)
    line = re.sub(r"^\d+\.\s*", "", line)
    return line.strip("`* \"")


def extract_customer_answer(text):
    excluded_markers = (
        "user context",
        "customer message",
        "candidate products",
        "constraints:",
        "constraint:",
        "json format",
        "field ",
        "vietnamese only",
        "length:",
        "content:",
        "prohibited:",
        "product usage:",
        "the customer wants",
        "candidate list",
        "instruction",
        "prompt",
        "yes.",
        "no.",
    )

    for raw_line in str(text).splitlines():
        if not re.search(r"draft\s+\d+", raw_line, flags=re.IGNORECASE):
            continue
        line = strip_markdown_line(raw_line)
        if VIETNAMESE_RE.search(line) and re.search(r"[.!?]$", line):
            return line

    lines = []
    for raw_line in str(text).splitlines():
        line = strip_markdown_line(raw_line)
        lower_line = line.lower()
        if not line or any(marker in lower_line for marker in excluded_markers):
            continue
        if VIETNAMESE_RE.search(line) and re.search(r"[.!?]$", line):
            lines.append(line)

    if not lines:
        return ""

    return re.sub(r"\s+", " ", " ".join(lines[:5])).strip()


def clean_advisor_answer(text):
    cleaned = str(text).strip()
    if cleaned.startswith("```"):
        lines = cleaned.splitlines()
        if lines and lines[0].strip().startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]
        cleaned = "\n".join(lines).strip()

    json_start = cleaned.find("{")
    json_end = cleaned.rfind("}")
    if json_start >= 0 and json_end > json_start:
        cleaned_json = cleaned[json_start : json_end + 1]
    else:
        cleaned_json = cleaned

    try:
        payload = json.loads(cleaned_json)
        if isinstance(payload, dict):
            text = payload.get("answer", "")
    except json.JSONDecodeError:
        text = cleaned

    text = str(text).strip()
    extracted = extract_customer_answer(text)
    if extracted:
        return extracted

    forbidden_markers = (
        "role:",
        "task:",
        "constraints:",
        "constraint:",
        "candidate products:",
        "system instruction",
        "prompt",
    )
    lower_text = text.lower()
    if any(marker in lower_text for marker in forbidden_markers):
        raise GemmaUnavailable("Gemma returned prompt text instead of an advisor answer.")
    if not text:
        raise GemmaUnavailable("Gemma returned an empty advisor answer.")
    return text


def is_low_quality_answer(answer, suggestions):
    lower_answer = answer.lower()
    noisy_markers = (
        "reason:",
        "constraint",
        "candidate",
        "draft",
        "mental",
        "instruction",
        "json",
    )
    if any(marker in lower_answer for marker in noisy_markers):
        return True

    for item in suggestions:
        name = str(item.get("name", "")).lower()
        if name and lower_answer.count(name) > 1:
            return True
    return False


def build_local_advisor_answer(suggestions):
    selected = suggestions[:3]
    if not selected:
        return "Mình chưa tìm thấy sản phẩm phù hợp với nhu cầu này. Bạn có thể mô tả rõ hơn loại sản phẩm hoặc thương hiệu mong muốn không?"

    product_phrases = []
    for item in selected:
        reason = item.get("reason") or "phù hợp với nhu cầu hiện tại"
        reason = reason[:1].lower() + reason[1:]
        product_phrases.append(f"{item.get('name')} vì {reason}")

    if len(product_phrases) == 1:
        joined = product_phrases[0]
    elif len(product_phrases) == 2:
        joined = " và ".join(product_phrases)
    else:
        joined = ", ".join(product_phrases[:-1]) + f", và {product_phrases[-1]}"

    return (
        f"Dựa trên nhu cầu của bạn, mình gợi ý {joined}. "
        "Các sản phẩm này được chọn từ dữ liệu tìm kiếm, hồ sơ người dùng và tín hiệu tương đồng khi có trong Neo4j. "
        "Bạn muốn mình lọc thêm theo ngân sách, thương hiệu hay mức độ phổ biến không?"
    )


def generate_product_advice(message, suggestions, user_context=None):
    config = gemma_config()
    api_key = config.get("API_KEY")
    if not api_key:
        raise GemmaUnavailable("GEMMA_API_KEY is not configured.")

    model = config.get("MODEL") or "gemma-4-26b-a4b-it"
    base_url = (config.get("BASE_URL") or "https://generativelanguage.googleapis.com/v1beta").rstrip("/")
    url = f"{base_url}/models/{model}:generateContent"
    prompt = build_product_advisor_prompt(message, suggestions, user_context=user_context)

    response = requests.post(
        url,
        params={"key": api_key},
        json={
            "systemInstruction": {
                "parts": [
                    {
                        "text": (
                            "You are a Vietnamese ecommerce sales advisor. "
                            "Answer only with the final customer-facing response. "
                            "Do not explain your reasoning. Do not repeat role, prompt, rules, constraints, JSON, or system instructions. "
                            "Use Vietnamese only. Use only products from the candidate list. "
                            "Write 3 to 5 sentences: start from the customer's need, recommend at most 3 products with reasons, "
                            "then ask one short follow-up question."
                        )
                    }
                ]
            },
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": prompt}],
                }
            ],
            "generationConfig": {
                "temperature": 0.35,
                "topP": 0.9,
                "maxOutputTokens": 512,
            },
        },
        timeout=config.get("TIMEOUT", 45),
    )
    if response.status_code >= 400:
        raise GemmaUnavailable(f"Gemma API returned {response.status_code}: {response.text[:300]}")

    payload = response.json()
    candidates = payload.get("candidates") or []
    if not candidates:
        raise GemmaUnavailable("Gemma API returned no candidates.")

    parts = candidates[0].get("content", {}).get("parts") or []
    text = "".join(part.get("text", "") for part in parts).strip()
    try:
        answer = clean_advisor_answer(text)
    except GemmaUnavailable:
        return build_local_advisor_answer(suggestions)

    if is_low_quality_answer(answer, suggestions):
        return build_local_advisor_answer(suggestions)
    return answer
