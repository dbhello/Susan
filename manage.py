#!/usr/bin/env python
import os
import sys
from management.mail_notification import run_scheduler

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "LM.settings")

    from django.core.management import execute_from_command_line

    run_scheduler()

    execute_from_command_line(sys.argv)
