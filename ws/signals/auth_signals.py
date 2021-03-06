from __future__ import unicode_literals

from django.contrib import messages
from django.contrib.auth.models import Group
from django.db.models.signals import post_save, pre_delete, post_delete
from django.dispatch import receiver

from ws.models import LeaderRating, Participant


leaders_group = Group.objects.get(name='leaders')
users_with_info = Group.objects.get(name='users_with_info')


def update_leader_status(participant):
    leader_ratings = participant.leaderrating_set.filter(active=True)
    if not leader_ratings.exists():
        leaders_group.user_set.remove(participant.user)


@receiver(post_save, sender=LeaderRating)
def add_leader_perms(sender, instance, created, raw, using, update_fields,
                     **kwargs):
    if created:
        leaders_group.user_set.add(instance.participant.user)
    else:
        update_leader_status(instance.participant)


@receiver(post_delete, sender=LeaderRating)
def remove_leader_perms(sender, instance, using, **kwargs):
    update_leader_status(instance.participant)


@receiver(post_save, sender=Participant)
def has_info(sender, instance, created, raw, using, update_fields, **kwargs):
    users_with_info.user_set.add(instance.user)


@receiver(pre_delete, sender=Participant)
def no_more_info(sender, instance, using, **kwargs):
    users_with_info.user_set.remove(instance.user)
