# setup/__init__.py

"""
Setup package for the Project Analyzer.
This package contains setup and configuration utilities.
"""

from .setup import setup

__all__ = ['setup']

# Version information
VERSION = '1.0.0'
AUTHOR = 'Your Name'
EMAIL = 'your.email@example.com'
DESCRIPTION = 'Multi-Agent Model Project Analyzer'

# Package metadata
metadata = {
    'name': 'mam_project',
    'version': VERSION,
    'author': AUTHOR,
    'author_email': EMAIL,
    'description': DESCRIPTION,
    'long_description': open('../README.md').read(),
    'long_description_content_type': 'text/markdown',
    'url': 'https://github.com/yourusername/mam_project',
    'project_urls': {
        'Bug Tracker': 'https://github.com/yourusername/mam_project/issues',
        'Documentation': 'https://github.com/yourusername/mam_project/wiki',
        'Source Code': 'https://github.com/yourusername/mam_project',
    },
    'classifiers': [
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ]
}
