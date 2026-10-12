"""Cache evaluated query results, with commit-aware invalidation.

Keys include the caller's owner/object IDs. Small, persistent generation keys
invalidate whole dependency groups without scanning Redis or flushing other apps.
"""

import hashlib
import json
import logging
from uuid import uuid4

from django.conf import settings
from django.core.cache import cache
from django.core.paginator import Paginator
from django.db import connections, models, transaction
from django.forms.models import ModelChoiceField, ModelChoiceIterator
from django.shortcuts import get_object_or_404
from django.utils.functional import cached_property
from redis.exceptions import RedisError

logger = logging.getLogger(__name__)
MISSING = object()
CACHE_ERRORS = (RedisError, OSError)
MODEL_GROUPS = {
    'profile.users': ('people',),
    'profile.student': ('people',),
    'profile.teacheruser': ('people',),
    'profile.schoolclass': ('people',),
    'question.exam': ('exams',),
    'question.examparticipation': ('participants',),
    'question.question': ('questions',),
    'question.subquestion': ('questions',),
    'question.studentquestionresult': ('grades',),
    'question.examsnapshot': ('snapshots',),
    'question.analysisbundle': ('bundles',),
    'question.analysisresult': ('bundles',),
    'question.prompttemplate': ('prompts',),
}


def cache_enabled():
    return getattr(settings, 'QUERY_CACHE_ENABLED', True)


def invalidate_groups(*groups, using='default'):
    """Only publish invalidation after SQL commits; rollback leaves cache valid."""
    if not cache_enabled() or not groups:
        return
    groups = tuple(set(groups))

    def invalidate():
        try:
            cache.set_many(
                {f'query-cache:v1:g:{group}': uuid4().hex for group in groups},
                timeout=None,
            )
        except CACHE_ERRORS:
            logger.warning('Query cache invalidation unavailable', exc_info=True)

    transaction.on_commit(invalidate, using=using)


def cached_value(name, identifiers, groups, timeout, factory, *, allow_in_atomic=False):
    """Never cache uncommitted SQL results. Redis outages fall back to SQL."""
    in_atomic = connections['default'].in_atomic_block
    if not cache_enabled() or (in_atomic and not allow_in_atomic):
        return factory()
    try:
        generation_keys = [f'query-cache:v1:g:{group}' for group in groups]
        generations = cache.get_many(generation_keys)
        missing = [key for key in generation_keys if key not in generations]
        for key in missing:
            cache.add(key, uuid4().hex, timeout=None)
        if missing:
            generations = cache.get_many(generation_keys)
        # If Redis lost a generation during the read, do not use an old key.
        if any(key not in generations for key in generation_keys):
            return factory()
        payload = json.dumps(
            [name, identifiers, [generations[key] for key in generation_keys]],
            sort_keys=True, default=str,
        )
        key = 'query-cache:v1:data:' + hashlib.sha256(payload.encode()).hexdigest()
        value = cache.get(key, MISSING)
    except CACHE_ERRORS:
        logger.warning('Query cache read unavailable; using SQL', exc_info=True)
        return factory()
    if value is not MISSING:
        return value
    value = factory()
    if not in_atomic:
        try:
            cache.set(key, value, timeout=timeout)
        except CACHE_ERRORS:
            logger.warning('Query cache write unavailable', exc_info=True)
    return value


class InvalidatingQuerySet(models.QuerySet):
    """Django's bulk writes skip model signals, so invalidate them explicitly."""

    def _invalidate(self):
        invalidate_groups(*MODEL_GROUPS.get(self.model._meta.label_lower.lower(), ()), using=self.db)

    def update(self, **kwargs):
        count = super().update(**kwargs)
        if count:
            self._invalidate()
        return count

    def bulk_create(self, objs, *args, **kwargs):
        rows = super().bulk_create(objs, *args, **kwargs)
        if rows:
            self._invalidate()
        return rows

    def bulk_update(self, objs, fields, *args, **kwargs):
        # Django implements this with update(), already covered above.
        return super().bulk_update(objs, fields, *args, **kwargs)


CacheInvalidatingManager = models.Manager.from_queryset(InvalidatingQuerySet)


class CachedPaginator(Paginator):
    def __init__(self, *args, cache_name, identifiers, groups, timeout=60, **kwargs):
        self.cache_name = cache_name
        self.identifiers = identifiers
        self.groups = groups
        self.timeout = timeout
        super().__init__(*args, **kwargs)

    @cached_property
    def count(self):
        return cached_value(
            self.cache_name + ':count', self.identifiers, self.groups,
            self.timeout, lambda: self.object_list.count(),
        )

    def _get_page(self, object_list, number, paginator):
        rows = cached_value(
            self.cache_name + ':page', (*self.identifiers, number, self.per_page),
            self.groups, self.timeout, lambda: list(object_list),
        )
        return super()._get_page(rows, number, paginator)


class CachedListMixin:
    cache_groups = ('exams', 'bundles', 'people', 'prompts')
    cache_timeout = 60

    def get_paginator(self, queryset, per_page, orphans=0, allow_empty_first_page=True, **kwargs):
        return CachedPaginator(
            queryset, per_page, orphans=orphans,
            allow_empty_first_page=allow_empty_first_page,
            cache_name=type(self).__name__,
            identifiers=(self.request.user.pk, tuple(sorted(self.kwargs.items()))),
            groups=self.cache_groups, timeout=self.cache_timeout, **kwargs,
        )


class CachedBundleDetailMixin:
    def get_object(self, queryset=None):
        if not cache_enabled() or connections['default'].in_atomic_block:
            return super().get_object(queryset=queryset)
        queryset = self.get_queryset() if queryset is None else queryset
        pk = self.kwargs[self.pk_url_kwarg]
        # Recheck ownership and success status before serving a cached payload.
        metadata = get_object_or_404(
            queryset.select_related(None).values('pk', 'status'), pk=pk,
        )
        if metadata['status'] != 'success':
            return super().get_object(queryset=queryset)
        return cached_value(
            type(self).__name__, (self.request.user.pk, pk),
            ('bundles', 'exams', 'prompts', 'people'), 3600,
            lambda: super(CachedBundleDetailMixin, self).get_object(queryset=queryset),
        )


class CachedPromptIterator(ModelChoiceIterator):
    def _choices(self):
        return cached_value(
            'prompt-choices', (self.field.cache_variant,), ('prompts',), 1800,
            lambda: [(obj.pk, self.field.label_from_instance(obj))
                     for obj in self.queryset.only('id', 'name', 'version')],
        )

    def __iter__(self):
        if self.field.empty_label is not None:
            yield ('', self.field.empty_label)
        yield from self._choices()

    def __len__(self):
        return len(self._choices()) + int(self.field.empty_label is not None)

    def __bool__(self):
        return self.field.empty_label is not None or bool(self._choices())


class CachedPromptChoiceField(ModelChoiceField):
    """Cache display choices only; inherited to_python validates against live SQL."""

    iterator = CachedPromptIterator

    def __init__(self, *args, cache_variant, **kwargs):
        self.cache_variant = cache_variant
        super().__init__(*args, **kwargs)
