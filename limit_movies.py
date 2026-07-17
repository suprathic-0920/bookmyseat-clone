import os

home_html_path = os.path.join('templates', 'home.html')
with open(home_html_path, 'r', encoding='utf-8') as f:
    html = f.read()

# We need to find the Recommended Movies section and replace it.
# The section starts with '<div class="section-title text-white mt-5 mb-4" style="border-bottom: 2px solid var(--accent-color); padding-bottom: 10px; font-size: 24px; font-weight: bold;">Recommended Movies</div>'

old_header = '<div class="section-title text-white mt-5 mb-4" style="border-bottom: 2px solid var(--accent-color); padding-bottom: 10px; font-size: 24px; font-weight: bold;">Recommended Movies</div>'
new_header = """
    <div class="d-flex justify-content-between align-items-center mt-5 mb-4" style="border-bottom: 2px solid var(--accent-color); padding-bottom: 10px;">
        <div class="section-title text-white m-0" style="font-size: 24px; font-weight: bold;">Recommended Movies</div>
        <a href="{% url 'movie_list' %}" class="text-danger text-decoration-none font-weight-bold" style="font-size: 14px;">See All Movies <i class="fas fa-chevron-right"></i></a>
    </div>
"""

# Replace the loop to limit to 10
old_loop = '{% for movie in movies %}'
new_loop = '{% for movie in movies|slice:":10" %}'

if old_header in html:
    html = html.replace(old_header, new_header)
    html = html.replace(old_loop, new_loop)
    
    with open(home_html_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print("Movies section limited to 10 and 'See All' button added!")
else:
    print("Could not find Recommended Movies header.")
