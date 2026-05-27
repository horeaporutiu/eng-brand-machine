"""Tests for the conference catalog, scheduler, and AI Conference Pulse insights.

Run with:
    python3 -m unittest tests/test_conferences.py -v
"""

import json
import os
import sys
import tempfile
import unittest
from datetime import date

# Ensure repo root is on sys.path so `import eng_brand_machine` works when
# the suite is launched from /tests or from the repo root.
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import eng_brand_machine as ebm  # noqa: E402


SAMPLE_BLUEPRINT = {
    "name": "Test Summit",
    "month": 6,
    "day": 15,
    "duration_days": 2,
    "venue": "Test Venue",
    "focus": "Testing focus",
    "format": "Test format",
    "audience": "Test audience",
    "miro_angle": "Test angle",
    "watch_for": "Test signal",
    "tags": ["Test"],
}


class FormatDateRangeTests(unittest.TestCase):
    def test_single_day(self):
        d = date(2026, 6, 15)
        self.assertEqual(ebm.format_date_range(d, d), "Jun 15, 2026")

    def test_same_month_range(self):
        result = ebm.format_date_range(date(2026, 6, 15), date(2026, 6, 17))
        self.assertEqual(result, "Jun 15–17, 2026")

    def test_cross_month_same_year(self):
        result = ebm.format_date_range(date(2026, 6, 30), date(2026, 7, 2))
        self.assertEqual(result, "Jun 30–Jul 02, 2026")

    def test_cross_year(self):
        result = ebm.format_date_range(date(2026, 12, 30), date(2027, 1, 2))
        self.assertEqual(result, "Dec 30, 2026–Jan 02, 2027")


class BuildScheduleTests(unittest.TestCase):
    def setUp(self):
        # Snapshot module-level state so we can restore it.
        self._original_blueprints = ebm.AI_CONFERENCE_BLUEPRINTS
        ebm.AI_CONFERENCE_BLUEPRINTS = [SAMPLE_BLUEPRINT]

    def tearDown(self):
        ebm.AI_CONFERENCE_BLUEPRINTS = self._original_blueprints

    def test_returns_current_year_when_event_still_upcoming(self):
        schedule = ebm.build_ai_conference_schedule(
            location="Testville",
            today=date(2026, 1, 1),
        )
        self.assertEqual(len(schedule), 1)
        self.assertEqual(schedule[0]["start_date"].year, 2026)
        self.assertEqual(schedule[0]["location"], "Testville")
        self.assertEqual(schedule[0]["date_label"], "Jun 15–16, 2026")

    def test_rolls_over_to_next_year_when_all_events_passed(self):
        schedule = ebm.build_ai_conference_schedule(
            location="Testville",
            today=date(2026, 12, 31),
        )
        self.assertEqual(len(schedule), 1)
        self.assertEqual(schedule[0]["start_date"].year, 2027)

    def test_filters_out_already_completed_events(self):
        # Two blueprints — one in the past, one in the future
        ebm.AI_CONFERENCE_BLUEPRINTS = [
            {**SAMPLE_BLUEPRINT, "name": "Past", "month": 1, "day": 5},
            {**SAMPLE_BLUEPRINT, "name": "Future", "month": 11, "day": 5},
        ]
        schedule = ebm.build_ai_conference_schedule(
            location="Testville",
            today=date(2026, 6, 1),
        )
        names = [item["name"] for item in schedule]
        self.assertEqual(names, ["Future"])


