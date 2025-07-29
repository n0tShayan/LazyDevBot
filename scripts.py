import requests
import google.generativeai as genai
import os
import time

# CONFIGURATION — replace with your actual tokens
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN") or "your_github_token_here"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or "your_gemini_api_key_here"

# Your GitHub repo: "owner/repo"
REPO_NAME = "owner/repository"

# ========== SETUP ==========

# GitHub API headers
headers = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json"
}

# Gemini API setup
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-pro")


# ========== FUNCTIONS ==========

def get_open_issues():
    url = f"https://api.github.com/repos/{REPO_NAME}/issues?state=open"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return [issue for issue in response.json() if "pull_request" not in issue]


def generate_solution(title, body):
    prompt = f"""
You are an expert open-source contributor.

Here is a GitHub issue:
Title: {title}
Description: {body}

Provide a concise, actionable solution in markdown. If not solvable directly, suggest the next steps for the maintainer.
"""
    response = model.generate_content(prompt)
    return response.text.strip()


def post_comment(issue_number, comment_body):
    url = f"https://api.github.com/repos/{REPO_NAME}/issues/{issue_number}/comments"
    payload = {"body": comment_body}
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    print(f"✅ Commented on issue #{issue_number}")


# ========== MAIN AGENT LOGIC ==========

def main():
    print(f"🔍 Fetching issues from {REPO_NAME}...")
    issues = get_open_issues()

    if not issues:
        print("🎉 No open issues found!")
        return

    for issue in issues:
        number = issue["number"]
        title = issue["title"]
        body = issue.get("body", "")
        print(f"\n🛠️ Resolving Issue #{number}: {title}")

        try:
            solution = generate_solution(title, body)
            post_comment(number, solution)
            time.sleep(2)  # Rate limit protection
        except Exception as e:
            print(f"❌ Failed on issue #{number}: {e}")

    print("\n✅ All done!")


if __name__ == "__main__":
    main()
