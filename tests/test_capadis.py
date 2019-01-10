#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `capadis` package."""


import unittest
from click.testing import CliRunner

from capadis.capadis import Capadis
from capadis import cli


class TestCapadis(unittest.TestCase):
    """Tests for `capadis` package."""

    def setUp(self):
        """Set up test fixtures, if any."""
        self.capad = Capadis()

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_000_something(self):
        """Test something."""

    def test_command_line_interface(self):
        """Test the CLI."""
        runner = CliRunner()
        result = runner.invoke(cli.main)
        assert result.exit_code == 0
        assert 'capadis.cli.main' in result.output
        help_result = runner.invoke(cli.main, ['--help'])
        assert help_result.exit_code == 0
        assert '--help  Show this message and exit.' in help_result.output

    def test_capadis(self):
        """Test the Capadis"""
        x = b'\xee\x03\x09\x12\x0b\x0e\x0f5.\xed'
        x1 = b'\xee\x04\x01'
        x2 = b'\x12\x0b\x0e\x0f5-\xed'
        result1 = self.capad.received(x1)
        result2 = self.capad.received(x2+x)
        self.assertEqual(None, result1)
        self.assertTrue(result2)


if __name__ == "__main__":
    unittest.main()
