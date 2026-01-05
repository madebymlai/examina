"""
Tests for active learning classification system.
"""

import numpy as np


class TestPairFeatures:
    """Test feature extraction."""

    def test_extract_features_similar_items(self):
        from core.features import extract_features

        item_a = {
            "name": "velocity_calculation",
            "description": "Calculate velocity using kinematic equations",
            "category": "Kinematics",
        }
        item_b = {
            "name": "speed_calculation",
            "description": "Compute speed using kinematic formulas",
            "category": "Kinematics",
        }

        features = extract_features(item_a, item_b)

        # Embedding similarity should be high (synonyms: velocity≈speed, calculate≈compute)
        assert features.embedding_similarity > 0.7
        # Same category
        assert features.same_category is True
        # Verb match (Calculate vs Compute - different)
        assert features.verb_match is False

    def test_extract_features_different_items(self):
        from core.features import extract_features

        item_a = {
            "name": "velocity_calculation",
            "description": "Calculate velocity using kinematic equations",
            "category": "Kinematics",
        }
        item_b = {
            "name": "thermodynamics_laws",
            "description": "Explain the laws of thermodynamics",
            "category": "Thermodynamics",
        }

        features = extract_features(item_a, item_b)

        # Embedding similarity should be low (completely different topics)
        assert features.embedding_similarity < 0.5
        # Different category
        assert features.same_category is False

    def test_to_vector(self):
        from core.features import PairFeatures

        features = PairFeatures(
            embedding_similarity=0.8,
            token_jaccard=0.5,
            trigram_jaccard=0.6,
            desc_length_ratio=0.9,
            same_category=True,
            verb_match=True,
            name_similarity=0.7,
        )

        vector = features.to_vector()

        assert len(vector) == 7
        assert vector[0] == 0.8  # embedding_similarity
        assert vector[4] == 1.0  # same_category (True -> 1.0)
        assert vector[5] == 1.0  # verb_match (True -> 1.0)


class TestTransitiveInference:
    """Test transitive inference engine."""

    def test_direct_edge(self):
        from core.transitive import TransitiveInference

        ti = TransitiveInference()
        ti.add_edge("a", "b", True, 0.95)

        result = ti.infer("a", "b")

        assert result is not None
        assert result[0] is True  # is_match
        assert result[1] == 0.95  # confidence

    def test_transitive_inference(self):
        from core.transitive import TransitiveInference

        ti = TransitiveInference()
        ti.add_edge("a", "b", True, 0.95)
        ti.add_edge("b", "c", True, 0.90)

        result = ti.infer("a", "c")

        assert result is not None
        assert result[0] is True  # is_match
        assert result[1] >= 0.85  # 0.95 * 0.90 = 0.855

    def test_no_inference_low_confidence(self):
        from core.transitive import TransitiveInference

        ti = TransitiveInference(min_confidence=0.75)
        ti.add_edge("a", "b", True, 0.5)  # Low confidence
        ti.add_edge("b", "c", True, 0.5)  # Low confidence

        result = ti.infer("a", "c")

        # Should not infer because 0.5 * 0.5 = 0.25 < 0.75
        assert result is None

    def test_get_component(self):
        from core.transitive import TransitiveInference

        ti = TransitiveInference()
        ti.add_edge("a", "b", True, 0.95)
        ti.add_edge("b", "c", True, 0.95)
        ti.add_edge("d", "e", True, 0.95)  # Separate component

        component_a = ti.get_component("a")

        assert "a" in component_a
        assert "b" in component_a
        assert "c" in component_a
        assert "d" not in component_a  # Different component


class TestActiveLearner:
    """Test the active learner (QBC)."""

    def test_fit_and_predict(self):
        from core.active_learning import ActiveLearner

        learner = ActiveLearner(n_estimators=3)

        # Create simple training data
        X = np.array([
            [0.9, 0.8, 0.7, 0.9, 1.0, 1.0, 0.8],  # Match
            [0.85, 0.75, 0.65, 0.85, 1.0, 1.0, 0.75],  # Match
            [0.2, 0.1, 0.1, 0.5, 0.0, 0.0, 0.2],  # No match
            [0.15, 0.05, 0.05, 0.4, 0.0, 0.0, 0.15],  # No match
        ])
        y = np.array([1, 1, 0, 0])

        learner.fit(X, y)

        assert learner.is_fitted is True

        # Test prediction on similar item
        test_match = np.array([[0.88, 0.78, 0.68, 0.88, 1.0, 1.0, 0.78]])
        proba = learner.predict_proba(test_match)

        assert proba[0][1] > 0.5  # Should predict match

    def test_uncertainty(self):
        from core.active_learning import ActiveLearner

        learner = ActiveLearner(n_estimators=3)

        # Without fitting, everything should be uncertain
        X = np.array([[0.5, 0.5, 0.5, 0.5, 0.0, 0.0, 0.5]])
        uncertainty = learner.uncertainty(X)

        assert uncertainty[0] == 1.0  # Max uncertainty when not fitted