class LoadConferencesCatalogTests(unittest.TestCase):
    def test_loads_real_catalog(self):
        catalog = ebm.load_conferences_catalog()
        self.assertIn("default_location", catalog)
        self.assertIn("fictional_local_slate", catalog)
        self.assertIn("major_ai_conferences", catalog)
        self.assertGreater(len(catalog["fictional_local_slate"]), 0)
        self.assertGreater(len(catalog["major_ai_conferences"]), 0)

    def test_missing_file_returns_fallback(self):
        with tempfile.TemporaryDirectory() as tmp:
            catalog = ebm.load_conferences_catalog(
                os.path.join(tmp, "missing.json")
            )
        self.assertIn("default_location", catalog)
        self.assertIsInstance(catalog["fictional_local_slate"], list)
        self.assertIsInstance(catalog["major_ai_conferences"], list)

    def test_malformed_json_returns_fallback(self):
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as fh:
            fh.write("{ not valid json")
            broken_path = fh.name
        try:
            catalog = ebm.load_conferences_catalog(broken_path)
        finally:
            os.unlink(broken_path)
        self.assertIn("default_location", catalog)

    def test_custom_catalog_round_trips(self):
        custom = {
            "default_location": "Berlin, Germany",
            "fictional_local_slate": [SAMPLE_BLUEPRINT],
            "major_ai_conferences": [
                {
                    "name": "CustomConf",
                    "keywords": ["customconf"],
                    "cadence": "Annual",
                    "audience": "Custom",
                    "miro_angle": "Custom angle",
                }
            ],
        }
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as fh:
            json.dump(custom, fh)
            path = fh.name
        try:
            catalog = ebm.load_conferences_catalog(path)
        finally:
            os.unlink(path)
        self.assertEqual(catalog["default_location"], "Berlin, Germany")
        self.assertEqual(catalog["major_ai_conferences"][0]["name"], "CustomConf")


class ExtractConferenceInsightsTests(unittest.TestCase):
    SAMPLE_CONFS = [
        {
            "name": "NeurIPS",
            "long_name": "Neural Information Processing Systems",
            "keywords": ["neurips", "nips"],
            "cadence": "Annual · December",
            "audience": "ML researchers",
            "miro_angle": "Map papers.",
            "signal_topics": ["alignment", "agents"],
        },
        {
            "name": "AWS re:Invent",
            "keywords": ["re:invent", "reinvent"],
            "cadence": "Annual · December",
            "audience": "Cloud teams",
            "miro_angle": "Diff board.",
        },
        {
            "name": "Empty",
            "keywords": [],
            "cadence": "",
            "audience": "",
            "miro_angle": "",
        },
    ]

    def _article(self, title, score=10, source="HN", description=""):
        return {
            "title": title,
            "description": description,
            "source": source,
            "source_icon": "🟠",
            "url": "http://example.com",
            "score": score,
        }

    def test_no_articles_returns_empty(self):
        self.assertEqual(ebm.extract_conference_insights([], self.SAMPLE_CONFS), [])

    def test_no_confs_returns_empty(self):
        self.assertEqual(
            ebm.extract_conference_insights([self._article("hello")], []),
            [],
        )

    def test_detects_mentions_in_title_and_description(self):
        articles = [
            self._article("Top NeurIPS papers of the year", score=200),
            self._article("AWS re:Invent keynote recap", score=80),
            self._article("Generic post", description="discussion of NIPS dataset"),
            self._article("Unrelated post"),
        ]
        insights = ebm.extract_conference_insights(articles, self.SAMPLE_CONFS)
        names = [i["name"] for i in insights]
        # Both NeurIPS (2 mentions) and re:Invent (1 mention) should appear,
        # sorted by mention_count desc.
        self.assertEqual(names[0], "NeurIPS")
        self.assertEqual(names[1], "AWS re:Invent")
        neurips = insights[0]
        self.assertEqual(neurips["mention_count"], 2)
        # Top articles should be score-ordered.
        self.assertEqual(neurips["top_articles"][0]["score"], 200)

    def test_max_articles_per_conf_is_respected(self):
        articles = [self._article(f"NeurIPS thing {i}") for i in range(10)]
        insights = ebm.extract_conference_insights(
            articles, self.SAMPLE_CONFS, max_articles_per_conf=3
        )
        self.assertEqual(insights[0]["mention_count"], 10)
        self.assertEqual(len(insights[0]["top_articles"]), 3)

    def test_skips_conferences_without_keywords(self):
        articles = [self._article("NeurIPS update")]
        insights = ebm.extract_conference_insights(articles, self.SAMPLE_CONFS)
        names = [i["name"] for i in insights]
        self.assertNotIn("Empty", names)

    def test_case_insensitive_matching(self):
        articles = [self._article("DEEP DIVE INTO neurips")]
        insights = ebm.extract_conference_insights(articles, self.SAMPLE_CONFS)
        self.assertEqual(insights[0]["name"], "NeurIPS")


if __name__ == "__main__":
    unittest.main()
