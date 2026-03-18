#!/usr/bin/env python3
"""
Hybrid workflow: Use ZenRows for discovery, standard resolver for downloads.

This shows how to get the benefits of both resolvers:
- ZenRows: Fast discovery, bypass rate limits, handle CAPTCHAs
- Standard: Authenticated access to paywalled content
"""

import os
import asyncio
from typing import List, Dict, Tuple
from scitex.scholar.open_url import OpenURLResolver, ZenRowsOpenURLResolver
from scitex.scholar.auth import AuthenticationManager
from scitex.scholar import Scholar
from scitex import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HybridResolverWorkflow:
    """Combines ZenRows and standard resolvers for optimal workflow."""

    def __init__(self):
        """Initialize both resolvers."""
        # Set API keys
        os.environ["SCITEX_SCHOLAR_2CAPTCHA_API_KEY"] = "36d184fbba134f828cdd314f01dc7f18"

        # Initialize authentication
        self.auth_manager = AuthenticationManager(
            email_openathens=os.getenv("SCITEX_SCHOLAR_OPENATHENS_EMAIL")
        )

        # Initialize resolvers
        resolver_url = os.getenv("SCITEX_SCHOLAR_OPENURL_RESOLVER_URL")

        # ZenRows for discovery (fast, handles CAPTCHAs)
        self.zenrows_resolver = ZenRowsOpenURLResolver(
            self.auth_manager,
            resolver_url,
            os.getenv("SCITEX_SCHOLAR_ZENROWS_API_KEY"),
            enable_captcha_solving=True
        )

        # Standard for authenticated access
        self.standard_resolver = OpenURLResolver(
            self.auth_manager,
            resolver_url
        )

        # Scholar for integrated workflow
        self.scholar = Scholar()

    async def discover_access_async(self, dois: List[str]) -> Dict[str, Dict]:
        """
        Phase 1: Use ZenRows to quickly discover which papers might be accessible.

        Benefits:
        - Fast parallel checking
        - Bypasses rate limits
        - Handles CAPTCHAs automatically
        """
        print("\n🔍 PHASE 1: Discovery with ZenRows")
        print("="*50)

        results = {}
        tasks = []

        for doi in dois:
            task = self._check_single_doi(doi)
            tasks.append(task)

        # Check all DOIs in parallel
        discoveries = await asyncio.gather(*tasks)

        # Categorize results
        for doi, discovery in zip(dois, discoveries):
            results[doi] = discovery

        # Summary
        accessible = [doi for doi, r in results.items() if r['status'] == 'accessible']
        needs_auth = [doi for doi, r in results.items() if r['status'] == 'needs_auth']
        no_access = [doi for doi, r in results.items() if r['status'] == 'no_access']

        print(f"\n📊 Discovery Results:")
        print(f"  ✅ Openly accessible: {len(accessible)}")
        print(f"  🔐 Needs authentication: {len(needs_auth)}")
        print(f"  ❌ No access found: {len(no_access)}")

        return results

    async def _check_single_doi(self, doi: str) -> Dict:
        """Check single DOI availability with ZenRows."""
        try:
            result = await self.zenrows_resolver._resolve_single_async(doi=doi)

            # Categorize based on ZenRows result
            if result.get('success'):
                return {
                    'status': 'accessible',
                    'url': result.get('final_url'),
                    'method': 'zenrows'
                }
            elif result.get('access_type') == 'zenrows_auth_required':
                return {
                    'status': 'needs_auth',
                    'reason': 'Requires institutional authentication'
                }
            else:
                return {
                    'status': 'no_access',
                    'reason': result.get('access_type', 'Unknown')
                }
        except Exception as e:
            return {
                'status': 'error',
                'reason': str(e)
            }

    async def download_authenticated_async(self, dois: List[str]) -> Dict[str, str]:
        """
        Phase 2: Use standard resolver for papers that need authentication.

        Benefits:
        - Uses your actual browser session
        - Maintains authentication context
        - Can access paywalled content
        """
        print("\n\n🔐 PHASE 2: Authenticated Downloads")
        print("="*50)

        # Ensure authenticated
        is_auth = await self.auth_manager.is_authenticated()
        if not is_auth:
            print("Authenticating with institution...")
            success = await self.auth_manager.authenticate()
            if not success:
                print("❌ Authentication failed!")
                return {}

        results = {}

        for doi in dois:
            print(f"\nDownloading: {doi}")
            try:
                result = await self.standard_resolver._resolve_single_async(doi=doi)
                if result and result.get('success'):
                    results[doi] = result.get('final_url')
                    print(f"  ✅ Success: {result.get('final_url')}")
                else:
                    print(f"  ❌ Failed: {result.get('access_type', 'Unknown')}")
            except Exception as e:
                print(f"  ❌ Error: {e}")

        return results

    def run_hybrid_workflow(self, dois: List[str]):
        """Run the complete hybrid workflow."""
        print("🚀 HYBRID RESOLVER WORKFLOW")
        print("="*70)
        print("Combining ZenRows (discovery) + Standard (authenticated access)")

        # Run async workflow
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            # Phase 1: Discovery
            discoveries = loop.run_until_complete(self.discover_access_async(dois))

            # Separate papers by access type
            needs_auth = [doi for doi, d in discoveries.items()
                         if d['status'] == 'needs_auth']

            # Phase 2: Authenticated download for paywalled papers
            if needs_auth:
                print(f"\n\n📥 {len(needs_auth)} papers need authenticated access")
                auth_results = loop.run_until_complete(
                    self.download_authenticated_async(needs_auth)
                )

            # Phase 3: Use Scholar for integrated download
            print("\n\n📚 PHASE 3: Integrated Download with Scholar")
            print("="*50)
            print("Scholar automatically uses the best method for each paper")

            download_results = self.scholar.download_pdfs(dois)

            # Summary
            print("\n\n📊 FINAL SUMMARY")
            print("="*50)
            for paper in download_results.papers:
                if hasattr(paper, 'pdf_path') and paper.pdf_path:
                    print(f"✅ {paper.doi or 'Unknown'}: Downloaded via {getattr(paper, 'pdf_source', 'Unknown')}")
                else:
                    print(f"❌ {paper.doi or 'Unknown'}: Failed")

        finally:
            loop.close()

def main():
    """Demonstrate the hybrid workflow."""

    # Example DOIs - mix of open access and paywalled
    test_dois = [
        # Likely paywalled
        "10.1038/nature12373",  # Nature
        "10.1016/j.cell.2020.05.032",  # Cell
        "10.1126/science.abg6155",  # Science

        # Might be open access
        "10.1371/journal.pone.0123456",  # PLOS ONE (usually OA)
        "10.1186/s12859-020-3456-3",  # BMC (usually OA)
    ]

    # Run workflow
    workflow = HybridResolverWorkflow()
    workflow.run_hybrid_workflow(test_dois)

    print("\n\n💡 BENEFITS OF HYBRID APPROACH:")
    print("="*50)
    print("1. ZenRows for discovery:")
    print("   - Fast parallel checking")
    print("   - Bypasses rate limits")
    print("   - Handles CAPTCHAs")
    print("\n2. Standard resolver for downloads:")
    print("   - Uses your real authentication")
    print("   - Access to paywalled content")
    print("   - Maintains session context")
    print("\n3. Scholar for integration:")
    print("   - Automatically chooses best method")
    print("   - Seamless workflow")
    print("   - Handles all edge cases")

if __name__ == "__main__":
    main()
