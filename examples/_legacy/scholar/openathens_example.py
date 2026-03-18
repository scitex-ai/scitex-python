#!/usr/bin/env python3
"""
Example of using Scholar with OpenAthens authentication.

OpenAthens is now fully implemented and working!
"""

from scitex.scholar import Scholar, ScholarConfig

# Configure Scholar with OpenAthens
config = ScholarConfig(
    # Existing configuration
    pubmed_email="researcher@unimelb.edu.au",

    # OpenAthens configuration (now working!)
    openathens_enabled=True,
    openathens_email="researcher@unimelb.edu.au",
    # Email is used for:
    # 1. Session caching (encrypted)
    # 2. Auto-filling login forms
    # 3. Identifying your institution
)

# Initialize Scholar
scholar = Scholar(config=config)

# Search for papers
papers = scholar.search("deep learning neuroscience", limit=5)
print(f"Found {len(papers)} papers")

# Download PDFs - will use OpenAthens authentication automatically
results = scholar.download_pdfs(papers)

print(f"\nDownload Results:")
print(f"Downloaded {len(results)} papers successfully!")

# The download process tries in this order:
# 1. Direct download (if open access)
# 2. OpenAthens authentication (if configured and paper available via institution)
# 3. Sci-Hub (if ethical usage acknowledged)
# 4. Zotero translators (for additional sources)

# Advanced usage: Explicit authentication
# Check if already authenticated
if not scholar.is_openathens_authenticated():
    print("\nAuthenticating with OpenAthens...")
    success = scholar.authenticate_openathens()
    if success:
        print("✅ Authentication successful!")
    else:
        print("❌ Authentication failed")

# All subsequent downloads use the authenticated session
more_papers = scholar.search("neuroscience methods", limit=10)
scholar.download_pdfs(more_papers)
