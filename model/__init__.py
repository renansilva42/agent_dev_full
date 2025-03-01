# model/__init__.py

"""
Model package for the Project Analyzer.
This package contains the transformer model and related utilities.
"""

from .transformer_model import TransformerModel, OpenAIError

__all__ = ['TransformerModel', 'OpenAIError']
