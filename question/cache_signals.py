"""Invalidate dependencies for ordinary/admin writes and membership changes."""

from django.apps import apps
from django.db.models.signals import m2m_changed, post_delete, post_save

from ai_asistant_with_sina.query_cache import MODEL_GROUPS, invalidate_groups


def model_changed(sender, instance, using, **kwargs):
    label = sender._meta.label_lower.lower()
    if label == 'profile.users' and kwargs.get('update_fields') == frozenset({'last_login'}):
        return
    invalidate_groups(*MODEL_GROUPS[label], using=using)


for model in apps.get_models():
    label = model._meta.label_lower.lower()
    if label not in MODEL_GROUPS:
        continue
    post_save.connect(model_changed, sender=model, dispatch_uid=f'query-cache-save:{label}')
    post_delete.connect(model_changed, sender=model, dispatch_uid=f'query-cache-delete:{label}')


def membership_changed(sender, action, using, **kwargs):
    if action in {'post_add', 'post_remove', 'post_clear'}:
        invalidate_groups('people', using=using)


for label, field in [('Profile.TeacherUser', 'students'), ('Profile.Student', 'classes'), ('Profile.Student', 'teachers')]:
    through = apps.get_model(label)._meta.get_field(field).remote_field.through
    m2m_changed.connect(membership_changed, sender=through, dispatch_uid=f'query-cache-m2m:{label}:{field}')
