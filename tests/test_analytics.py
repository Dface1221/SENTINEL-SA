import unittest
import sys
import os

# Add prototype root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.database import SessionLocal, init_db
from backend.database.models import CSE, Alert, Finding, GroundTruth
from backend.data.generator import generate_synthetic_dataset
from backend.analytics.pipeline import run_full_supervisory_analysis
from backend.analytics.validation import compute_validation_metrics
from backend.reports.generator import generate_executive_report_html, generate_cse_report_html

class TestSATSAAnalytics(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()
        cls.db = SessionLocal()

    @classmethod
    def tearDownClass(cls):
        cls.db.close()

    def test_01_synthetic_generator(self):
        result = generate_synthetic_dataset(self.db)
        self.assertEqual(result["status"], "success")
        self.assertGreaterEqual(result["cses_count"], 10)
        self.assertGreaterEqual(result["alerts_count"], 10000)
        print(f"\n[PASS] Generator produced {result['alerts_count']} alerts across {result['cses_count']} CSEs.")

    def test_02_supervisory_pipeline(self):
        pipeline_res = run_full_supervisory_analysis(self.db)
        self.assertEqual(pipeline_res["status"], "success")
        self.assertGreater(pipeline_res["total_findings"], 5)
        self.assertGreater(pipeline_res["execution_gaps_count"], 0)
        self.assertGreater(pipeline_res["negative_space_count"], 0)
        print(f"[PASS] Pipeline identified {pipeline_res['total_findings']} findings ({pipeline_res['execution_gaps_count']} gaps, {pipeline_res['negative_space_count']} negative space).")

    def test_03_star_demo_cse07(self):
        cse07 = self.db.query(CSE).filter(CSE.cse_id == "CSE-07").first()
        self.assertIsNotNone(cse07)
        self.assertGreaterEqual(cse07.attention_score, 65.0)
        
        # Check specific findings for CSE-07
        cse07_findings = self.db.query(Finding).filter(Finding.cse_id == "CSE-07").all()
        titles = [f.title for f in cse07_findings]
        print(f"[PASS] CSE-07 Attention Score: {cse07.attention_score} ({cse07.review_status})")
        print(f"       CSE-07 Findings Count: {len(cse07_findings)}")
        self.assertTrue(any("Critical alerts closed" in t or "quickly" in t for t in titles))
        self.assertTrue(any("escalation" in t.lower() for t in titles))
        self.assertTrue(any("telemetry" in t.lower() for t in titles))

    def test_04_validation_metrics(self):
        val_res = compute_validation_metrics(self.db)
        overall = val_res["overall"]
        self.assertGreater(overall["precision"], 0.70)
        self.assertGreater(overall["recall"], 0.70)
        self.assertGreater(overall["f1_score"], 0.70)
        print(f"[PASS] Validation Metrics -> Precision: {overall['precision']}, Recall: {overall['recall']}, F1 Score: {overall['f1_score']}")

    def test_05_reports(self):
        exec_html = generate_executive_report_html(self.db)
        self.assertIn("NCIIPC", exec_html)
        self.assertIn("Supervisory Assessment Report", exec_html)

        cse_html = generate_cse_report_html(self.db, "CSE-07")
        self.assertIn("Northern Regional Load Despatch", cse_html)
        self.assertIn("Corrective Action Plan", cse_html)
        print("[PASS] Executive and CSE-07 Dossier HTML reports generated successfully.")

if __name__ == "__main__":
    unittest.main()
