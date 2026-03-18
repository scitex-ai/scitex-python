#!/usr/bin/env python3
"""
Simple working example for ZenRowsOpenURLResolver.

This is the corrected version of the user's code.
"""

from scitex.scholar.open_url import ZenRowsOpenURLResolver
from scitex.scholar.auth import AuthenticationManager
import os
from scitex import logging

# Enable debug logging
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# Initialize authentication
auth_manager = AuthenticationManager(
    email_openathens=os.getenv("SCITEX_SCHOLAR_OPENATHENS_EMAIL")
)

# Initialize ZenRows resolver
resolver = ZenRowsOpenURLResolver(
    auth_manager,
    os.getenv("SCITEX_SCHOLAR_OPENURL_RESOLVER_URL"),
    os.getenv("SCITEX_SCHOLAR_ZENROWS_API_KEY")
)

# DOIs to resolve
dois = [
    "10.1002/hipo.22488",
    "10.1038/nature12373",
    "10.1016/j.neuron.2018.01.048",
    "10.1126/science.1172133",
    "10.1073/pnas.0608765104",  # Known anti-bot issues
]

# CORRECTED: Use resolve_doi_sync instead of _resolve_single
# The underscore methods are internal and async
result = resolver.resolve_doi_sync(doi=dois[0])

print(f"Resolved URL: {result}")

# Or resolve all DOIs
print("\nResolving all DOIs...")
for doi in dois:
    result = resolver.resolve_doi_sync(doi=doi)
    print(f"{doi}: {result or 'No access'}")
