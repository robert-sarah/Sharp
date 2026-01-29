#!/usr/bin/env python
"""
Wrapper script to run gui.py with warnings suppressed.
"""
import warnings
warnings.simplefilter("ignore")

from gui import main

if __name__ == "__main__":
    main()
