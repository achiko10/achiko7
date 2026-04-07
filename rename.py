import os

workspace = r"c:\Users\Utente\.gemini\antigravity\scratch\zenith"

def replace_in_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        new_content = content.replace("Zenith", "Zenith")\
                             .replace("zenith", "zenith")\
                             .replace("ზენითი", "ზენითი")

        if new_content != content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"Updated {filepath}")
    except Exception as e:
        print(f"Error processing {filepath}: {e}")

extensions = ('.py', '.html', '.md', '.po', '.txt')

for root, dirs, files in os.walk(workspace):
    if '.venv' in root or '.git' in root or '__pycache__' in root or 'node_modules' in root:
        continue
    for file in files:
        if file.endswith(extensions):
            replace_in_file(os.path.join(root, file))

print("Text replacement completed.")
