#!/usr/bin/env python
# -*- coding: utf-8 -*-

#----------------------------------------------------------------------------------------------------------------------------------
# includes

# 2+3 compat
from __future__ import absolute_import, division, print_function, unicode_literals

# standards
from os.path import basename, dirname, join as path_join
from unittest import TestCase

# flott
from flott import Flott, MemberNotFound

#----------------------------------------------------------------------------------------------------------------------------------

fixtures_path = path_join(
    dirname(__file__),
    'fixtures',
)

class TestMember(object):

    id = None

    def __init__(self):
        if self.id is None:
            self.id = self.__class__.__name__

#----------------------------------------------------------------------------------------------------------------------------------

class TestFlott(TestCase):

    def setUp(self):
        self.flott = Flott(TestMember, fixtures_path)

    def test_load_alpha(self):
        member = self.flott.load_member_by_id('Alpha')
        self.assertIsInstance(member, TestMember)
        self.assertEqual(member.id, 'Alpha')

    def test_load_beta(self):
        member = self.flott.load_member_by_id('Beta')
        self.assertIsInstance(member, TestMember)
        self.assertEqual(member.id, 'Beta')

    def test_load_gamma(self):
        member = self.flott.load_member_by_id('Gamma')
        self.assertIsInstance(member, TestMember)
        self.assertEqual(member.id, 'Gamma')

    def test_load_all(self):
        member_ids = list(s.id for s in self.flott.all_members())
        self.assertEqual(
            member_ids,
            ['Alpha', 'Beta', 'Gamma'],
        )

#----------------------------------------------------------------------------------------------------------------------------------

class VerboseFlott(Flott):

    def __init__(self, *args, **kwargs):
        super(VerboseFlott, self).__init__(*args, **kwargs)
        self.first_file_loaded = None

    def _load_members_from_file(self, file_path):
        if self.first_file_loaded is None:
            self.first_file_loaded = basename(file_path)
        return super(VerboseFlott, self)._load_members_from_file(file_path)


class TestLoadOrder(TestCase):

    def setUp(self):
        self.flott = VerboseFlott(TestMember, fixtures_path)

    def test_load_alpha(self):
        member = self.flott.load_member_by_id('Alpha')
        self.assertEqual(
            self.flott.first_file_loaded,
            'alpha.py',
        )

    def test_load_beta(self):
        member = self.flott.load_member_by_id('Beta')
        self.assertEqual(
            self.flott.first_file_loaded,
            'beta.py',
        )

    def test_load_gamma(self):
        member = self.flott.load_member_by_id('Gamma')
        self.assertEqual(
            self.flott.first_file_loaded,
            'gamma.py',
        )

    def test_load_alphabet(self):
        with self.assertRaises(MemberNotFound):
            self.flott.load_member_by_id('Alphabet')
        self.assertEqual(
            self.flott.first_file_loaded,
            'alpha.py',
        )

    def test_load_tibetan(self):
        with self.assertRaises(MemberNotFound):
            self.flott.load_member_by_id('Tibetan')
        self.assertEqual(
            self.flott.first_file_loaded,
            'beta.py',
        )

    def test_load_grammar(self):
        with self.assertRaises(MemberNotFound):
            self.flott.load_member_by_id('Grammar')
        self.assertEqual(
            self.flott.first_file_loaded,
            'gamma.py',
        )

#----------------------------------------------------------------------------------------------------------------------------------
