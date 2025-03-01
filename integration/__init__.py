# integration/__init__.py

"""
Integration package for the Project Analyzer.
This package contains the integration layer that coordinates all agents.
"""

from .integration_layer import IntegrationLayer, IntegrationError

__all__ = ['IntegrationLayer', 'IntegrationError']
