import json
import os
import shutil
import time

from google import genai
from google.genai import types


API_KEY = os.getenv("GEMINI_API_KEY")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

SKIP_FILES = {
    "1.Python",
    "2.html",
    "3.another",
    os.path.basename(__file__),
    "ai_sort.py",
    "sort_projects.py",
    "struct.pyc",
    "__pycache__",
    ".git",
    ".vscode",
}


def build_manifest():
    manifest = []

    for item in os.listdir(BASE_DIR):
        if item in SKIP_FILES or item.startswith("."):
            continue

        full_path = os.path.join(BASE_DIR, item)

        if os.path.isfile(full_path):
            snippet = ""
            extension = os.path.splitext(item)[1].lower()

            if extension in {
                ".py",
                ".html",
                ".js",
                ".css",
                ".json",
                ".txt",
                ".md",
                ".env",
            }:
                try:
                    with open(
                        full_path,
                        "r",
                        encoding="utf-8",
                        errors="ignore",
                    ) as file:
                        snippet = "".join(file.readline() for _ in range(5))
                except OSError:
                    pass

            manifest.append(
                {
                    "file": item,
                    "snippet": snippet[:200],
                }
            )

        elif os.path.isdir(full_path):
            manifest.append({"folder": item})

    return manifest


def get_ai_plan(manifest):
    if not API_KEY:
        raise RuntimeError(
            "GEMINI_API_KEY environment variable is not set."
        )

    client = genai.Client(api_key=API_KEY.strip())

    prompt = f"""
You are a system architect. Organize the files into logical projects.

List of files:
{json.dumps(manifest, ensure_ascii=False, indent=2)}

Rules:
1. Combine related files into one project. For example:
   telegram_bot.py, config.py, and database.db should be grouped together.
2. Use "project_folder_name" for the name of each related project.
3. Use only these categories:
   "1.Python/needs improvement",
   "2.html/needs improvement",
   "3.another".
4. Return ONLY a valid JSON array without Markdown or additional text.

Example:
[
  {{
    "project_folder_name": "ProjectName",
    "target_category": "1.Python/needs improvement",
    "files": ["main.py", "db.py"]
  }},
  {{
    "project_folder_name": "",
    "target_category": "3.another",
    "files": ["photo.jpg"]
  }}
]
"""

    models_to_try = [
        "gemini-2.5-flash",
        "gemini-1.5-flash",
    ]

    for model_name in models_to_try:
        for attempt in range(3):
            try:
                print(
                    f"Sending request to {model_name} "
                    f"(attempt {attempt + 1})..."
                )

                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                    ),
                )

                return json.loads(response.text)

            except Exception as error:
                error_message = str(error)

                if "503" in error_message or "UNAVAILABLE" in error_message:
                    print(
                        f"Server {model_name} is unavailable. "
                        "Retrying in 3 seconds..."
                    )
                    time.sleep(3)
                else:
                    print(f"Request failed: {error_message}")
                    break

    raise RuntimeError(
        "Could not get a response from any of the Gemini models."
    )


def execute_plan(plan):
    for group in plan:
        target_category = group.get(
            "target_category",
            "3.another",
        )
        project_folder = group.get(
            "project_folder_name",
            "",
        ).strip()
        files = group.get("files", [])

        if project_folder:
            destination_directory = os.path.join(
                BASE_DIR,
                target_category,
                project_folder,
            )
        else:
            destination_directory = os.path.join(
                BASE_DIR,
                target_category,
            )

        os.makedirs(destination_directory, exist_ok=True)

        for filename in files:
            source_path = os.path.join(BASE_DIR, filename)

            if not os.path.isfile(source_path):
                continue

            destination_path = os.path.join(
                destination_directory,
                os.path.basename(filename),
            )

            try:
                shutil.move(source_path, destination_path)
                print(
                    f"[+] {filename} -> "
                    f"{os.path.relpath(destination_path, BASE_DIR)}"
                )
            except OSError as error:
                print(f"[!] Error moving {filename}: {error}")


if __name__ == "__main__":
    print("Removing cache...")

    cache_path = os.path.join(BASE_DIR, "struct.pyc")
    if os.path.exists(cache_path):
        os.remove(cache_path)

    print("Scanning the folder...")
    manifest = build_manifest()

    if manifest:
        print(f"Submitting {len(manifest)} items to Gemini...")

        try:
            plan = get_ai_plan(manifest)
            print("\nOrganizing files into projects...")
            execute_plan(plan)
            print("\nAll done!")
        except Exception as error:
            print(f"[!] Error: {error}")
    else:
        print("No files found to organize.")