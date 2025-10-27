#!/usr/bin/env python
"""
Trigger the /sentry-debug/ URL using Django test client and print Sentry event id.
Run from project root:
    D:\code\onField\virtualEnvironment\Scripts\python.exe trigger_sentry_url.py
"""
import os
import django

# Ensure the test client host is allowed. The test client uses 'testserver' as HTTP_HOST.
# Add it to ALLOWED_HOSTS env before settings are loaded so decouple picks it up.
os.environ.setdefault('ALLOWED_HOSTS', 'localhost,127.0.0.1,testserver')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'OnFieldRecording.settings')
# django.setup() will initialize sentry via settings
django.setup()

from django.test import Client
import sentry_sdk


def main():
    client = Client()
    url = '/sentry-debug/'
    print(f"Triggering {url} ...")
    try:
        resp = client.get(url)
        print("Unexpected response (no exception):", resp.status_code)
    except Exception as exc:
        print("View raised exception as expected:", repr(exc))
        event_id = sentry_sdk.last_event_id()
        if event_id:
            print("✅ Sentry event id:", event_id)
            print("Check Sentry dashboard for this event id.")
        else:
            print("⚠️ No Sentry event id returned. Sentry may have sampling or network issues.")


if __name__ == '__main__':
    main()
