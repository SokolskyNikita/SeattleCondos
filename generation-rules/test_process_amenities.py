import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import process_amenities as processor


class AmenityProcessingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rules = json.loads((processor.ROOT / "amenity-consolidation-rules.json").read_text())

    def fixture(self, names):
        return {"metadata": {"criteria": {"minimum_shared_amenities": 1}, "methodology": {},
                             "counts": {"buildings": 1}},
                "buildings": [{"id": "example", "name": "Example", "amenities": names,
                               "approx_1br_monthly_usd": 2200, "sources": [{"url": "https://example.com"}]}]}

    def labels(self, source):
        return set(self.rules["mappings"][processor.normalize_name(source)])

    def test_extract_before_excluding_wifi_and_tv(self):
        self.assertEqual(self.labels("two skyline lounges with Wi-Fi, a full kitchen, TVs, a fireplace and shuffleboard"),
                         {"Resident lounge", "Shared kitchen", "Fireplace", "Shuffleboard"})
        self.assertEqual(self.labels("community Wi-Fi"), set())

    def test_no_substring_spa_or_coffee_bar_inferences(self):
        self.assertEqual(self.labels("resident lounge with pool table, television, and private workspaces"),
                         {"Resident lounge", "Pool table", "Private workspace"})
        self.assertEqual(self.labels("resident lounge with kitchenette, coffee machine, mini-fridge, dining table and tv seating"),
                         {"Resident lounge", "Kitchenette"})

    def test_distinct_watercraft_and_shared_studio(self):
        self.assertEqual(self.labels("reservation-only kayaks and paddle boards"), {"Kayak access", "Paddleboard access"})
        self.assertEqual(self.labels("yoga and spin studio with five stationary bikes"), {"Yoga/spin studio"})
        self.assertEqual(self.labels("fitness center with free weights"), {"Gym"})

    def test_meaningful_subtype_distinctions(self):
        for source, expected in {
            "EV-ready parking": {"Parking"},
            "EV parking": {"Parking"},
            "bike racks": {"Bike parking"},
            "bike storage": {"Bike storage"},
            "rooftop pet relief area and self-service pet wash": {"Pet relief area", "Pet wash station"},
            "sky lounge": {"Resident lounge"},
            "spa": {"Spa"},
            "pet spa": {"Pet spa"},
            "private rooftop garden": {"Rooftop garden"},
        }.items():
            with self.subTest(source=source):
                self.assertEqual(self.labels(source), expected)

    def test_all_canonical_labels_can_be_reused_as_inputs(self):
        for label in self.rules["canonical_amenities"]:
            self.assertEqual(self.labels(label), {label})

    def test_picnic_context_needs_independent_grill_evidence(self):
        alone, _ = processor.process(self.fixture(["picnic area"]), self.rules)
        self.assertEqual(alone["buildings"][0]["amenities"], [])
        together, _ = processor.process(self.fixture(["picnic area", "BBQ/Picnic Area"]), self.rules)
        details = together["buildings"][0]["amenity_details"]["BBQs"]
        self.assertEqual(details["source_descriptions"], ["BBQ/Picnic Area"])
        self.assertEqual(details["related_details"][0]["source_description"], "picnic area")

    def test_wellness_routing_requires_explicit_activity(self):
        zen = "landscaped courtyard and indoor/outdoor zen room"
        alone, _ = processor.process(self.fixture([zen, "wellness studio"]), self.rules)
        self.assertEqual(alone["buildings"][0]["amenities"], ["Courtyard"])
        yoga = "indoor/outdoor zen room for yoga postures"
        supported, _ = processor.process(self.fixture([zen, yoga]), self.rules)
        details = supported["buildings"][0]["amenity_details"]["Yoga studio"]
        self.assertEqual(details["source_descriptions"], [yoga])
        self.assertEqual(details["related_details"][0]["source_description"], zen)

    def test_full_audit_preserves_user_selected_names_and_source_context(self):
        for label in ["Private dining room", "Package service", "Movie theater", "Gym",
                      "Resident lounge", "Yoga studio", "Parking", "BBQs"]:
            with self.subTest(label=label):
                self.assertEqual(self.labels(label), {label})
        sources = ["elevated park with walking paths and firepits", "Pilates studio", "lakefront access"]
        result, _ = processor.process(self.fixture(sources), self.rules)
        building = result["buildings"][0]
        self.assertEqual(building["amenities"], ["Fire pit", "Shared park"])
        self.assertEqual(building["amenities_original"], sources)
        self.assertEqual(building["amenity_details"]["Shared park"]["source_descriptions"], sources[:1])
        self.assertEqual({n["source"] for n in building["amenity_review_notes"]}, set(sources[1:]))

    def test_rare_components_fold_without_losing_parent_features(self):
        for source, expected in {
            "Social lounge with DJ booth, karaoke and TV.": {"Resident lounge", "Karaoke"},
            "rooftop greenhouse lounge and resident garden": {"Rooftop lounge", "Rooftop garden"},
            "Fitness center with locker room and sauna": {"Gym", "Sauna"},
            "dry sauna with plunge shower": {"Sauna"},
            "package lockers and oversized package storage room": {"Package lockers", "Package room"},
            "reservable wine cellar lounge with wine storage lockers": {"Resident lounge", "Wine storage"},
            "Skee-Ball game room": {"Arcade games", "Game room"},
            "workshop/hobby locker with bike repair and tools to borrow": {"Makerspace", "Bike repair", "Tool lending"},
            "resident wellness program with personal training and weekly classes": {"Fitness classes"},
        }.items():
            with self.subTest(source=source):
                self.assertEqual(self.labels(source), expected)

    def test_approved_rare_omissions_preserve_source_and_caveats(self):
        sources = ["creative studio", "Soul Fitness partnership", "gym access", "office space",
                   "movement space", "resident cooking events and nutritionist appointments"]
        result, report = processor.process(self.fixture(sources), self.rules)
        building = result["buildings"][0]
        self.assertEqual(building["amenities"], [])
        self.assertEqual(building["amenities_original"], sources)
        self.assertIn("Soul Fitness partnership", {note["source"] for note in building["amenity_review_notes"]})
        self.assertEqual(report["summary"]["buildings_removed"], 0)

    def test_related_lobby_detail_never_creates_concierge_or_changes_hours(self):
        staffing = "24/7 attended lobby with mail room"
        alone, _ = processor.process(self.fixture([staffing]), self.rules)
        self.assertEqual(alone["buildings"][0]["amenities"], [])
        together, _ = processor.process(self.fixture([staffing, "concierge"]), self.rules)
        building = together["buildings"][0]
        self.assertEqual(building["amenities"], ["Concierge"])
        details = building["amenity_details"]["Concierge"]
        self.assertEqual(details["source_descriptions"], ["concierge"])
        self.assertEqual(details["related_details"][0]["source_description"], staffing)
        self.assertIn("does not establish concierge service or 24/7 concierge availability", details["related_details"][0]["note"])
        rerun, _ = processor.process(together, self.rules)
        self.assertEqual(rerun, together)

    def test_invalid_detail_parent_is_rejected(self):
        invalid = copy.deepcopy(self.rules)
        invalid["detail_attachments"]["staffed lobby"]["attach_to_if_present"] = ["Nonexistent parent"]
        with self.assertRaisesRegex(ValueError, "invalid parent"):
            processor.process(self.fixture(["staffed lobby"]), invalid)

    def test_deduplication_preserves_all_sources_and_qualifiers(self):
        sources = ["BBQ area", "rooftop terrace with BBQ", "Seasonal outdoor pool at Arrive Magnolia West",
                   "assigned garage parking available for rent", "reservation-only kayaks and paddle boards"]
        original = self.fixture(sources)
        result, report = processor.process(original, self.rules)
        building = result["buildings"][0]
        self.assertEqual(building["amenities"].count("BBQs"), 1)
        self.assertEqual(building["amenity_details"]["BBQs"]["source_descriptions"], sources[:2])
        self.assertEqual(building["amenities_original"], sources)
        self.assertEqual(building["amenity_details"]["Pool"]["source_descriptions"], [sources[2]])
        self.assertEqual(building["amenity_details"]["Parking"]["source_descriptions"], [sources[3]])
        self.assertEqual(building["amenity_details"]["Kayak access"]["source_descriptions"], [sources[4]])
        self.assertEqual(original, self.fixture(sources))
        for key in ("id", "name", "approx_1br_monthly_usd", "sources"):
            self.assertEqual(building[key], original["buildings"][0][key])
        self.assertEqual(report["summary"]["duplicate_feature_mentions_removed"], 1)

    def test_idempotent_and_reapplies_rules_to_originals(self):
        data = self.fixture(["community Wi-Fi", "bike storage and repair"])
        first, report = processor.process(data, self.rules)
        second, second_report = processor.process(first, self.rules)
        self.assertEqual(second, first)
        self.assertEqual(second_report, report)
        changed = copy.deepcopy(self.rules)
        changed["mappings"]["bike storage and repair"] = ["Bike storage"]
        third, _ = processor.process(first, changed)
        self.assertEqual(third["buildings"][0]["amenities"], ["Bike storage"])
        self.assertEqual(third["buildings"][0]["amenities_original"], data["buildings"][0]["amenities"])

    def test_empty_building_is_retained_and_flagged(self):
        data = self.fixture(["community Wi-Fi", "elevator"])
        result, report = processor.process(data, self.rules)
        self.assertEqual(len(result["buildings"]), 1)
        self.assertEqual(result["buildings"][0]["amenities"], [])
        self.assertEqual(report["inclusion_review"][0]["id"], "example")
        self.assertEqual(result["metadata"]["criteria"], data["metadata"]["criteria"])

    def test_unknown_name_fails_without_writing_anything(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source, report = root / "apartments.json", root / "report.json"
            before = processor.json_bytes(self.fixture(["unreviewed underwater chess arena"]))
            source.write_bytes(before)
            result = subprocess.run([sys.executable, str(processor.ROOT / "process_amenities.py"),
                                     "--input", str(source), "--report", str(report), "--write"], capture_output=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn(b"Unmapped amenity names", result.stderr)
            self.assertEqual(source.read_bytes(), before)
            self.assertFalse(report.exists())

    def test_output_collision_fails_without_overwrite(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "apartments.json"
            before = processor.json_bytes(self.fixture(["fitness center"]))
            source.write_bytes(before)
            result = subprocess.run([sys.executable, str(processor.ROOT / "process_amenities.py"),
                                     "--input", str(source), "--report", str(source), "--write"], capture_output=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(source.read_bytes(), before)

    def test_first_run_does_not_overwrite_unowned_fields(self):
        data = self.fixture(["fitness center"])
        data["buildings"][0]["amenity_review_notes"] = ["User-authored note"]
        with self.assertRaisesRegex(ValueError, "unowned fields"):
            processor.process(data, self.rules)

    def test_failed_second_output_restores_first_output(self):
        with tempfile.TemporaryDirectory() as directory:
            first, second = Path(directory) / "first.json", Path(directory) / "second.json"
            first.write_bytes(b"original first")
            second.write_bytes(b"original second")
            original_replace = Path.replace
            calls = 0

            def fail_second(path, destination):
                nonlocal calls
                calls += 1
                if calls == 2:
                    raise OSError("simulated second replace failure")
                return original_replace(path, destination)

            with patch.object(Path, "replace", fail_second):
                with self.assertRaisesRegex(OSError, "simulated"):
                    processor.write_outputs([(first, b"updated first"), (second, b"updated second")])
            self.assertEqual(first.read_bytes(), b"original first")
            self.assertEqual(second.read_bytes(), b"original second")
            self.assertEqual(set(Path(directory).iterdir()), {first, second})


if __name__ == "__main__":
    unittest.main()
