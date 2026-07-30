"""
Outbound mail.

Adze has never sent an email. integrations/purelymail.py wraps Purelymail's
*admin* API -- it creates mailboxes and forwarding rules, it does not send
anything. This is the transport, and it is what makes password reset possible
at all: no artist has a login email today, so "forgot my password" currently
means phoning Gabriel.

Everything here is best-effort by design. The caller's write (a feedback
record, a reset row) is the source of truth; the email is a notification. A
dead mailbox, a blocked port or a wrong password must never make an artist's
action fail, so send_async swallows and logs.

Configuration -- all optional. With nothing set, is_configured() is False,
send() returns (False, 'not configured') and callers degrade quietly:

    ADZE_SMTP_HOST      default smtp.purelymail.com (workspaces.py:32)
    ADZE_SMTP_PORT      default 465 (implicit TLS)
    ADZE_SMTP_USER      the sending mailbox, e.g. noreply@adze.studio
    ADZE_SMTP_PASSWORD  that mailbox's password -- NOT PURELYMAIL_API_TOKEN,
                        which is an account API token and cannot authenticate
                        an SMTP session
    ADZE_SMTP_FROM      default "Adze <${ADZE_SMTP_USER}>"
    ADZE_SMTP_REPLY_TO  default unset
    ADZE_FEEDBACK_TO    where artist feedback is sent
"""

import os
import smtplib
import ssl
import threading
from email.message import EmailMessage

# Bound concurrent sends so a burst can't spawn unbounded threads.
_send_slots = threading.Semaphore(4)


def _cfg():
    host = os.environ.get('ADZE_SMTP_HOST') or 'smtp.purelymail.com'
    try:
        port = int(os.environ.get('ADZE_SMTP_PORT') or 465)
    except ValueError:
        port = 465
    user = os.environ.get('ADZE_SMTP_USER') or ''
    pw = os.environ.get('ADZE_SMTP_PASSWORD') or ''
    sender = os.environ.get('ADZE_SMTP_FROM') or (f'Adze <{user}>' if user else '')
    return host, port, user, pw, sender


def is_configured():
    _, _, user, pw, _ = _cfg()
    return bool(user and pw)


def default_recipient():
    return os.environ.get('ADZE_FEEDBACK_TO') or ''


def send(to, subject, text_body, html_body=None, reply_to=None):
    """Send one message. Returns (ok, error). Blocks -- prefer send_async from
    a request handler."""
    host, port, user, pw, sender = _cfg()
    if not (user and pw):
        return False, 'not configured'
    to = to or default_recipient()
    if not to:
        return False, 'no recipient'

    msg = EmailMessage()
    msg['From'] = sender
    msg['To'] = to
    msg['Subject'] = subject
    rt = reply_to or os.environ.get('ADZE_SMTP_REPLY_TO')
    if rt:
        msg['Reply-To'] = rt
    msg.set_content(text_body)
    if html_body:
        msg.add_alternative(html_body, subtype='html')

    # Port 465 is implicit TLS; 587 is STARTTLS. This host can only use 587 --
    # Hetzner blocks outbound 465, 25 and 2525, which presents as a bare
    # connect timeout rather than a refusal, so it looks like a wrong password
    # until you port-scan. Don't "fix" a timeout by changing credentials.
    try:
        ctx = ssl.create_default_context()
        if port == 465:
            with smtplib.SMTP_SSL(host, port, timeout=20, context=ctx) as s:
                s.login(user, pw)
                s.send_message(msg)
        else:
            with smtplib.SMTP(host, port, timeout=20) as s:
                s.ehlo()
                s.starttls(context=ctx)
                s.ehlo()
                s.login(user, pw)
                s.send_message(msg)
        return True, None
    except Exception as e:
        return False, f'{type(e).__name__}: {e}'


def send_async(subject, text_body, to=None, html_body=None, reply_to=None):
    """Fire and forget.

    Threaded rather than synchronous for two reasons: an SMTP handshake is
    2-10s and would make the caller feel broken, and on the password-reset
    path a synchronous send is a timing oracle that tells an attacker whether
    an account exists.
    """
    def _run():
        with _send_slots:
            ok, err = send(to, subject, text_body, html_body, reply_to)
            if not ok:
                print(f'[mailer] send failed ({err}): {subject!r} -> {to or default_recipient()!r}')

    threading.Thread(target=_run, daemon=True).start()


# Reset mail says this out loud because the mail itself is unreadable if it
# lands in spam -- the warning has to survive being filed there.
SPAM_WARNING = ("If this doesn't arrive in a few minutes, check your spam or "
                "junk folder -- it often ends up there the first time.")
