import re
import shutil
import subprocess
import tempfile
from pathlib import Path


swedish_to_english = {
    "gronkalsbiff": "kale patty",
    "grönkålsbiff": "kale patty",
    "hamburgerbrod": "hamburger bread",
    "hamburgerbröd": "hamburger bread",
    "vegoschnitzel": "veggie schnitzel",
    "tomat runda import": "tomato",
    "tomat": "tomato",
    "morot": "carrot",
    "potatis sot": "sweet potato",
    "potatis söt": "sweet potato",
    "potatis": "potato",
    "brioche": "brioche",
    "frukt & mandel": "fruit and almond chocolate",
    "chokladkaka mjolk": "milk chocolate bar",
    "chokladkaka mjölk": "milk chocolate bar",
    "biscoff crunchy": "biscoff spread",
    "chokladkaka daim": "daim chocolate bar",
    "ostbagar cheddar": "cheese puffs",
    "ostbågar cheddar": "cheese puffs",
    "gurka sverige st": "cucumber",
    "gurka": "cucumber",
    "tuggummi": "chewing gum",
    "4 cheese": "four cheese pizza",
    "kondenserad mjolk": "condensed milk",
    "kondenserad mjölk": "condensed milk",
    "cola sockerfri": "sugar-free cola",
    "emd brau": "beer",
    "ewp brau": "beer",
    "poraris sor": "sweet potato",
    "potatis sor": "sweet potato",
    "ruccuen": "chewing gum",
    "tugcuen": "chewing gum",
}


average_grams_per_item = {
    "tomato": 120,
    "carrot": 75,
    "potato": 170,
    "sweet potato": 180,
    "cucumber": 300,
    "hamburger bread": 60,
    "brioche": 80,
    "kale patty": 120,
    "veggie schnitzel": 120,
    "four cheese pizza": 350,
    "beer": 500,
    "sugar-free cola": 2000,
}


skip_patterns = [
    r"^willys\b",
    r"^tel\b",
    r"^org\b",
    r"^\+?pant\b",
    r"rabatt",
    r"willys plus",
    r"^totalt\b",
    r"^mottaget\b",
    r"^mastercard\b",
    r"^kop\b",
    r"^butik\b",
    r"^ref\b",
    r"^tvr\b",
    r"^vr\b",
    r"^mind\b",
    r"^sind\b",
    r"^kontakt",
    r"^moms",
    r"^spara",
    r"^oppettider",
    r"^mand",
    r"^sond",
    r"^valkommen",
    r"^du betjanades",
    r"^kassa",
    r"^laga priser",
    r"^med willys",
    r"^202\d",
    r"^\d+$",
]


simple_grocery_words = {
    "apple",
    "banana",
    "bread",
    "cake",
    "candy",
    "carrot",
    "carrots",
    "cheese",
    "chicken",
    "fish",
    "meat",
    "milk",
    "pie",
    "potato",
    "potatoes",
    "tomato",
    "tomatoes",
    "yogurt",
}


def scan_receipt_or_list_file(file_path: str) -> tuple[str, list[dict]]:
    text = extract_text_from_receipt_file(file_path)
    return text, parse_scanned_receipt_or_list_text(text)


def extract_text_from_receipt_file(file_path: str) -> str:
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(file_path)

    if not shutil.which("tesseract"):
        raise RuntimeError("Tesseract is not installed on this machine.")

    if path.suffix.lower() == ".pdf":
        image_path = render_receipt_pdf_to_image(path)
        return run_image_ocr(image_path)

    return run_image_ocr(path)