class TestQualityGates:
    """Test training data quality gates."""

    def test_high_confidence_passes(self):
        from core.features import PairFeatures, should_add_to_training

        features = PairFeatures(
            embedding_similarity=0.8,
            token_jaccard=0.5,
            trigram_jaccard=0.6,
            desc_length_ratio=0.9,
            same_category=True,
            verb_match=True,
            name_similarity=0.7,
        )

        # High confidence LLM decision should pass
        assert should_add_to_training(features, 0.95) is True

    def test_uncertain_fails(self):
        from core.features import PairFeatures, should_add_to_training

        features = PairFeatures(
            embedding_similarity=0.5,
            token_jaccard=0.3,
            trigram_jaccard=0.4,
            desc_length_ratio=0.8,
            same_category=True,
            verb_match=False,
            name_similarity=0.5,
        )

        # Uncertain LLM decision should be filtered
        assert should_add_to_training(features, 0.5) is False

    def test_suspicious_match_fails(self):
        from core.features import PairFeatures, should_add_to_training

        features = PairFeatures(
            embedding_similarity=0.1,  # Very low similarity
            token_jaccard=0.0,
            trigram_jaccard=0.1,
            desc_length_ratio=0.9,
            same_category=False,
            verb_match=False,
            name_similarity=0.1,
        )

        # LLM says "match" but features say "no way" - suspicious
        assert should_add_to_training(features, 0.95) is False


