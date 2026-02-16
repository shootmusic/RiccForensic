#!/usr/bin/env python3
"""
RICC FORENSIC v1.0 - CLI Interface
"""

import argparse
import sys
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(
        description="RICC FORENSIC - Face-to-Identity Intelligence Suite",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  forensic.py target.jpg                    # Full investigation
  forensic.py target.jpg -o report.txt      # Save report
  forensic.py target.jpg --enhance        # Enhance before analysis
  forensic.py target.jpg --check-fake     # Verify authenticity
  forensic.py target.jpg --compare ref.jpg  # Face comparison
        """
    )
    
    parser.add_argument("image", help="Target image path")
    parser.add_argument("-o", "--output", default="report.txt", help="Output file")
    parser.add_argument("-f", "--format", choices=["text", "json", "html"], default="text", help="Report format")
    parser.add_argument("--enhance", action="store_true", help="Enhance image quality")
    parser.add_argument("--check-fake", action="store_true", help="Check for manipulation")
    parser.add_argument("--fast", action="store_true", help="Skip deep scraping")
    parser.add_argument("--compare", help="Compare with reference image")
    parser.add_argument("--engines", nargs="+", default=["yandex", "google", "bing"], help="Search engines")
    
    args = parser.parse_args()
    
    if not Path(args.image).exists():
        print(f"Error: File not found: {args.image}")
        sys.exit(1)
    
    with open("banner.txt", "r") as f:
        print(f.read())
    
    from ricc_forensic.core.face_engine import FaceEngine
    from ricc_forensic.core.reverse_search import ReverseSearch
    from ricc_forensic.core.socmed_scraper import SocmedScraper
    from ricc_forensic.core.geolocation import GeoAnalyzer
    from ricc_forensic.core.contact_extractor import ContactExtractor
    from ricc_forensic.core.report_generator import ReportGenerator
    
    face_engine = FaceEngine()
    
    if args.compare:
        print(f"\n[MODE] Face Comparison")
        result = face_engine.compare(args.image, args.compare)
        print(f"\nResult: {result.get('verdict')}")
        print(f"Similarity: {result.get('similarity', 0):.4f}")
        print(f"Confidence: {result.get('confidence', 0):.2f}%")
        sys.exit(0)
    
    print(f"\n[1] Processing target face...")
    face_data = face_engine.process(args.image)
    
    if not face_data.get("success"):
        print(f"Error: {face_data.get('error')}")
        sys.exit(1)
    
    print(f"Face hash: {face_data['hash']}")
    print(f"Confidence: {face_data['confidence']:.2%}")
    
    if args.enhance:
        print("\n[ENHANCE] Improving image quality...")
        from ricc_forensic.core.enhancement import FaceEnhancer
        import cv2
        
        enhancer = FaceEnhancer()
        enhanced = enhancer.enhance(face_data["crop"])
        enhanced_path = f"temp/enhanced_{face_data['hash']}.jpg"
        cv2.imwrite(enhanced_path, enhanced)
        face_data = face_engine.process(enhanced_path)
        print("Enhancement complete")
    
    if args.check_fake:
        print("\n[FORENSIC] Checking authenticity...")
        from ricc_forensic.core.deepfake_detect import DeepfakeDetector
        
        detector = DeepfakeDetector()
        check = detector.analyze(args.image)
        print(f"Manipulation score: {check['manipulation_score']:.2%}")
        print(f"Verdict: {check['verdict']}")
    
    print(f"\n[2] Reverse image search...")
    search = ReverseSearch()
    results = search.search(args.image, args.engines)
    
    all_urls = []
    for engine, urls in results.items():
        print(f"  {engine}: {len(urls)} results")
        all_urls.extend(urls)
    
    social_urls = search.filter_social(all_urls)
    print(f"\n[3] Found {len(social_urls)} social media links")
    
    scraper = SocmedScraper()
    accounts = []
    
    for url_data in social_urls[:15]:
        extracted = scraper.extract_from_url(url_data["url"])
        if extracted and extracted not in accounts:
            accounts.append(extracted)
            print(f"  {extracted['platform']}: @{extracted['username']}")
    
    detailed = []
    if not args.fast:
        print(f"\n[4] Scraping {len(accounts)} profiles...")
        for acc in accounts[:5]:
            print(f"  Scraping {acc['platform']}/@{acc['username']}...")
            data = scraper.scrape(acc["platform"], acc["username"])
            if data.get("success"):
                extractor = ContactExtractor()
                data["contacts"] = extractor.from_profile(data)
                detailed.append(data)
            import time
            time.sleep(1.5)
    
    print(f"\n[5] Analyzing locations...")
    all_posts = []
    for d in detailed:
        all_posts.extend(d.get("recent_posts", []))
    
    geo = GeoAnalyzer()
    locations = geo.analyze(all_posts)
    print(f"Found {len(locations)} unique locations")
    
    tracking_data = {
        "face_hash": face_data["hash"],
        "confidence_score": min(len(detailed) * 15 + len(locations) * 10 + 25, 100),
        "summary": {
            "total_accounts": len(detailed),
            "total_locations": len(locations),
            "total_contacts": sum(len(d.get("contacts", {}).get("emails", [])) for d in detailed)
        },
        "accounts": detailed,
        "locations": locations,
        "contacts": ContactExtractor().cross_reference(detailed) if detailed else {"emails": [], "phones": []},
        "timeline": geo.timeline(locations)
    }
    
    print(f"\n[6] Generating {args.format} report...")
    gen = ReportGenerator()
    report = gen.generate(tracking_data, args.format)
    gen.save(report, args.output)
    
    print(f"\nReport saved: {args.output}")
    print(f"\nInvestigation Summary:")
    print(f"  Confidence: {tracking_data['confidence_score']:.1f}%")
    print(f"  Accounts: {tracking_data['summary']['total_accounts']}")
    print(f"  Locations: {tracking_data['summary']['total_locations']}")

if __name__ == "__main__":
    main()
