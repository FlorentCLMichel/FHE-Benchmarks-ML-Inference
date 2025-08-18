#!/usr/bin/env python3
"""
params.py - Parameters and directory structure for the submission.
"""

from pathlib import Path

# Enum for benchmark size
SINGLE = 0
SMALL = 1
MEDIUM = 2
LARGE = 3

def instance_name(size):
    """Return the string name of the instance size."""
    if size > LARGE:
        return "unknown"
    names = ["single", "small", "medium", "large"]
    return names[size]

class InstanceParams:
    """Parameters that differ for different instance sizes."""

    def __init__(self, size, rootdir=None):
        """Constructor."""
        self.size = size
        self.rootdir = Path(rootdir) if rootdir else Path.cwd()

        if size > LARGE:
            raise ValueError("Invalid instance size")
        
        # Andreea: changed SMALL to 10 for debugging purposes
        batch_size =              [1, 10, 1000, 10000]

        self.batch_size = batch_size[size]

    def get_size(self):
        """Return the instance size."""
        return self.size

    # Directory structure methods
    def subdir(self):
        """Return the submission directory of this repository."""
        return self.rootdir

    def datadir(self):
        """Return the dataset directory path."""
        return self.rootdir / "datasets" / instance_name(self.size)
    
    def dataset_intermediate_dir(self):
        """Return the intermediate  directory path."""
        return self.datadir() / "intermediate"

    def iodir(self):
        """Return the I/O directory path."""
        return self.rootdir / "io" / instance_name(self.size)

    def io_intermediate_dir(self):
        """Return the intermediate  directory path."""
        return self.iodir() / "intermediate"

    def measuredir(self):
        """Return the measurements directory path."""
        return self.rootdir / "measurements" / instance_name(self.size)
    
    def get_batch_size(self):
        """Return the number of items in the batch."""
        return self.batch_size