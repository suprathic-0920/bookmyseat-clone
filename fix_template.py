import os
path = r"c:\Users\supra\Downloads\djnago-bookmyshow-clone\templates\home.html"
with open(path, 'r', encoding='utf-8') as f:
    text = f.read()

# Remove the accidental backslash inside the Django url tag
text = text.replace(r"\'movie_list\'", "'movie_list'")

with open(path, 'w', encoding='utf-8') as f:
    f.write(text)
print("Template fixed!")
