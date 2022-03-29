# encoding: utf-8

from logging import getLogger
import click
from ckan.model import Session, Package, DomainObjectOperation
from ckan.model.modification import DomainObjectModificationExtension
from ckan.logic import NotAuthorized, ValidationError


log = getLogger(__name__)


@click.group(name="notify", short_help="Send out modification notifications.")
def notify():
    pass


@notify.command(name="replay", short_help="Send out modification signals.")
def replay():
    dome = DomainObjectModificationExtension()
    for package in Session.query(Package):
        dome.notify(package, DomainObjectOperation.changed)


@notify.command(name="send_emails", short_help="Send out Email notifications.")
def send_emails():
    """
    As currently implemented, it will only send notifications from dashboard 
    activity list.

    It will send emails to users who have `activity_streams_email_notifications`
    set in their profile.

    It will send emails with updates depending on how `ckan.email_notifications_since` 
    is configured.
    The default value is 2 days.
    """
    import ckan.logic as logic
    import ckan.lib.mailer as mailer
    from ckan.types import Context
    from typing import cast

    site_user = logic.get_action("get_site_user")({"ignore_auth": True}, {})
    context = cast(Context, {"user": site_user["name"]})
    try:
        logic.get_action("send_email_notifications")(context, {})
    except (NotAuthorized, ValidationError, mailer.MailerException) as e:
        log.error(e)
