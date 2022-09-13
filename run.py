#!/usr/bin/env python3
import os
import sys
import re

from gcodegenerator import main

if __name__ == "__main__":
    sys.argv[0] = re.sub(r'(-script\.pyw|\.exe)?$', '', sys.argv[0])
    sys.exit(main())
