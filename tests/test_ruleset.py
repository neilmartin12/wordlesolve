"""Tests for ruleset module"""
# pylint: disable=no-self-use, too-few-public-methods, redefined-outer-name, protected-access

import pytest

from wordlesolve.ruleset import Rule, RuleSet


@pytest.fixture
def happy_rule_set():
    "RuleSet with HAPPY/01210 outcome added"
    rule_set = RuleSet()
    rule_set.add_outcome("HAPPY", "01210")
    return rule_set


@pytest.fixture
def ten_words():
    "List of ten words"
    return [
        "ABOUT",
        "THEIR",
        "THERE",
        "WHICH",
        "WOULD",
        "OTHER",
        "AFTER",
        "FIRST",
        "THINK",
        "COULD",
    ]


class TestRule:
    "Tests of Rule class"

    def test_defaults(self):
        "Default values correctly set"
        rule = Rule()
        assert rule.count == 0
        assert rule.count_op == "gte"
        assert not rule.confirmed
        assert not rule.excluded


class TestRuleSet:
    "Tests of RuleSet class"

    def test_add_outcome(self):
        "add_outcome() method"

        # Create empty RuleSet
        rule_set = RuleSet()
        assert len(rule_set) == 0

        # Add an outcome
        rule_set.add_outcome("HAPPY", "01210")

        # Should be rules for 4 letters
        assert len(rule_set) == 4

        # No H in the solution
        assert "H" in rule_set
        rule = rule_set["H"]
        assert rule.count == 0
        assert rule.count_op == "eq"
        assert not rule.confirmed
        assert not rule.excluded

        # At least one A not in position 1
        assert "A" in rule_set
        rule = rule_set["A"]
        assert rule.count == 1
        assert rule.count_op == "gte"
        assert not rule.confirmed
        assert rule.excluded == {1}

        # At least two P's, one in position 2 but not in position 3
        assert "P" in rule_set
        rule = rule_set["P"]
        assert rule.count == 2
        assert rule.count_op == "gte"
        assert rule.confirmed == {2}
        assert rule.excluded == {3}

        # Y should be the same as H
        assert "Y" in rule_set
        rule = rule_set["Y"]
        assert rule.count == 0
        assert rule.count_op == "eq"
        assert not rule.confirmed
        assert not rule.excluded

    def test_add_second_outcome(self, happy_rule_set):
        "Outcomes should accumulate"

        rule_set = happy_rule_set

        # Add a second outcome
        rule_set.add_outcome("ALTAR", "20001")

        # Seven letters in total
        assert len(rule_set) == 7

        # There is only one A, in position 0
        rule = rule_set["A"]
        assert rule.count == 1
        assert rule.count_op == "eq"
        assert rule.confirmed == {0}
        assert rule.excluded == {1}

    def test_is_match(self, happy_rule_set):
        "is_match() method"

        rule_set = happy_rule_set

        # APPLE is a match
        assert rule_set.is_match("APPLE")

        # No A is not a match
        assert not rule_set.is_match("IPPLE")

        # Can't include H or Y
        assert not rule_set.is_match("APPHE")
        assert not rule_set.is_match("APPYE")

        # Must have 2 P's
        assert not rule_set.is_match("ARPHE")

        # Must have P in position 2
        assert not rule_set.is_match("APLEP")

        # Can't have P in position 3
        assert not rule_set.is_match("ALPPE")

        # Add a second outcome
        rule_set.add_outcome("ALTAR", "20001")

        # Exactly one A
        assert not rule_set.is_match("APPRA")

    def test_filter_matches(self, happy_rule_set):
        "filter_matches() method"

        rule_set = happy_rule_set

        # List of words to filter
        words = ["HIPPY", "POPPY", "APPLE", "PLANT"]

        matches = rule_set.filter_matches(words)
        assert matches == ["APPLE"]

    def test_get_letter_status(self, happy_rule_set):
        "_get_letter_status() method"

        rule_set = happy_rule_set

        assert rule_set._get_letter_status("H") == 0  # Not in solution
        assert rule_set._get_letter_status("A") == 1  # Position unknown
        assert rule_set._get_letter_status("P") == 2  # Position known
        assert rule_set._get_letter_status("Z") == -1  # No information

    def test_get_alphabet_status(self, happy_rule_set):
        "get_alphabet_status() method"

        rule_set = happy_rule_set
        status = rule_set.get_alphabet_status()

        assert status["H"] == 0  # Not in solution
        assert status["A"] == 1  # Position unknown
        assert status["P"] == 2  # Position known
        assert status["Z"] == -1  # No information


