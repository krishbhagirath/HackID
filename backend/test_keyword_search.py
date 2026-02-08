import os
from github import Github
from dotenv import load_dotenv
from pathlib import Path

# Load environment
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

def test_search():
    token = os.getenv('GITHUB_TOKEN')
    if not token or token == "your-github-token-here-optional":
        print("⚠️  Warning: GITHUB_TOKEN not set. Using public rate limit (60 req/hr).")
        g = Github()
    else:
        g = Github(token)

    repo_name = "krishbhagirath/cradlewatch"
    keywords = ["html", "css", "javascript", "flask", "mediapipe", "opencv"]

    print(f"🔍 GitHub Keyword Search Tool")
    print(f"Target Repo: {repo_name}")
    print("=" * 40)

    try:
        repo = g.get_repo(repo_name)
        print(f"📦 Repository: {repo_name}")
        
        # WORKAROUND: Get the entire file tree (this bypasses search indexing)
        print("\n🌳 Fetching recursive file tree (Workaround for indexing issues)...")
        branch = repo.default_branch
        tree = repo.get_git_tree(branch, recursive=True)
        all_files = [item.path for item in tree.tree if item.type == 'blob']
        print(f"   ✓ Found {len(all_files)} total files in repo")

        results_map = {kw: [] for kw in keywords}

        # 1. Prioritize files (Configs and Manifests first)
        priority_files = [f for f in all_files if f.lower() in ('requirements.txt', 'package.json', 'go.mod', 'pom.xml', 'app.py', 'main.py')]
        other_code = [f for f in all_files if f.endswith(('.py', '.js', '.html', '.css')) and f not in priority_files]
        
        search_queue = priority_files + other_code
        print(f"   🔍 Organized search queue: {len(priority_files)} priority files, {len(other_code)} code files.")

        # 2. Iterate and check contents (with Early Exit)
        remaining_kws = set(keywords)
        
        for file_path in search_queue:
            if not remaining_kws:
                print("\n✨ All keywords found! Skipping remaining files.")
                break
            
            try:
                print(f"   📡 Peeking into: {file_path} (Remaining: {len(remaining_kws)})")
                file_content = repo.get_contents(file_path).decoded_content.decode('utf-8').lower()
                
                found_this_round = []
                for kw in list(remaining_kws):
                    search_terms = [kw]
                    if kw == "opencv": search_terms.append("cv2")
                    
                    if any(term in file_content for term in search_terms):
                        results_map[kw].append(file_path)
                        found_this_round.append(kw)
                        remaining_kws.remove(kw) # Early exit for this specific keyword
                
                if found_this_round:
                    print(f"      📍 Found keywords: {found_this_round}")
                
            except Exception:
                continue

        print("\n" + "="*40)
        print("📊 FINAL WORKAROUND RESULTS")
        print("="*40)
        for kw, files in results_map.items():
            status = "✅ FOUND" if files else "❌ NOT FOUND"
            print(f"{kw.ljust(12)} : {status} (in {len(files)} files)")
            if files:
                print(f"               First seen in: {files[0]}")
                
    except Exception as e:
        print(f"CRITICAL ERROR: {e}")

if __name__ == "__main__":
    test_search()
