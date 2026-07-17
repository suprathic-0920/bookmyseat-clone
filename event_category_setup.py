import os
import re

# 1. Update movies/urls.py
urls_path = os.path.join('movies', 'urls.py')
with open(urls_path, 'r', encoding='utf-8') as f:
    urls_content = f.read()

new_url = "    path('events/category/<str:category>/', views.event_category, name='event_category'),\n]"
urls_content = urls_content.replace(']', new_url)

with open(urls_path, 'w', encoding='utf-8') as f:
    f.write(urls_content)

# 2. Update movies/views.py
views_path = os.path.join('movies', 'views.py')
with open(views_path, 'a', encoding='utf-8') as f:
    f.write("""

def event_category(request, category):
    # Mapping for Workshop -> Theatre Plays
    if category == 'Workshop':
        events = Event.objects.filter(category__in=['Workshop', 'Theatre'])
    else:
        events = Event.objects.filter(category__iexact=category)
    return render(request, 'movies/event_list.html', {'events': events, 'category': category})
""")

# 3. Create event_list.html
template_path = os.path.join('templates', 'movies', 'event_list.html')
html_content = """{% extends 'base.html' %}
{% block content %}
<div class="container mt-5 text-white">
    <h2 class="mb-4 text-warning border-bottom pb-2">{{ category }} Events</h2>
    
    <div class="row">
        {% if events %}
        {% for event in events %}
        <div class="col-md-3 col-sm-6 mb-4">
            <a href="{% url 'event_detail' event.id %}" class="text-decoration-none">
                <div class="card bg-dark text-white border-0 shadow-sm" style="transition: transform 0.3s;" onmouseover="this.style.transform='scale(1.05)'" onmouseout="this.style.transform='scale(1)'">
                    {% if event.image %}
                    <img src="{{ event.image.url }}" class="card-img-top rounded" alt="{{ event.name }}" height="200" style="object-fit: cover;">
                    {% else %}
                    <div class="card-img-top d-flex justify-content-center align-items-center bg-secondary rounded" style="height: 200px;">
                        <i class="fas fa-ticket-alt fa-3x text-light"></i>
                    </div>
                    {% endif %}
                    <div class="card-body p-3">
                        <h5 class="card-title font-weight-bold">{{ event.name }}</h5>
                        <p class="card-text text-muted small"><i class="fas fa-map-marker-alt"></i> {{ event.venue }}</p>
                        <p class="text-success font-weight-bold mb-0">${{ event.ticket_price }}</p>
                    </div>
                </div>
            </a>
        </div>
        {% endfor %}
        {% else %}
        <div class="col-12 text-center mt-5">
            <i class="far fa-frown fa-4x text-muted mb-3"></i>
            <h4>No {{ category }} events are currently scheduled!</h4>
            <p class="text-muted">Check back later for exciting new shows.</p>
        </div>
        {% endif %}
    </div>
</div>
{% endblock %}
"""

with open(template_path, 'w', encoding='utf-8') as f:
    f.write(html_content)

print("Event category routing and template setup complete!")