class TestWordScoring:
    "Tests of word scoring methods"

    def test_get_frequency_mask(self, happy_rule_set):
        "_get_frequency_mask() method"

        rule_set = happy_rule_set

        # Get mask
        mask = rule_set._get_frequency_mask()

        # No H in the word
        assert mask["H"] == [0, 0, 0, 0, 0]

        # At least one A
        assert mask["A"] == [0, 1, 1, 1, 1]

        # At least two P's
        assert mask["P"] == [0, 0, 1, 1, 1]

        # No rule for Z
        assert mask["Z"] == [1, 1, 1, 1, 1]

    def test_get_frequency_scores_no_mask(self):
        "_get_frequency_scores() method with no mask applied"

        # Blank rule set = no mask
        rule_set = RuleSet()
        words = ["HAPPY", "ABBEY", "PEDAL"]

        scores = rule_set._get_frequency_scores(words)
        assert scores["A"] == [3, 0, 0, 0, 0]
        assert scores["B"] == [1, 1, 0, 0, 0]
        assert scores["C"] == [0, 0, 0, 0, 0]
        assert scores["H"] == [1, 0, 0, 0, 0]
        assert scores["P"] == [2, 1, 0, 0, 0]
        assert scores["Y"] == [2, 0, 0, 0, 0]

    def test_get_frequency_scores_with_mask(self, happy_rule_set):
        "_get_frequency_scores() method with mask applied"

        # Rule set will apply a mask
        rule_set = happy_rule_set
        words = ["HAPPY", "ABBEY", "PEDAL"]

        scores = rule_set._get_frequency_scores(words)
        assert scores["A"] == [0, 0, 0, 0, 0]  # Mask is [0, 1, 1, 1, 1]
        assert scores["B"] == [1, 1, 0, 0, 0]
        assert scores["C"] == [0, 0, 0, 0, 0]
        assert scores["H"] == [0, 0, 0, 0, 0]  # Mask is [0, 0, 0, 0, 0]
        assert scores["P"] == [0, 0, 0, 0, 0]  # Mask is [0, 0, 1, 1, 1]
        assert scores["Y"] == [0, 0, 0, 0, 0]  # Mask is [0, 0, 0, 0, 0]

    def test_get_position_mask(self, happy_rule_set):
        "_get_position_mask() method"

        rule_set = happy_rule_set

        # Get mask
        mask = rule_set._get_position_mask()

        # No H in the word
        assert mask["H"] == [0, 0, 0, 0, 0]

        # A not in position 1
        assert mask["A"] == [1, 0, 1, 1, 1]

        # P in position 2 and not position 3
        assert mask["P"] == [1, 1, 0, 0, 1]

        # No rule for Z
        assert mask["Z"] == [1, 1, 1, 1, 1]

    def test_get_position_scores_no_mask(self):
        "_get_position_scores() method with no mask applied"

        # Blank rule set = no mask
        rule_set = RuleSet()
        words = ["HAPPY", "ABBEY", "PEDAL"]

        scores = rule_set._get_position_scores(words)
        assert scores["A"] == [1, 1, 0, 1, 0]
        assert scores["B"] == [0, 1, 1, 0, 0]
        assert scores["C"] == [0, 0, 0, 0, 0]
        assert scores["H"] == [1, 0, 0, 0, 0]
        assert scores["P"] == [1, 0, 1, 1, 0]
        assert scores["Y"] == [0, 0, 0, 0, 2]

    def test_get_position_scores_with_mask(self, happy_rule_set):
        "_get_position_scores() method with mask applied"

        # Rule set will apply a mask
        rule_set = happy_rule_set
        words = ["HAPPY", "ABBEY", "PEDAL"]

        scores = rule_set._get_position_scores(words)
        assert scores["A"] == [1, 0, 0, 1, 0]  # mask is [1, 0, 1, 1, 1]
        assert scores["B"] == [0, 1, 1, 0, 0]  # mask is [1, 1, 1, 1, 1]
        assert scores["C"] == [0, 0, 0, 0, 0]  # mask is [1, 1, 1, 1, 1]
        assert scores["H"] == [0, 0, 0, 0, 0]  # mask is [0, 0, 0, 0, 0]
        assert scores["P"] == [1, 0, 0, 0, 0]  # mask is [1, 1, 0, 0, 1]
        assert scores["Y"] == [0, 0, 0, 0, 0]  # mask is [0, 0, 0, 0, 0]

    def test_score_words(self, ten_words):
        "score_words() method"

        # Score without mask
        rule_set = RuleSet()
        scores = rule_set.score_words(ten_words, ten_words)

        # Highest scoring is THEIR
        assert scores[0].word == "THEIR"
        assert scores[0].score >= scores[1].score
        assert scores[0].frequency > 0

    def test_score_words_with_mask(self, ten_words):
        "score_words() method with mask"

        # Score with mask
        rule_set = RuleSet()
        rule_set.add_outcome("COULD", "01100")  # Solution is 'ABOUT'
        matches = rule_set.filter_matches(ten_words)
        scores = rule_set.score_words(ten_words, matches)

        # Should indicate ABOUT
        assert scores[0].word == "ABOUT"
