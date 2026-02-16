"""
Professional GUI Interface
"""

import customtkinter as ctk
from tkinter import filedialog, messagebox
from pathlib import Path
import threading

class ForensicGUI:
    def __init__(self):
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")
        
        self.root = ctk.CTk()
        self.root.title("RICC FORENSIC v1.0")
        self.root.geometry("1600x1000")
        self.root.minsize(1400, 900)
        
        self.current_file = None
        self.current_data = None
        
        self._build_ui()
    
    def _build_ui(self):
        main = ctk.CTkFrame(self.root)
        main.pack(fill="both", expand=True, padx=15, pady=15)
        
        self._build_header(main)
        
        content = ctk.CTkFrame(main)
        content.pack(fill="both", expand=True, pady=15)
        
        self._build_left_panel(content)
        self._build_center_panel(content)
        self._build_right_panel(content)
        
        self.status = ctk.CTkLabel(main, text="Ready", anchor="w", font=ctk.CTkFont(size=12))
        self.status.pack(fill="x", pady=(10, 0))
    
    def _build_header(self, parent):
        header = ctk.CTkFrame(parent, height=100)
        header.pack(fill="x", pady=(0, 15))
        header.pack_propagate(False)
        
        title = ctk.CTkLabel(
            header,
            text="RICC FORENSIC",
            font=ctk.CTkFont(size=36, weight="bold")
        )
        title.pack(side="left", padx=30, pady=25)
        
        subtitle = ctk.CTkLabel(
            header,
            text="Face-to-Identity Intelligence Suite v1.0",
            font=ctk.CTkFont(size=14)
        )
        subtitle.pack(side="left", padx=10, pady=25)
    
    def _build_left_panel(self, parent):
        left = ctk.CTkFrame(parent, width=320)
        left.pack(side="left", fill="y", padx=(0, 15))
        left.pack_propagate(False)
        
        target = ctk.CTkFrame(left)
        target.pack(fill="x", padx=15, pady=15)
        
        ctk.CTkLabel(target, text="TARGET", font=ctk.CTkFont(weight="bold", size=14)).pack(pady=10)
        
        ctk.CTkButton(
            target,
            text="Select Image",
            command=self._select_image,
            height=45,
            font=ctk.CTkFont(size=13)
        ).pack(fill="x", padx=15, pady=10)
        
        self.file_label = ctk.CTkLabel(target, text="No file selected", font=ctk.CTkFont(size=12))
        self.file_label.pack(pady=5)
        
        ctrl = ctk.CTkFrame(left)
        ctrl.pack(fill="x", padx=15, pady=15)
        
        ctk.CTkLabel(ctrl, text="ANALYSIS", font=ctk.CTkFont(weight="bold", size=14)).pack(pady=10)
        
        self.btn_analyze = ctk.CTkButton(
            ctrl,
            text="Start Investigation",
            command=self._start_analysis,
            state="disabled",
            height=50,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#8B0000",
            hover_color="#660000"
        )
        self.btn_analyze.pack(fill="x", padx=15, pady=10)
        
        self.btn_compare = ctk.CTkButton(
            ctrl,
            text="Compare Faces",
            command=self._compare_faces,
            state="disabled",
            height=40,
            font=ctk.CTkFont(size=12)
        )
        self.btn_compare.pack(fill="x", padx=15, pady=5)
        
        opts = ctk.CTkFrame(left)
        opts.pack(fill="x", padx=15, pady=15)
        
        ctk.CTkLabel(opts, text="OPTIONS", font=ctk.CTkFont(weight="bold", size=14)).pack(pady=10)
        
        self.opt_enhance = ctk.CTkCheckBox(opts, text="Enhance image quality", font=ctk.CTkFont(size=12))
        self.opt_enhance.pack(padx=15, pady=5, anchor="w")
        
        self.opt_deepfake = ctk.CTkCheckBox(opts, text="Check manipulation", font=ctk.CTkFont(size=12))
        self.opt_deepfake.pack(padx=15, pady=5, anchor="w")
        
        self.opt_fast = ctk.CTkCheckBox(opts, text="Fast mode (no deep scrape)", font=ctk.CTkFont(size=12))
        self.opt_fast.pack(padx=15, pady=5, anchor="w")
        
        export = ctk.CTkFrame(left)
        export.pack(fill="x", padx=15, pady=15)
        
        ctk.CTkLabel(export, text="EXPORT", font=ctk.CTkFont(weight="bold", size=14)).pack(pady=10)
        
        self.btn_export = ctk.CTkButton(
            export,
            text="Save Report",
            command=self._export_report,
            state="disabled",
            height=40,
            font=ctk.CTkFont(size=12)
        )
        self.btn_export.pack(fill="x", padx=15, pady=10)
    
    def _build_center_panel(self, parent):
        center = ctk.CTkFrame(parent)
        center.pack(side="left", fill="both", expand=True, padx=(0, 15))
        
        preview_frame = ctk.CTkFrame(center, height=500)
        preview_frame.pack(fill="x", padx=15, pady=15)
        preview_frame.pack_propagate(False)
        
        self.preview_label = ctk.CTkLabel(
            preview_frame,
            text="No image loaded",
            font=ctk.CTkFont(size=16)
        )
        self.preview_label.pack(expand=True)
        
        log_frame = ctk.CTkFrame(center)
        log_frame.pack(fill="both", expand=True, padx=15, pady=15)
        
        ctk.CTkLabel(log_frame, text="ANALYSIS LOG", font=ctk.CTkFont(weight="bold", size=12)).pack(anchor="w", pady=5)
        
        self.log_text = ctk.CTkTextbox(log_frame, wrap="word", font=ctk.CTkFont(family="Courier", size=11))
        self.log_text.pack(fill="both", expand=True, padx=5, pady=5)
    
    def _build_right_panel(self, parent):
        right = ctk.CTkFrame(parent, width=450)
        right.pack(side="right", fill="y")
        right.pack_propagate(False)
        
        self.tabs = ctk.CTkTabview(right)
        self.tabs.pack(fill="both", expand=True, padx=15, pady=15)
        
        tab_summary = self.tabs.add("Summary")
        self.summary_text = ctk.CTkTextbox(tab_summary, wrap="word", font=ctk.CTkFont(size=12))
        self.summary_text.pack(fill="both", expand=True, padx=5, pady=5)
        
        tab_accts = self.tabs.add("Accounts")
        self.accts_text = ctk.CTkTextbox(tab_accts, wrap="word", font=ctk.CTkFont(size=12))
        self.accts_text.pack(fill="both", expand=True, padx=5, pady=5)
        
        tab_locs = self.tabs.add("Locations")
        self.locs_text = ctk.CTkTextbox(tab_locs, wrap="word", font=ctk.CTkFont(size=12))
        self.locs_text.pack(fill="both", expand=True, padx=5, pady=5)
        
        tab_contacts = self.tabs.add("Contacts")
        self.contacts_text = ctk.CTkTextbox(tab_contacts, wrap="word", font=ctk.CTkFont(size=12))
        self.contacts_text.pack(fill="both", expand=True, padx=5, pady=5)
        
        tab_tech = self.tabs.add("Technical")
        self.tech_text = ctk.CTkTextbox(tab_tech, wrap="word", font=ctk.CTkFont(size=11))
        self.tech_text.pack(fill="both", expand=True, padx=5, pady=5)
    
    def _select_image(self):
        path = filedialog.askopenfilename(
            filetypes=[("Images", "*.jpg *.jpeg *.png *.webp *.tiff *.bmp"), ("All", "*.*")]
        )
        if path:
            self.current_file = path
            self.file_label.configure(text=Path(path).name)
            self._load_preview(path)
            self.btn_analyze.configure(state="normal")
            self.btn_compare.configure(state="normal")
            self._log(f"Target loaded: {path}")
    
    def _load_preview(self, path):
        from PIL import Image
        
        img = Image.open(path)
        img.thumbnail((600, 600))
        
        ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=img.size)
        self.preview_label.configure(image=ctk_img, text="")
        self.preview_label.image = ctk_img
    
    def _log(self, msg):
        self.log_text.insert("end", f"{msg}\n")
        self.log_text.see("end")
    
    def _start_analysis(self):
        if not self.current_file:
            return
        
        self._log("Starting investigation...")
        threading.Thread(target=self._analysis_worker, daemon=True).start()
    
    def _analysis_worker(self):
        from ricc_forensic.core.face_engine import FaceEngine
        from ricc_forensic.core.reverse_search import ReverseSearch
        from ricc_forensic.core.socmed_scraper import SocmedScraper
        from ricc_forensic.core.geolocation import GeoAnalyzer
        from ricc_forensic.core.contact_extractor import ContactExtractor
        from ricc_forensic.core.report_generator import ReportGenerator
        
        try:
            self._update_status("Processing face...")
            self._log("Extracting face signature...")
            
            face_engine = FaceEngine()
            face_data = face_engine.process(self.current_file)
            
            if not face_data.get("success"):
                self._log(f"Error: {face_data.get('error')}")
                self._update_status("Analysis failed")
                return
            
            self._log(f"Face hash: {face_data['hash']}")
            self._log(f"Confidence: {face_data['confidence']:.2%}")
            
            if self.opt_enhance.get():
                self._log("Enhancing image quality...")
                from ricc_forensic.core.enhancement import FaceEnhancer
                import cv2
                
                enhancer = FaceEnhancer()
                enhanced = enhancer.enhance(face_data["crop"])
                enhanced_path = f"temp/enhanced_{face_data['hash']}.jpg"
                cv2.imwrite(enhanced_path, enhanced)
                face_data = face_engine.process(enhanced_path)
                self._log("Enhancement complete")
            
            if self.opt_deepfake.get():
                self._log("Checking for manipulation...")
                from ricc_forensic.core.deepfake_detect import DeepfakeDetector
                
                detector = DeepfakeDetector()
                check = detector.analyze(self.current_file)
                self._log(f"Manipulation score: {check['manipulation_score']:.2%}")
                self._log(f"Verdict: {check['verdict']}")
            
            self._update_status("Searching image...")
            self._log("Initiating reverse image search...")
            
            search = ReverseSearch()
            results = search.search(self.current_file, ["yandex", "google", "bing"])
            
            total = sum(len(v) for v in results.values())
            self._log(f"Found {total} potential matches")
            
            all_urls = []
            for engine, urls in results.items():
                all_urls.extend(urls)
            
            social_urls = search.filter_social(all_urls)
            self._log(f"Social media links: {len(social_urls)}")
            
            scraper = SocmedScraper()
            accounts = []
            
            for url_data in social_urls[:15]:
                extracted = scraper.extract_from_url(url_data["url"])
                if extracted and extracted not in accounts:
                    accounts.append(extracted)
                    self._log(f"Found: {extracted['platform']} - @{extracted['username']}")
            
            detailed = []
            if not self.opt_fast.get():
                self._update_status("Scraping profiles...")
                for acc in accounts[:5]:
                    self._log(f"Scraping {acc['platform']}/@{acc['username']}...")
                    data = scraper.scrape(acc["platform"], acc["username"])
                    if data.get("success"):
                        extractor = ContactExtractor()
                        contacts = extractor.from_profile(data)
                        data["contacts"] = contacts
                        detailed.append(data)
                    import time
                    time.sleep(1.5)
            
            self._update_status("Analyzing locations...")
            all_posts = []
            for d in detailed:
                all_posts.extend(d.get("recent_posts", []))
            
            geo = GeoAnalyzer()
            locations = geo.analyze(all_posts)
            self._log(f"Unique locations: {len(locations)}")
            
            self.current_data = {
                "face_hash": face_data["hash"],
                "confidence_score": self._calc_confidence(len(detailed), len(locations)),
                "summary": {
                    "total_accounts": len(detailed),
                    "total_locations": len(locations),
                    "total_contacts": sum(len(d.get("contacts", {}).get("emails", [])) for d in detailed)
                },
                "accounts": detailed,
                "locations": locations,
                "contacts": extractor.cross_reference(detailed) if detailed else {"emails": [], "phones": []},
                "timeline": geo.timeline(locations)
            }
            
            self._display_results(self.current_data)
            self.btn_export.configure(state="normal")
            self._update_status("Investigation complete")
            self._log("Analysis finished successfully")
            
        except Exception as e:
            self._log(f"Error: {str(e)}")
            self._update_status("Error occurred")
    
    def _calc_confidence(self, accounts: int, locations: int) -> float:
        score = min(accounts * 15, 45) + min(locations * 10, 30) + 25
        return min(score, 100)
    
    def _display_results(self, data):
        self.summary_text.delete("1.0", "end")
        self.summary_text.insert("1.0", f"Target Hash: {data['face_hash']}\n")
        self.summary_text.insert("end", f"Confidence: {data['confidence_score']:.1f}%\n")
        self.summary_text.insert("end", f"Accounts: {data['summary']['total_accounts']}\n")
        self.summary_text.insert("end", f"Locations: {data['summary']['total_locations']}\n")
        
        self.accts_text.delete("1.0", "end")
        for acc in data["accounts"]:
            self.accts_text.insert("end", f"[{acc.get('platform')}]\n")
            self.accts_text.insert("end", f"  @{acc.get('username')}\n")
            self.accts_text.insert("end", f"  Name: {acc.get('full_name', 'N/A')}\n")
            self.accts_text.insert("end", f"  Bio: {acc.get('biography', 'N/A')[:80]}\n\n")
        
        self.locs_text.delete("1.0", "end")
        for loc in data["locations"][:10]:
            self.locs_text.insert("end", f"{loc['name']}\n")
            self.locs_text.insert("end", f"  Frequency: {loc['frequency']}\n")
            if loc.get('coordinates'):
                self.locs_text.insert("end", f"  Coords: {loc['coordinates']['lat']:.4f}, {loc['coordinates']['lon']:.4f}\n")
            self.locs_text.insert("end", "\n")
        
        self.contacts_text.delete("1.0", "end")
        contacts = data["contacts"]
        if contacts.get("emails"):
            self.contacts_text.insert("end", f"Emails: {', '.join(contacts['emails'])}\n")
        if contacts.get("phones"):
            self.contacts_text.insert("end", f"Phones: {', '.join(contacts['phones'])}\n")
        
        self.tech_text.delete("1.0", "end")
        import json
        self.tech_text.insert("1.0", json.dumps(data, indent=2, default=str)[:5000])
    
    def _compare_faces(self):
        if not self.current_file:
            return
        
        ref = filedialog.askopenfilename(
            title="Select reference image",
            filetypes=[("Images", "*.jpg *.jpeg *.png")]
        )
        
        if ref:
            from ricc_forensic.core.face_engine import FaceEngine
            engine = FaceEngine()
            result = engine.compare(self.current_file, ref)
            
            msg = f"Result: {result.get('verdict')}\nSimilarity: {result.get('similarity', 0):.4f}\nConfidence: {result.get('confidence', 0):.2f}%"
            messagebox.showinfo("Face Comparison", msg)
    
    def _export_report(self):
        if not self.current_data:
            return
        
        from ricc_forensic.core.report_generator import ReportGenerator
        
        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text", "*.txt"), ("JSON", "*.json"), ("HTML", "*.html")]
        )
        
        if path:
            fmt = "json" if path.endswith(".json") else "html" if path.endswith(".html") else "text"
            gen = ReportGenerator()
            report = gen.generate(self.current_data, fmt)
            gen.save(report, path)
            self._log(f"Report saved: {path}")
    
    def _update_status(self, msg):
        self.root.after(0, lambda: self.status.configure(text=f"Status: {msg}"))
    
    def run(self):
        self.root.mainloop()

def launch():
    app = ForensicGUI()
    app.run()
