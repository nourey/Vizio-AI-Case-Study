import ast
import re
from typing import Any, Dict, Optional, Tuple

import pandas as pd

CANONICAL_COLUMNS = [
    "source",
    "source_job_id",
    "job_url",
    "apply_url",
    "title",
    "company_name",
    "company_url",
    "company_source_id",
    "description_text",
    "date_posted",
    "application_deadline",
    "location_raw",
    "city_or_region",
    "country",
    "location_type_normalized",
    "employment_type_raw",
    "employment_type_normalized",
    "seniority_raw",
    "seniority_normalized",
    "salary_raw",
    "salary_currency",
    "salary_min",
    "salary_max",
    "salary_period",
    "industry_raw",
    "industry_normalized",
    "skills_raw",
    "is_easy_apply",
    "is_featured",
    "source_metadata",
]

MAPPING_DICT_DICE = {
    "source_job_id": "id",
    "job_url": "url",
    "apply_url": "applyUrl",
    "title": "title",
    "company_name": "companyName",
    "description_text": "description",
    "date_posted": "datePosted",
    "application_deadline": "lastApplicationDate",
    "location_raw": "location",
    "country": "country",
    "salary_raw": "salaryRaw",
    "salary_period": "salaryRawUnit",
    "skills_raw": "skills",
}

SALARY_PATTERN = re.compile(
    r"^[A-Z]{3}\s+([\d,]+(?:\.\d+)?)\s+-\s+([\d,]+(?:\.\d+)?)\s+per\s+\w+$"
)

SENIORITY_RULES = [
    (r"\bsenior\s+principal\b|\bprincipal\s+engineer\b|\bprincipal\b", "principal"),
    (r"\bstaff\b", "staff"),
    (r"\blead\b|\bteam\s+lead\b|\btech\s+lead\b", "lead"),
    (r"\bdirector\b|\bhead\b", "director"),
    (r"\bmanager\b", "manager"),
    (r"\bsenior\b|\bsr\.?\b", "senior"),
    (r"\bmid\b|\bmid-level\b|\bintermediate\b", "mid"),
    (r"\bjunior\b|\bjr\.?\b|\bentry[- ]level\b", "junior"),
    (r"\btrainee\b", "trainee"),
    (r"\bintern\b|\binternship\b", "intern"),
]


def _null_safe(value: Any) -> Any:
    return None if pd.isna(value) else value


def _parse_location_detail(value: Any) -> Dict[str, Any]:
    if pd.isna(value):
        return {}
    if isinstance(value, dict):
        return value
    if isinstance(value, str):
        try:
            parsed = ast.literal_eval(value)
            if isinstance(parsed, dict):
                return parsed
        except (ValueError, SyntaxError):
            pass
    return {}


def _build_employment_fields(df: pd.DataFrame) -> Tuple[pd.Series, pd.Series]:
    def build_raw(contract_type: Any, position_schedule: Any) -> Optional[str]:
        contract_type = None if pd.isna(contract_type) else str(contract_type).strip()
        position_schedule = None if pd.isna(position_schedule) else str(position_schedule).strip()

        parts = []
        if contract_type:
            parts.append(f"contractType={contract_type}")
        if position_schedule:
            parts.append(f"positionSchedule={position_schedule}")
        return "; ".join(parts) if parts else None

    def normalize(contract_type: Any, position_schedule: Any) -> str:
        contract_type = None if pd.isna(contract_type) else str(contract_type).strip().upper()
        position_schedule = None if pd.isna(position_schedule) else str(position_schedule).strip().upper()

        if contract_type == "CONTRACT":
            return "contract"
        if contract_type == "DIRECT_HIRE_CONTRACT":
            return "contract"
        if position_schedule == "PART_TIME":
            return "part_time"
        if contract_type == "DIRECT_HIRE" and position_schedule == "FULL_TIME":
            return "full_time"
        if contract_type == "DIRECT_HIRE":
            return "full_time"
        return "unknown"

    raw = df.apply(lambda row: build_raw(row.get("contractType"), row.get("positionSchedule")), axis=1)
    normalized = df.apply(lambda row: normalize(row.get("contractType"), row.get("positionSchedule")), axis=1)
    return raw, normalized


