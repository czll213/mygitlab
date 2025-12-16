#!/usr/bin/env python3
"""
Student Information Management System
Main entry point for the application
"""

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.main import main

if __name__ == "__main__":
    main()