class TestCatBoostActiveLearner:
    """Test the CatBoost active learner."""

    def test_catboost_available(self):
        from core.active_learning import CATBOOST_AVAILABLE

        # This test documents whether CatBoost is installed in test environment
        # It should pass regardless of whether CatBoost is available
        assert isinstance(CATBOOST_AVAILABLE, bool)

    def test_fit_and_predict(self):
        import pytest

        from core.active_learning import CATBOOST_AVAILABLE

        if not CATBOOST_AVAILABLE:
            pytest.skip("CatBoost not installed")

        from core.active_learning import CatBoostActiveLearner

        learner = CatBoostActiveLearner(n_estimators=3)

        # Create training data (need enough for 3-fold CV calibration)
        X = np.array([
            [0.9, 0.8, 0.7, 0.9, 1.0, 1.0, 0.8],  # Match
            [0.85, 0.75, 0.65, 0.85, 1.0, 1.0, 0.75],  # Match
            [0.88, 0.78, 0.68, 0.88, 1.0, 0.0, 0.78],  # Match
            [0.92, 0.82, 0.72, 0.92, 1.0, 1.0, 0.82],  # Match
            [0.2, 0.1, 0.1, 0.5, 0.0, 0.0, 0.2],  # No match
            [0.15, 0.05, 0.05, 0.4, 0.0, 0.0, 0.15],  # No match
            [0.18, 0.08, 0.08, 0.45, 0.0, 0.0, 0.18],  # No match
            [0.22, 0.12, 0.12, 0.55, 0.0, 0.0, 0.22],  # No match
        ])
        y = np.array([1, 1, 1, 1, 0, 0, 0, 0])

        learner.fit(X, y)

        assert learner.is_fitted is True

        # Test prediction on similar item
        test_match = np.array([[0.88, 0.78, 0.68, 0.88, 1.0, 1.0, 0.78]])
        proba = learner.predict_proba(test_match)

        assert proba[0][1] > 0.5  # Should predict match

    def test_uncertainty_probability_std(self):
        import pytest

        from core.active_learning import CATBOOST_AVAILABLE

        if not CATBOOST_AVAILABLE:
            pytest.skip("CatBoost not installed")

        from core.active_learning import CatBoostActiveLearner

        learner = CatBoostActiveLearner(n_estimators=3)

        # Without fitting, everything should be uncertain
        X = np.array([[0.5, 0.5, 0.5, 0.5, 0.0, 0.0, 0.5]])
        uncertainty = learner.uncertainty(X)

        assert uncertainty[0] == 1.0  # Max uncertainty when not fitted

    def test_fit_with_early_stopping(self):
        import pytest

        from core.active_learning import CATBOOST_AVAILABLE

        if not CATBOOST_AVAILABLE:
            pytest.skip("CatBoost not installed")

        from core.active_learning import CatBoostActiveLearner

        learner = CatBoostActiveLearner(n_estimators=3)

        # Create larger training data for early stopping test
        np.random.seed(42)
        n_samples = 50
        X_match = np.random.uniform(0.7, 1.0, (n_samples // 2, 7))
        X_no_match = np.random.uniform(0.0, 0.3, (n_samples // 2, 7))
        X = np.vstack([X_match, X_no_match])
        y = np.array([1] * (n_samples // 2) + [0] * (n_samples // 2))

        learner.fit_with_early_stopping(X, y)

        assert learner.is_fitted is True
        assert len(learner.committee) == 3

    def test_teach_incremental(self):
        import pytest

        from core.active_learning import CATBOOST_AVAILABLE

        if not CATBOOST_AVAILABLE:
            pytest.skip("CatBoost not installed")

        from core.active_learning import CatBoostActiveLearner

        learner = CatBoostActiveLearner(n_estimators=3)

        # Initial training data
        X = np.array([
            [0.9, 0.8, 0.7, 0.9, 1.0, 1.0, 0.8],
            [0.85, 0.75, 0.65, 0.85, 1.0, 1.0, 0.75],
            [0.88, 0.78, 0.68, 0.88, 1.0, 0.0, 0.78],
            [0.2, 0.1, 0.1, 0.5, 0.0, 0.0, 0.2],
            [0.15, 0.05, 0.05, 0.4, 0.0, 0.0, 0.15],
            [0.18, 0.08, 0.08, 0.45, 0.0, 0.0, 0.18],
        ])
        y = np.array([1, 1, 1, 0, 0, 0])

        learner.fit(X, y)
        initial_samples = len(learner.X_train)

        # Teach new samples
        new_X = np.array([[0.91, 0.81, 0.71, 0.91, 1.0, 1.0, 0.81]])
        new_y = np.array([1])
        learner.teach(new_X, new_y)

        assert len(learner.X_train) == initial_samples + 1


class TestFactoryFunction:
    """Test the active learner factory function."""

    def test_factory_returns_learner(self):
        from core.active_learning import ActiveLearner, create_active_learner

        learner = create_active_learner(n_estimators=3, prefer_catboost=False)
        assert isinstance(learner, ActiveLearner)

    def test_factory_prefers_catboost_when_available(self):
        from core.active_learning import (
            CATBOOST_AVAILABLE,
            ActiveLearner,
            create_active_learner,
        )

        learner = create_active_learner(n_estimators=3, prefer_catboost=True)

        if CATBOOST_AVAILABLE:
            from core.active_learning import CatBoostActiveLearner

            assert isinstance(learner, CatBoostActiveLearner)
        else:
            assert isinstance(learner, ActiveLearner)


class TestBackwardCompatibility:
    """Test that existing training data format still works."""

    def test_load_existing_training_data(self):
        from core.active_learning import ActiveClassifier

        classifier = ActiveClassifier()

        # Simulate existing training data format
        existing_data = [
            {"features": [0.9, 0.8, 0.7, 0.9, 1.0, 1.0, 0.8], "label": 1},
            {"features": [0.85, 0.75, 0.65, 0.85, 1.0, 1.0, 0.75], "label": 1},
            {"features": [0.2, 0.1, 0.1, 0.5, 0.0, 0.0, 0.2], "label": 0},
            {"features": [0.15, 0.05, 0.05, 0.4, 0.0, 0.0, 0.15], "label": 0},
        ]

        # Should not raise
        classifier.load_training_data(existing_data)

        assert classifier.stats.training_samples == 4

    def test_export_import_roundtrip(self):
        from core.active_learning import ActiveClassifier

        classifier = ActiveClassifier()

        existing_data = [
            {"features": [0.9, 0.8, 0.7, 0.9, 1.0, 1.0, 0.8], "label": 1},
            {"features": [0.2, 0.1, 0.1, 0.5, 0.0, 0.0, 0.2], "label": 0},
        ]
        classifier.load_training_data(existing_data)

        exported = classifier.export_training_data()

        # Create new classifier and import
        new_classifier = ActiveClassifier()
        count = new_classifier.import_training_data(exported)

        assert count == 2
        assert new_classifier.stats.training_samples == 2

    def test_record_decision_trigger_retrain_default_false(self):
        """Test that trigger_retrain defaults to False (no inline retraining)."""
        from core.active_learning import ActiveClassifier
        from core.features import PairFeatures

        classifier = ActiveClassifier()

        # Load enough data to enable predictions
        existing_data = [
            {"features": [0.9, 0.8, 0.7, 0.9, 1.0, 1.0, 0.8], "label": 1},
            {"features": [0.85, 0.75, 0.65, 0.85, 1.0, 1.0, 0.75], "label": 1},
            {"features": [0.88, 0.78, 0.68, 0.88, 1.0, 0.0, 0.78], "label": 1},
            {"features": [0.2, 0.1, 0.1, 0.5, 0.0, 0.0, 0.2], "label": 0},
            {"features": [0.15, 0.05, 0.05, 0.4, 0.0, 0.0, 0.15], "label": 0},
            {"features": [0.18, 0.08, 0.08, 0.45, 0.0, 0.0, 0.18], "label": 0},
        ] * 5  # 30 samples
        classifier.load_training_data(existing_data)

        initial_fitted = classifier.learner.is_fitted

        # Record a decision without trigger_retrain (default)
        features = PairFeatures(
            embedding_similarity=0.9,
            token_jaccard=0.8,
            trigram_jaccard=0.7,
            desc_length_ratio=0.9,
            same_category=True,
            verb_match=True,
            name_similarity=0.8,
        )

        item_a = {"id": "test_a", "description": "Test A"}
        item_b = {"id": "test_b", "description": "Test B"}

        # This should add the record but NOT retrain
        result = classifier.record_decision(
            item_a, item_b, features, is_match=True, llm_confidence=0.95
        )

        assert result is True
        # Model state should be the same as before (no inline retrain)
        assert classifier.learner.is_fitted == initial_fitted
