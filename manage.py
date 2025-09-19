#!/usr/bin/env python
"""
Copyright (c) 2019 - present AppSeed.us
"""

import os
import sys
from pathlib import Path
def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings.production')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

    current_path = Path(__file__).parent.resolve()
    sys.path.append(str(current_path / "apps")) # this appends the apps folder to the python path
    # but we are already in the apps folder so we don't need to append it



    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()
