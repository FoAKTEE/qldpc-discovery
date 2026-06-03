"""Put the src/ layout package on sys.path for pytest (robust across pytest versions)."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
