"""Clean Naukri transform script derived from the final notebook."""

from __future__ import annotations

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

MAPPING_DICT_NAUKRI = {
    "source_job_id": "jobId",
    "job_url": "jdURL",
    "title": "title",
    "company_name": "companyName",
    "company_source_id": "companyId",
    "description_text": "jobDescription",
    "date_posted": "createdDate",
    "location_raw": "location",
    "employment_type_raw": "jobType",
    "salary_currency": "currency",
    "skills_raw": "tagsAndSkills",
}

NAUKRI_METADATA_COLS = [
    "footerPlaceholderLabel",
    "footerPlaceholderColor",
    "isSaved",
    "showMultipleApply",
    "groupId",
    "isTopGroup",
    "hiringFor",
    "consultant",
    "hideClientName",
    "mode",
    "board",
    "experienceText",
    "minimumExperience",
    "maximumExperience",
    "saved",
    "experience",
    "salary",
    "companyJobsUrl",
    "ambitionBoxData",
    "vacancy",
    "clientHeadline",
    "brandingTags",
    "exclusive",
    "diversityTagText",
    "clientCareersUrl",
    "clientGroupId",
    "clientTitleString",
    "diversityCountLabel",
    "smbJobFields",
    "internshipTags",
    "logoPathV3",
    "logoPath",
    "clientLogo",
]


def infer_country_from_location(text: Any) -> Optional[str]:
    if pd.isna(text):
        return None

    text = str(text).lower()

    if "germany" in text:
        return "Germany"
    if "saudi" in text or "arabia" in text:
        return "Saudi Arabia"
    if "canada" in text:
        return "Canada"
    if "sweden" in text:
        return "Sweden"
    if "bahrain" in text:
        return "Bahrain"
    if "malaysia" in text:
        return "Malaysia"
    if "dubai" in text or "united" in text:
        return "United Arab Emirates"
    if "india" in text:
        return "India"

    return "India"


def build_naukri_employment_fields(df: pd.DataFrame) -> Tuple[pd.Series, pd.Series]:
    def build_raw(job_type: Any, description: Any) -> Optional[str]:
        job_type = None if pd.isna(job_type) else str(job_type).strip()
        description = "" if pd.isna(description) else str(description).strip()

        signals = []
        if job_type:
            signals.append(f"jobType={job_type}")

        desc_lower = description.lower()

        if "full time" in desc_lower or "full-time" in desc_lower:
            signals.append("desc=full_time")
        if "part time" in desc_lower or "part-time" in desc_lower:
            signals.append("desc=part_time")
        if "contract" in desc_lower:
            signals.append("desc=contract")
        if "temporary" in desc_lower:
            signals.append("desc=temporary")
        if "internship" in desc_lower or "intern " in desc_lower:
            signals.append("desc=internship")

        return "; ".join(signals) if signals else None

    def normalize(job_type: Any, description: Any) -> str:
        job_type = None if pd.isna(job_type) else str(job_type).strip().lower()
        description = "" if pd.isna(description) else str(description).strip().lower()

        if job_type == "internship":
            return "internship"
        if "full time" in description or "full-time" in description:
            return "full_time"
        if "part time" in description or "part-time" in description:
            return "part_time"
        if "contract" in description:
            return "contract"
        if "temporary" in description:
            return "temporary"
        if "internship" in description or " intern " in f" {description} ":
            return "internship"

        return "unknown"

    employment_type_raw = df.apply(
        lambda row: build_raw(row["jobType"], row["jobDescription"]),
        axis=1,
    )
    employment_type_normalized = df.apply(
        lambda row: normalize(row["jobType"], row["jobDescription"]),
        axis=1,
    )
    return employment_type_raw, employment_type_normalized


def normalize_seniority_from_title(title: Any) -> Optional[str]:
    if pd.isna(title):
        return None

    text = str(title).strip().lower()

    pattern_rules = [
        (r"\bsenior\s+principal\b|\bprincipal\s+engineer\b|\bprincipal\b", "principal"),
        (r"\bstaff\b", "staff"),
        (r"\blead\b|\bteam\s+lead\b|\btech\s+lead\b", "lead"),
        (r"\bmanager\b|\bdirector\b|\bhead\b", "manager"),
        (r"\bsenior\b|\bsr\.?\b", "senior"),
        (r"\bmid\b|\bmid-level\b|\bintermediate\b", "mid"),
        (r"\bjunior\b|\bjr\.?\b|\bentry[- ]level\b", "junior"),
        (r"\bintern\b|\binternship\b|\btrainee\b", "intern"),
    ]

    for pattern, label in pattern_rules:
        if re.search(pattern, text):
            return label
    return None


def row_to_metadata(row: pd.Series) -> Optional[Dict[str, Any]]:
    out: Dict[str, Any] = {}
    for col in NAUKRI_METADATA_COLS:
        val = row[col]
        if pd.notna(val):
            out[col] = val
    return out if out else None


def transform_naukri(dataset_naukri_jobs: pd.DataFrame) -> pd.DataFrame:
    naukri_unified = pd.DataFrame(index=dataset_naukri_jobs.index)
    naukri_unified["source"] = "naukri"

    for col in CANONICAL_COLUMNS:
        if col in MAPPING_DICT_NAUKRI:
            naukri_unified[col] = dataset_naukri_jobs[MAPPING_DICT_NAUKRI[col]]
        elif col != "source":
            naukri_unified[col] = None

    salary_parsed = dataset_naukri_jobs["salaryDetail"].apply(
        lambda x: ast.literal_eval(x) if pd.notna(x) else {}
    )
    naukri_unified["salary_raw"] = dataset_naukri_jobs["salaryDetail"]
    naukri_unified["salary_min"] = salary_parsed.apply(lambda d: d.get("minimumSalary"))
    naukri_unified["salary_max"] = salary_parsed.apply(lambda d: d.get("maximumSalary"))
    naukri_unified["salary_currency"] = salary_parsed.apply(lambda d: d.get("currency"))

    naukri_unified["city_or_region"] = (
        naukri_unified["location_raw"]
        .astype("string")
        .str.replace(r"^(Hybrid|Remote|Onsite)\s*-\s*", "", regex=True)
        .str.strip()
    )

    naukri_unified["seniority_raw"] = dataset_naukri_jobs["title"]
    naukri_unified["country"] = naukri_unified["city_or_region"].apply(
        infer_country_from_location
    )

    loc_lower = naukri_unified["location_raw"].astype("string").str.lower()
    naukri_unified["location_type_normalized"] = None
    naukri_unified.loc[
        loc_lower.str.contains(r"\bhybrid\b", na=False), "location_type_normalized"
    ] = "hybrid"
    naukri_unified.loc[
        loc_lower.str.contains(r"\bremote\b", na=False), "location_type_normalized"
    ] = "remote"

    (
        naukri_unified["employment_type_raw"],
        naukri_unified["employment_type_normalized"],
    ) = build_naukri_employment_fields(dataset_naukri_jobs)

    naukri_unified["seniority_normalized"] = naukri_unified["seniority_raw"].apply(
        normalize_seniority_from_title
    )
    naukri_unified["source_metadata"] = dataset_naukri_jobs.apply(
        row_to_metadata, axis=1
    )

    return naukri_unified[CANONICAL_COLUMNS]


def load_and_transform(csv_path: str = "csv/dataset_naukri_jobs.csv") -> pd.DataFrame:
    dataset_naukri_jobs = pd.read_csv(csv_path)
    return transform_naukri(dataset_naukri_jobs)


if __name__ == "__main__":
    df = load_and_transform()
    print(df.head())
