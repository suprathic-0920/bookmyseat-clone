import os
import re

file_path = os.path.join('templates', 'home.html')

with open(file_path, 'r', encoding='utf-8') as f:
    html = f.read()

# Fix Live Events cards
html = re.sub(
    r'(<div class="col-md-2 col-sm-4">\s*)<div class="card">',
    r'\1<a href="{% url \'movie_list\' %}" class="text-decoration-none text-dark">\n        <div class="card border-0 shadow-sm" style="transition: transform 0.3s;" onmouseover="this.style.transform=\'scale(1.05)\'" onmouseout="this.style.transform=\'scale(1)\'">',
    html
)
html = re.sub(
    r'(<h5 class="card-title">Event \d+</h5>\s*</div>\s*)</div>',
    r'\1</div>\n        </a>',
    html
)

# Fix Premiere cards
html = re.sub(
    r'(<div class="col-md-3 col-sm-6">\s*)<div class="card">',
    r'\1<a href="{% url \'movie_list\' %}" class="text-decoration-none text-dark">\n        <div class="card border-0 shadow-sm" style="transition: transform 0.3s;" onmouseover="this.style.transform=\'scale(1.05)\'" onmouseout="this.style.transform=\'scale(1)\'">',
    html
)
html = re.sub(
    r'(<h5 class="card-title">Premiere \d+</h5>\s*</div>\s*)</div>',
    r'\1</div>\n        </a>',
    html
)

# Also fix "Online Streaming Events" cards if any
html = re.sub(
    r'(<div class="col-md-3 col-sm-6 mt-4">\s*)<div class="card">',
    r'\1<a href="{% url \'movie_list\' %}" class="text-decoration-none text-dark">\n        <div class="card border-0 shadow-sm" style="transition: transform 0.3s;" onmouseover="this.style.transform=\'scale(1.05)\'" onmouseout="this.style.transform=\'scale(1)\'">',
    html
)
html = re.sub(
    r'(<h5 class="card-title">Streaming Event \d+</h5>\s*</div>\s*)</div>',
    r'\1</div>\n        </a>',
    html
)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(html)

print("Successfully fixed links and hover animations for all static cards!")
