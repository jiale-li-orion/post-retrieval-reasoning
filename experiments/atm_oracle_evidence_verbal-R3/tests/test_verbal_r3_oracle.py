import sys
import tempfile
import unittest
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
ATM_ROOT = ROOT / "ATM-Bench"
SCRIPTS_ROOT = ROOT / "experiments/atm_oracle_evidence_verbal-R3/scripts"
sys.path.insert(0, str(ATM_ROOT))
sys.path.insert(0, str(SCRIPTS_ROOT))

import verbal_r3_core as module


class FakeTokenizer:
    def encode(self, text, add_special_tokens=False):
        del add_special_tokens
        return text.split()


class VerbalR3ContractTests(unittest.TestCase):
    def test_config_is_single_source_of_model_and_generation_settings(self):
        config = module.load_experiment_config(
            ROOT / "experiments/atm_oracle_evidence_verbal-R3/configs/verbal_r3_official.json"
        )
        self.assertEqual(config.reranker.model, "0k9d0h1/reranker3b-sft")
        self.assertEqual(
            config.reranker.revision,
            "cdf46c85892ebb715cbd6a0b582af35ad5caa96b",
        )
        self.assertEqual(config.reranker.temperature, 0.6)
        self.assertEqual(config.reranker.top_p, 0.95)
        self.assertEqual(config.reranker.max_new_tokens, 1024)
        self.assertEqual(config.reranker.seed, 0)
        self.assertNotIn("thinking", config.answerer.request_body)

    def test_official_prompt_is_loaded_from_verbal_r3_source(self):
        prompt = module.load_python_string_assignment(
            ROOT / "VerbalR3/utils/reranker_server.py", "system_prompt"
        )
        self.assertIn("reason internally", prompt)
        self.assertIn("Score: <1-5>", prompt)
        self.assertTrue(prompt.endswith("\n"))

    def test_parse_requires_both_comment_and_score(self):
        parsed = module.parse_reranker_output(
            "Comment: This document supplies the requested date.\nScore: 5"
        )
        self.assertEqual(parsed.comment, "This document supplies the requested date.")
        self.assertEqual(parsed.score, 5)

        for malformed in ("Comment: useful", "Score: 4", "Comment: useful\nScore: 0"):
            with self.subTest(malformed=malformed):
                with self.assertRaises(module.RerankerParseError):
                    module.parse_reranker_output(malformed)

    def test_annotation_preserves_sgm_and_adds_comment_and_score(self):
        chunk = "ID: item-1\nCaption: Porto bridge\n"
        annotated = module.append_verbal_annotation(chunk, "Directly relevant.", 5)
        self.assertTrue(annotated.startswith(chunk.rstrip()))
        self.assertIn("Verbal Annotation: Directly relevant.", annotated)
        self.assertIn("Relevance score: 5", annotated)

    def test_token_count_uses_checkpoint_tokenizer(self):
        self.assertEqual(module.count_tokens(FakeTokenizer(), "one two three"), 3)

    def test_retry_usage_counts_every_generation_attempt(self):
        prompt_tokens, completion_tokens = module.accumulate_generation_usage(
            prompt_tokens_per_attempt=20,
            completion_tokens_by_attempt=[7, 6],
        )
        self.assertEqual(prompt_tokens, 40)
        self.assertEqual(completion_tokens, 13)

    def test_existing_output_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            existing = Path(tmp) / "predictions.jsonl"
            missing = Path(tmp) / "annotations.jsonl"
            existing.write_text("occupied\n")
            with self.assertRaises(FileExistsError):
                module.ensure_outputs_absent([existing, missing])

    def test_evaluation_summary_collects_atm_and_fallback_count(self):
        with tempfile.TemporaryDirectory() as tmp:
            eval_dir = Path(tmp)
            (eval_dir / "atm_gpt-5-mini_summary.json").write_text(
                json.dumps({"accuracy": 0.5, "by_qtype": {"number": {"accuracy": 1.0}}})
            )
            (eval_dir / "atm_gpt-5-mini.json").write_text(
                json.dumps([
                    {"id": "q1", "fallback_model_used": True},
                    {"id": "q2"},
                ])
            )
            summary = module.load_evaluation_summary(eval_dir)
            self.assertEqual(summary["atm_qs"], 0.5)
            self.assertEqual(summary["by_qtype"]["number"]["accuracy"], 1.0)
            self.assertEqual(summary["judge_fallback_count"], 1)

    def test_answer_record_keeps_protocol_fields(self):
        record = module.build_answer_record(
            qa={"id": "q1", "qtype": "number"},
            evidence_ids=["e1"],
            answer="3",
            usage=None,
            latency_ms=12,
            requested_model="mimo-v2.5",
            returned_model=None,
        )
        self.assertEqual(record["qa_id"], "q1")
        self.assertEqual(record["qtype"], "number")
        self.assertEqual(record["evidence_ids"], ["e1"])
        self.assertIsNone(record["prompt_tokens"])
        self.assertNotIn("thinking", record)

    def test_annotation_record_keeps_tokens_and_provenance(self):
        record = module.build_annotation_record(
            qa_id="q1",
            evidence_id="e1",
            evidence_index=0,
            question="When?",
            sgm_text="Timestamp: 2025-01-01",
            raw_output="Comment: contains date\nScore: 5",
            comment="contains date",
            score=5,
            retry_count=1,
            prompt_tokens=20,
            completion_tokens=6,
            latency_ms=10,
            model="reranker",
            checkpoint_revision="abc",
        )
        self.assertEqual(record["total_tokens"], 26)
        self.assertTrue(record["parse_ok"])
        self.assertEqual(record["evidence_id"], "e1")


if __name__ == "__main__":
    unittest.main()