def _build_location_type(df: pd.DataFrame) -> pd.Series:
    def normalize_location_type(remote: Any, onsite: Any, hybrid: Any) -> str:
        remote = False if pd.isna(remote) else bool(remote)
        onsite = False if pd.isna(onsite) else bool(onsite)
        hybrid = False if pd.isna(hybrid) else bool(hybrid)

        if hybrid:
            return "hybrid"
        if remote and onsite:
            return "hybrid"
        if remote:
            return "remote"
        if onsite:
            return "onsite"
        return "unknown"

    return df.apply(
        lambda row: normalize_location_type(row.get("remote"), row.get("onsite"), row.get("hybrid")),
        axis=1,
    )


def _extract_salary_min(value: Any) -> Optional[float]:
    if pd.isna(value):
        return None
    match = SALARY_PATTERN.match(str(value).strip())
    if not match:
        return None
    return float(match.group(1).replace(",", ""))


def _extract_salary_max(value: Any) -> Optional[float]:
    if pd.isna(value):
        return None
    match = SALARY_PATTERN.match(str(value).strip())
    if not match:
        return None
    return float(match.group(2).replace(",", ""))


def _normalize_seniority_from_title(title: Any) -> Optional[str]:
    if pd.isna(title):
        return None

    text = str(title).strip().lower()
    for pattern, label in SENIORITY_RULES:
        if re.search(pattern, text):
            return label
    return None


def _build_source_metadata(df: pd.DataFrame) -> pd.Series:
    return df.apply(
        lambda row: {
            "dateUpdated": _null_safe(row.get("dateUpdated")),
            "companyLogo": _null_safe(row.get("companyLogo")),
            "descriptionHtml": _null_safe(row.get("descriptionHtml")),
            "locationDetail": _null_safe(row.get("locationDetail")),
            "remote": _null_safe(row.get("remote")),
            "onsite": _null_safe(row.get("onsite")),
            "hybrid": _null_safe(row.get("hybrid")),
            "contractType": _null_safe(row.get("contractType")),
            "positionSchedule": _null_safe(row.get("positionSchedule")),
        },
        axis=1,
    )


def transform_dice(dataset_dice_jobs: pd.DataFrame) -> pd.DataFrame:
    df = dataset_dice_jobs.copy()

    dice_unified = pd.DataFrame(index=df.index)
    dice_unified["source"] = "dice"

    for col in CANONICAL_COLUMNS:
        if col == "source":
            continue
        if col in MAPPING_DICT_DICE:
            dice_unified[col] = df[MAPPING_DICT_DICE[col]]
        else:
            dice_unified[col] = None

    parsed_location = df["locationDetail"].apply(_parse_location_detail)
    dice_unified["city_or_region"] = parsed_location.apply(lambda x: x.get("city") or x.get("state"))
    dice_unified["country"] = dice_unified["country"].fillna(parsed_location.apply(lambda x: x.get("country")))

    (
        dice_unified["employment_type_raw"],
        dice_unified["employment_type_normalized"],
    ) = _build_employment_fields(df)

    dice_unified["location_type_normalized"] = _build_location_type(df)
    dice_unified["seniority_raw"] = df["title"]
    dice_unified["seniority_normalized"] = dice_unified["seniority_raw"].apply(_normalize_seniority_from_title)

    dice_unified["salary_currency"] = df["id"].apply(
        lambda x: "CAD" if x == "d87a9d27-f2d1-4ded-97af-864d94b808e9" else "USD"
    )
    dice_unified["salary_min"] = df["salaryRaw"].apply(_extract_salary_min)
    dice_unified["salary_max"] = df["salaryRaw"].apply(_extract_salary_max)

    dice_unified["source_metadata"] = _build_source_metadata(df)

    return dice_unified[CANONICAL_COLUMNS]


def load_and_transform(csv_path: str = "csv/dataset_dice_jobs.csv") -> pd.DataFrame:
    dataset_dice_jobs = pd.read_csv(csv_path)
    return transform_dice(dataset_dice_jobs)


if __name__ == "__main__":
    df = load_and_transform()
    print(df.head())

