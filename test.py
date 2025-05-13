import re

pattern = r"https://"

text = "https://example.com ty"

# Regex for image/link detection
url_pattern = re.compile(r'https?://\S+', re.IGNORECASE)

stripped = text.strip()
has_url = url_pattern.search(stripped)

print("group: " + has_url.group(0))

if has_url and stripped == has_url.group(0):
    print("Only Link")
elif has_url:
        print("Text and Link")

# if re.search(pattern, text):
#     print("Found https:// in the string.")
# else:
#     print("No https:// found.")
