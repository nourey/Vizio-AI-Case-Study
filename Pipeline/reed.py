"""Clean Reed transform script derived from the final notebook."""

from __future__ import annotations

import re
from typing import Any, Optional

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

MAPPING_DICT_REED = {
    "source_job_id": "id",
    "job_url": "url",
    "apply_url": "url",
    "title": "title",
    "company_url": "companyProfileURL",
    "company_name": "companyName",
    "description_text": "descriptionText",
    "date_posted": "datePosted",
    "application_deadline": "validThrough",
    "location_raw": "jobLocationRegion",
    "city_or_region": "jobLocation",
    "country": "jobLocationCountry",
    "location_type_normalized": "jobLocationType",
    "employment_type_raw": "employmentType",
    "salary_raw": "salaryExact",
    "salary_currency": "currency",
    "salary_min": "salaryMin",
    "salary_max": "salaryMax",
    "salary_period": "salaryTimeUnit",
    "industry_raw": "industry",
    "is_easy_apply": "isEasyApply",
    "is_featured": "isFeatured",
}


def normalize_seniority_from_title(title: Any) -> Optional[str]:
    if pd.isna(title):
        return None

    text = str(title).strip().lower()

    pattern_rules = [
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
    for pattern, label in pattern_rules:
        if re.search(pattern, text):
            return label
    return None


def transform_reed(dataset_reed_jobs: pd.DataFrame) -> pd.DataFrame:
    reed_unified = pd.DataFrame(index=dataset_reed_jobs.index)
    reed_unified["source"] = "reed"

    for col in CANONICAL_COLUMNS:
        if col in MAPPING_DICT_REED:
            reed_unified[col] = dataset_reed_jobs[MAPPING_DICT_REED[col]]
        elif col != "source":
            reed_unified[col] = None

    reed_unified["employment_type_normalized"] = reed_unified["employment_type_raw"]
    reed_unified["seniority_raw"] = reed_unified["title"]
    reed_unified["seniority_normalized"] = reed_unified["seniority_raw"].apply(
        normalize_seniority_from_title
    )
    reed_unified["industry_normalized"] = reed_unified["industry_raw"]

    reed_unified["salary_raw"] = reed_unified["salary_raw"].where(
        reed_unified["salary_raw"].notna(), None
    )

    reed_unified["employment_type_normalized"] = (
        reed_unified["employment_type_raw"]
        .astype("string")
        .str.strip()
        .str.lower()
        .str.replace("-", "_", regex=False)
        .str.replace(" ", "_", regex=False)
    )

    return reed_unified[CANONICAL_COLUMNS]


def load_and_transform(csv_path: str = "csv/dataset_reed_jobs.csv") -> pd.DataFrame:
    dataset_reed_jobs = pd.read_csv(csv_path)
    return transform_reed(dataset_reed_jobs)


if __name__ == "__main__":
    df = load_and_transform()
    print(df.head())
