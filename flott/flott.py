#!/usr/bin/env python
# -*- coding: utf-8 -*-

#----------------------------------------------------------------------------------------------------------------------------------
# includes

# 2+3 compat
from __future__ import absolute_import, division, print_function, unicode_literals

# standards
from glob import glob
import logging
from os.path import basename, join as path_join, splitext

# flott
from .compatibility import execfile
from .exceptions import MemberNotFound

#----------------------------------------------------------------------------------------------------------------------------------

class Flott(object):

    def __init__(self, root_class, root_dir, namespace={}):
        self.root_class = root_class
        self.root_dir = root_dir
        self.namespace = dict(namespace)
        self.namespace[root_class.__name__] = root_class

    def _load_members_from_file(self, file_path, kwargs):
        file_locals = dict(self.namespace)
        try:
            execfile(file_path, file_locals, file_locals)
        except Exception as error:
            logging.error("Failed to load '%s': %s" % (file_path, error))
        else:
            for key, value in file_locals.items():
                if key not in self.namespace \
                        and isinstance(value, type) \
                        and issubclass(value, self.root_class):
                    member = value(**kwargs)
                    yield member

    def _list_source_file_paths(self, sort_key=None):
        if sort_key is None:
            sort_key = lambda file_path: self._normalize_id(file_path)
            reverse = False
        else:
            reverse = True
        return sorted(
            glob(path_join(self.root_dir, '*.py')),
            key=lambda file_path: sort_key(splitext(basename(file_path))[0]),
            reverse=reverse,
        )

    def all_members(self, kwargs={}, sort_key=None):
        for file_path in self._list_source_file_paths(sort_key):
            for member in self._load_members_from_file(file_path, kwargs):
                yield member

    def load_member_by_id(self, member_id):
        similarity = self._string_similarity(member_id)
        all_member_ids = []
        for member in self.all_members(sort_key=similarity):
            all_member_ids.append(member.id)
            if member.id == member_id:
                return member
        raise MemberNotFound("No member with ID '%s'. Did you mean '%s'?" % (
            member_id,
            min(all_member_ids, key=similarity)
        ))

    def members_from_command_line_arguments(self, arguments, **kwargs):
        if len(arguments) == 0:
            for member in self.all_members(kwargs):
                yield member
        else:
            selected_member_ids = set(arguments)
            for member in self.all_members(
                    kwargs,
                    sort_key=self._string_similarity(arguments[0]),
                    ):
                if member.id in selected_member_ids:
                    selected_member_ids.remove(member.id)
                    yield member
            if len(selected_member_ids) > 0:
                # On the one hand, we'd like to raise this before we've loaded all members, but otoh this has to be a generator,
                # because each member could have expensive resources associated with it. So we settle for this.
                raise MemberNotFound("Unknown member%s: %s" % (
                    '' if len(selected_member_ids) == 1 else 's',
                    ', '.join(sorted(selected_member_ids)),
                ))

    @classmethod
    def _string_similarity(cls, reference_text):
        chunk_size = 2
        chunks = lambda text: set(
            text[i:i+chunk_size]
            for i in range(len(text)-chunk_size)
        )
        reference_chunks = chunks(cls._normalize_id(reference_text))
        if not reference_chunks:
            return lambda text: 0.5
        overlap = lambda text_chunks: (
            2 * len(text_chunks & reference_chunks)
            / (len(text_chunks) + len(reference_chunks))
        )
        return lambda text: overlap(chunks(cls._normalize_id(text)))

    @staticmethod
    def _normalize_id(member_id):
        return member_id.lower()

#----------------------------------------------------------------------------------------------------------------------------------
