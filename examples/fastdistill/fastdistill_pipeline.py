from distilabel.models.llms import OpenAILLM
from distilabel.pipeline import Pipeline
from distilabel.steps import LoadDataFromDicts
from distilabel.steps.tasks import TextGeneration
from distilabel.steps.fastdistill import (
    CanonicalizeFields,
    ComputeHash,
    WriteManifest,
    WriteQualityReport,
)


def build_pipeline():
    teacher_llm = OpenAILLM(
        model="teacher-model-name",
        base_url="http://gateway.local/v1",
    )

    with Pipeline(name="fastdistill-v0") as pipeline:
        data = LoadDataFromDicts(
            data=[
                {
                    "task_id": "text2sql-001",
                    "schema": {"tables": ["users"], "columns": ["id", "name"]},
                    "question": "List user names",
                    "decode_profile": {"temperature": 0.2, "max_tokens": 128, "n": 1},
                    "system_prompt": "Return SQL only.",
                }
            ]
        )

        canonical = CanonicalizeFields(fields=["schema", "question"])
        schema_hash = ComputeHash(fields=["schema"], output_field="schema_hash")
        sample_id = ComputeHash(
            fields=["task_id", "schema_hash", "canonical_input", "decode_profile"],
            output_field="sample_id",
        )

        teacher = TextGeneration(
            llm=teacher_llm,
            system_prompt="Return SQL only.",
            template="{{ question }}",
            columns=["question"],
        )

        manifest = WriteManifest(stage="teacher_candidates")
        report = WriteQualityReport(stage="teacher_candidates")

        data >> canonical >> schema_hash >> sample_id >> teacher >> manifest >> report

    return pipeline


if __name__ == "__main__":
    pipeline = build_pipeline()
    pipeline.run(use_cache=False)
