#!/usr/bin/env python3
"""
Unit tests for Hand Gesture Cursor Control
Tests core functionality without requiring webcam access.
"""

import unittest
import sys
from unittest.mock import Mock, patch, MagicMock
import math

# Mock the dependencies before importing
sys.modules['cv2'] = MagicMock()
sys.modules['mediapipe'] = MagicMock()
sys.modules['pyautogui'] = MagicMock()

from hand_cursor_control import HandCursorController

class TestHandCursorController(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures"""
        with patch('hand_cursor_control.pyautogui.size', return_value=(1920, 1080)):
            self.controller = HandCursorController()
    
    def test_initialization(self):
        """Test controller initialization"""
        self.assertEqual(self.controller.screen_width, 1920)
        self.assertEqual(self.controller.screen_height, 1080)
        self.assertEqual(self.controller.prev_x, 0)
        self.assertEqual(self.controller.prev_y, 0)
        self.assertFalse(self.controller.click_performed)
        self.assertFalse(self.controller.paused)
    
    def test_calculate_distance(self):
        """Test distance calculation between two points"""
        # Create mock points
        point1 = Mock()
        point1.x = 0.0
        point1.y = 0.0
        
        point2 = Mock()
        point2.x = 3.0
        point2.y = 4.0
        
        distance = self.controller.calculate_distance(point1, point2)
        self.assertAlmostEqual(distance, 5.0, places=5)
    
    def test_smooth_coordinates(self):
        """Test coordinate smoothing"""
        # First call
        smooth_x, smooth_y = self.controller.smooth_coordinates(100, 100)
        self.assertEqual(smooth_x, 20)  # (0 + (100-0)/5)
        self.assertEqual(smooth_y, 20)
        
        # Second call - should smooth towards target
        smooth_x, smooth_y = self.controller.smooth_coordinates(100, 100)
        self.assertGreater(smooth_x, 20)
        self.assertLess(smooth_x, 100)
    
    def test_is_fist_closed(self):
        """Test fist detection logic"""
        # Create mock hand landmarks
        hand_landmarks = Mock()
        landmarks = []
        
        # Create 21 landmarks (standard for MediaPipe hands)
        for i in range(21):
            landmark = Mock()
            landmark.x = 0.5
            landmark.y = 0.5
            landmarks.append(landmark)
        
        hand_landmarks.landmark = landmarks
        
        # Test with folded fingers (fist closed)
        # Set finger tips below knuckles (higher y value)
        for tip_idx in [8, 12, 16, 20]:
            landmarks[tip_idx].y = 0.7
        
        for mcp_idx in [5, 9, 13, 17]:
            landmarks[mcp_idx].y = 0.5
        
        # Thumb
        landmarks[4].x = 0.3
        landmarks[2].x = 0.5
        
        result = self.controller.is_fist_closed(hand_landmarks)
        self.assertTrue(result)
        
        # Test with extended fingers (fist open)
        for tip_idx in [8, 12, 16, 20]:
            landmarks[tip_idx].y = 0.3
        
        result = self.controller.is_fist_closed(hand_landmarks)
        self.assertFalse(result)
    
    def test_click_cooldown(self):
        """Test that clicks respect cooldown period"""
        self.controller.last_click_time = 0
        self.controller.click_cooldown = 0.3
        
        # First click should be allowed
        self.assertFalse(self.controller.click_performed)
        
        # Set last click time to now
        import time
        self.controller.last_click_time = time.time()
        
        # Should be in cooldown
        self.assertTrue(time.time() - self.controller.last_click_time < self.controller.click_cooldown)
    
    def test_configuration_loading(self):
        """Test that configuration is properly loaded"""
        self.assertGreater(self.controller.smooth_factor, 0)
        self.assertGreater(self.controller.click_cooldown, 0)
        self.assertGreater(self.controller.pause_cooldown, 0)
        self.assertGreater(self.controller.pinch_threshold, 0)

class TestDistanceCalculation(unittest.TestCase):
    """Test standalone distance calculations"""
    
    def test_zero_distance(self):
        """Test distance when points are same"""
        controller = Mock()
        controller.calculate_distance = HandCursorController.calculate_distance.__get__(controller, type(controller))
        
        point = Mock()
        point.x = 0.5
        point.y = 0.5
        
        distance = controller.calculate_distance(point, point)
        self.assertEqual(distance, 0.0)
    
    def test_pythagorean_distance(self):
        """Test distance follows Pythagorean theorem"""
        controller = Mock()
        controller.calculate_distance = HandCursorController.calculate_distance.__get__(controller, type(controller))
        
        point1 = Mock()
        point1.x = 0.0
        point1.y = 0.0
        
        point2 = Mock()
        point2.x = 0.06
        point2.y = 0.08
        
        distance = controller.calculate_distance(point1, point2)
        expected = math.sqrt(0.06**2 + 0.08**2)
        self.assertAlmostEqual(distance, expected, places=5)

def run_tests():
    """Run all tests"""
    print("=" * 60)
    print("Running Hand Gesture Cursor Control Tests")
    print("=" * 60)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add tests
    suite.addTests(loader.loadTestsFromTestCase(TestHandCursorController))
    suite.addTests(loader.loadTestsFromTestCase(TestDistanceCalculation))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