def render_receipt_pdf_to_image(pdf_path: Path) -> Path:
    if not shutil.which("qlmanage"):
        raise RuntimeError("PDF receipt scanning requires qlmanage on this machine.")

    tmp_dir = Path(tempfile.mkdtemp(prefix="pantry_receipt_"))
    subprocess.run(
        [
            "qlmanage",
            "-t",
            "-s",
            "2200",
            "-o",
            str(tmp_dir),
            str(pdf_path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    image_path = tmp_dir / f"{pdf_path.name}.png"
    if not image_path.exists():
        raise RuntimeError("Could not render the receipt PDF for OCR.")

    return image_path


def run_image_ocr(image_path: Path) -> str:
    result = subprocess.run(
        ["tesseract", str(image_path), "stdout", "-l", "eng", "--psm", "6"],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout


def parse_scanned_receipt_or_list_text(text: str) -> list[dict]:
    items = []
    pending_item = None
    pending_name = None

    for raw_line in text.splitlines():
        line = clean_line(raw_line)
        if not line or should_skip_line(line):
            continue

        item = parse_willys_receipt_item_line(line)
        if item:
            items.append(item)
            pending_item = item
            pending_name = None
            continue

        item = parse_simple_list_item_line(line)
        if item:
            items.append(item)
            pending_item = item
            pending_name = None
            continue

        detail = parse_quantity_detail(line)
        if detail and (pending_item or pending_name):
            target_item = pending_item

            if pending_name:
                target_item = make_item(pending_name, line)
                items.append(target_item)
                pending_name = None

            target_item["quantity"] = estimate_piece_quantity(
                target_item["item_name"],
                kg=detail.get("kg"),
                grams=detail.get("grams"),
                explicit_count=detail.get("count"),
            )
            continue

        if looks_like_item_name(line):
            pending_name = line
            pending_item = None
            continue

    return merge_duplicate_items(items)


def clean_line(line: str) -> str:
    line = line.strip()
    line = line.replace("é", "e")
    line = re.sub(r"\s+", " ", line)
    return line


def should_skip_line(line: str) -> bool:
    lowered = re.sub(r"^[^a-zåäö0-9]+", "", line.lower()).strip()
    if not re.search(r"[a-zåäö]", lowered):
        return True
    return any(re.search(pattern, lowered) for pattern in skip_patterns)


def parse_quantity_detail(line: str) -> dict | None:
    lowered = line.lower().replace(" ", "")

    kg_match = re.search(r"(\d+,\d+|\d+\.\d+|\d+)kg\*", lowered)
    if kg_match:
        return {"kg": parse_decimal(kg_match.group(1))}

    grams_match = re.search(r"(\d+)g\*", lowered)
    if grams_match:
        return {"grams": float(grams_match.group(1))}

    count_match = re.search(r"(\d+)st\*", lowered)
    if count_match:
        return {"count": int(count_match.group(1))}

    return None


def parse_willys_receipt_item_line(line: str) -> dict | None:
    if not re.search(r"\d+,\d{2}$", line):
        return None

    working = re.sub(r"\s+-?\d+,\d{2}$", "", line).strip()
    working = re.sub(r"^\d+\s+\*\s+", "", working).strip()

    inline_count = None
    count_match = re.search(r"\b(\d+)st\*\d+,\d{2}\b", working.lower())
    if count_match:
        inline_count = int(count_match.group(1))
        working = working[:count_match.start()].strip()

    pack_match = re.search(r"\b\d+(?:,\d+)?\s?cl\s?(\d+)p\b", working.lower())
    if pack_match and not inline_count:
        inline_count = int(pack_match.group(1))

    package_grams = None
    package_kg = None

    kg_match = re.search(r"\b(\d+(?:,\d+)?)\s?kg\b", working.lower())
    if kg_match:
        package_kg = parse_decimal(kg_match.group(1))
        working = re.sub(r"\b\d+(?:,\d+)?\s?kg\b", "", working, flags=re.IGNORECASE).strip()

    grams_match = re.search(r"\b(\d{2,4})\s?g\b", working.lower())
    if grams_match:
        package_grams = float(grams_match.group(1))
        working = re.sub(r"\b\d{2,4}\s?g\b", "", working, flags=re.IGNORECASE).strip()

    working = re.sub(r"\b\d+(?:,\d+)?\s?(?:cl|l|%)\w*\b", "", working, flags=re.IGNORECASE).strip()
    working = re.sub(r"\s+", " ", working)

    if should_skip_line(working) or not looks_like_item_name(working):
        return None

    translated_name = translate_item_name(working)
    quantity = estimate_piece_quantity(
        translated_name,
        kg=package_kg,
        grams=package_grams,
        explicit_count=inline_count,
    )

    return {
        "item_name": translated_name,
        "quantity": quantity,
        "source_text": line,
    }


def parse_simple_list_item_line(line: str) -> dict | None:
    lowered = line.lower().strip()

    if re.search(r"\d+,\d{2}", lowered):
        return None

    if count_numbers(lowered) > 3:
        return None

    name = None
    quantity = None
    divider_match = re.match(r"^(.+?)\s*\|+\s*(\d+(?:[.,]\d+)?)(?:\s+.*)?$", lowered)
    if divider_match:
        name = clean_simple_list_name(divider_match.group(1))
        quantity = parse_decimal(divider_match.group(2))

    if name is None:
        match = re.match(r"^(.+?)\s*[:=-]\s*(\d+(?:[.,]\d+)?)\s*(?:pcs?|st)?$", lowered)
        if match:
            name = clean_simple_list_name(match.group(1))
            quantity = parse_decimal(match.group(2))
        else:
            match = re.match(r"^(.+?)\s+(\d+(?:[.,]\d+)?)(?:\s+\D.*|\s+\d.*)?$", lowered)
            if match:
                name = clean_simple_list_name(match.group(1))
                quantity = parse_decimal(match.group(2))

    if name is None:
        fallback = re.match(r"^([a-zåäö][a-zåäö ]{2,})\s+(?:pcs?|ps|st|x)$", lowered)
        if fallback:
            name = clean_simple_list_name(fallback.group(1))
            quantity = 1.0

    if name is None:
        fallback = re.match(r"^([a-zåäö][a-zåäö ]{2,})\s+[a-z]$", lowered)
        if fallback and normalize_name(fallback.group(1)) in simple_grocery_words:
            name = clean_simple_list_name(fallback.group(1))
            quantity = 1.0

    if name is None and normalize_name(lowered) in simple_grocery_words:
        name = clean_simple_list_name(lowered)
        quantity = 1.0

    if name is None or quantity is None:
        return None

    if quantity <= 0 or quantity > 100:
        return None

    if not looks_like_simple_list_item_name(name):
        return None

    translated_name = translate_item_name(name)
    return {
        "item_name": translated_name,
        "quantity": quantity,
        "source_text": line,
    }


def clean_simple_list_name(name: str) -> str:
    name = re.sub(r"\|+", " ", name)
    name = re.sub(r"\b(item|tem|pcs?|ps|st|ial|ia)\b", "", name, flags=re.IGNORECASE)
    name = re.sub(r"[^a-zåäöA-ZÅÄÖ& ]+", " ", name)
    name = re.sub(r"\s+", " ", name).strip()
    return name


def looks_like_simple_list_item_name(name: str) -> bool:
    normalized = normalize_name(name)

    if len(normalized) < 3:
        return False

    if should_skip_line(normalized):
        return False

    blocked_words = {
        "edit",
        "names",
        "quantities",
        "saving",
        "before",
        "review",
        "receipt",
        "total",
    }
    if normalized in blocked_words:
        return False

    return bool(re.search(r"[a-zåäö]{3,}", normalized))


def count_numbers(value: str) -> int:
    return len(re.findall(r"\d+(?:[.,]\d+)?", value))


def make_item(name: str, source_text: str) -> dict:
    translated_name = translate_item_name(name)
    return {
        "item_name": translated_name,
        "quantity": 1.0,
        "source_text": source_text,
    }


def looks_like_item_name(line: str) -> bool:
    lowered = line.lower()
    if len(line) < 3:
        return False
    if should_skip_line(line):
        return False
    if re.search(r"\d+,\d{2}", lowered) and not re.search(r"[a-zåäö]{3,}", lowered):
        return False
    return bool(re.search(r"[a-zåäö]{3,}", lowered))


def translate_item_name(name: str) -> str:
    normalized = normalize_name(name)

    if normalized in swedish_to_english:
        return swedish_to_english[normalized]

    for swedish, english in swedish_to_english.items():
        if normalized.startswith(swedish):
            return english

    return normalized.replace("&", "and").title().lower()


def normalize_name(name: str) -> str:
    normalized = name.lower()
    normalized = normalized.replace("ö", "o").replace("ä", "a").replace("å", "a")
    normalized = re.sub(r"[^a-z0-9& ]+", "", normalized)
    normalized = re.sub(r"\s+", " ", normalized).strip()
    return normalized


def estimate_piece_quantity(
    item_name: str,
    kg: float | None = None,
    grams: float | None = None,
    explicit_count: int | None = None,
) -> float:
    if explicit_count:
        return float(explicit_count)

    item_weight = average_grams_per_item.get(item_name)
    total_grams = None

    if kg:
        total_grams = kg * 1000
    elif grams:
        total_grams = grams

    if total_grams and item_weight:
        return float(max(1, round(total_grams / item_weight)))

    return 1.0


def merge_duplicate_items(items: list[dict]) -> list[dict]:
    merged = {}

    for item in items:
        name = item["item_name"]
        if name not in merged:
            merged[name] = item.copy()
            continue

        merged[name]["quantity"] += item["quantity"]
        merged[name]["source_text"] += f"; {item['source_text']}"

    return list(merged.values())


def parse_decimal(value: str) -> float:
    return float(value.replace(",", "."))
