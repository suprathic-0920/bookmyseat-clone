import os

home_html_path = os.path.join('templates', 'home.html')
with open(home_html_path, 'r', encoding='utf-8') as f:
    html = f.read()

# The movies section to restore
movies_section = """
    <div class="section-title text-white mt-5 mb-4" style="border-bottom: 2px solid var(--accent-color); padding-bottom: 10px; font-size: 24px; font-weight: bold;">Recommended Movies</div>
    <div class="row px-3">
      {% if movies %}
      {% for movie in movies %}
      <div class="col-md-2 col-sm-4 mb-4">
        <a href="{% url 'theater_list' movie.id %}" class="text-decoration-none text-dark">
          <div class="card border-0 shadow-sm" style="transition: transform 0.3s;" onmouseover="this.style.transform='scale(1.05)'" onmouseout="this.style.transform='scale(1)'">
            {% if movie.image %}
            <img src="{{ movie.image.url }}" class="card-img-top rounded" alt="{{ movie.name }}" height="260" style="object-fit: cover;" />
            {% else %}
            <div class="card-img-top d-flex justify-content-center align-items-center bg-secondary rounded" style="height: 260px;">
                <i class="fas fa-film fa-3x text-light"></i>
            </div>
            {% endif %}
            <div class="card-body bg-dark text-white text-center p-2 rounded-bottom">
              <h6 class="card-title mb-1 text-truncate" style="font-size: 0.9rem;">{{ movie.name }}</h6>
              <small class="text-muted"><i class="fas fa-star text-danger"></i> {{ movie.rating|default:"8.0" }}/10</small>
            </div>
          </div>
        </a>
      </div>
      {% endfor %}
      {% else %}
      <div class="col-12 text-center text-white my-4">
          <h5>No movies available right now!</h5>
      </div>
      {% endif %}
    </div>
"""

# Find where to insert it: right before Best of Live Events
insert_marker = '<div class="container-fluid mt-5 mb-5 py-4"'

if insert_marker in html and "Recommended Movies" not in html:
    parts = html.split(insert_marker)
    new_html = parts[0] + movies_section + "\n" + insert_marker + parts[1]
    
    with open(home_html_path, 'w', encoding='utf-8') as f:
        f.write(new_html)
    print("Movies section successfully restored!")
else:
    print("Could not insert or movies section already exists.")
