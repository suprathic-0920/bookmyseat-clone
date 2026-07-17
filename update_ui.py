import os
import re

views_path = os.path.join('users', 'views.py')
with open(views_path, 'r', encoding='utf-8') as f:
    views_content = f.read()

# Update home view
new_home_view = """def home(request):
    movies = Movie.objects.all()
    events = Event.objects.all()
    return render(request, 'home.html', {
        'movies': movies, 
        'events': events
    })"""
    
# Regex replace the home function
views_content = re.sub(r'def home\(request\):.*?return render\(.*?\)', new_home_view, views_content, flags=re.DOTALL)

with open(views_path, 'w', encoding='utf-8') as f:
    f.write(views_content)


home_html_path = os.path.join('templates', 'home.html')
with open(home_html_path, 'r', encoding='utf-8') as f:
    html = f.read()

# Rip out everything from "The Best of Live Events" to the endblock
start_marker = '<div class="section-title text-white mt-5 mb-4"'
end_marker = '{% endblock %}'

before = html.split(start_marker)[0]

new_ui = """
<div class="container-fluid mt-5 mb-5 py-4" style="background: linear-gradient(90deg, #1a1a2e 0%, #16213e 100%); border-radius: 10px;">
    <div class="d-flex align-items-center mb-4 px-3">
        <i class="fas fa-music text-info fa-2x mr-3"></i>
        <h2 class="text-white font-weight-bold m-0" style="font-size: 28px; letter-spacing: 0.5px;">Best of Live Events</h2>
    </div>
    
    <div class="row px-3">
        <!-- Comedy -->
        <div class="col-md-3 col-sm-6 mb-4">
            <a href="{% url 'event_category' 'Comedy' %}" class="text-decoration-none">
                <div class="card bg-transparent border-0 shadow-sm event-category-card" style="transition: transform 0.3s; border-radius: 15px; overflow: hidden;" onmouseover="this.style.transform='scale(1.03)'" onmouseout="this.style.transform='scale(1)'">
                    <img src="https://storage.googleapis.com/a1aa/image/wQXDIlqv4XoxGtNEO9XkSKBZYe9IuDePUWEcd0WwqcNzY5nTA.jpg" class="card-img-top" alt="Standup Comedy" style="height: 220px; object-fit: cover; border-top-left-radius: 15px; border-top-right-radius: 15px;" />
                    <div class="card-body text-white p-3" style="background-color: #22223b;">
                        <h5 class="card-title font-weight-bold mb-1">Standup Comedy</h5>
                        <small class="text-muted">Live Standup Acts</small>
                    </div>
                </div>
            </a>
        </div>
        
        <!-- Music -->
        <div class="col-md-3 col-sm-6 mb-4">
            <a href="{% url 'event_category' 'Music' %}" class="text-decoration-none">
                <div class="card bg-transparent border-0 shadow-sm event-category-card" style="transition: transform 0.3s; border-radius: 15px; overflow: hidden;" onmouseover="this.style.transform='scale(1.03)'" onmouseout="this.style.transform='scale(1)'">
                    <img src="https://storage.googleapis.com/a1aa/image/t52p8goZiO6QDBfid8wRyReanID18f5AxbszVhfPgESGklfcC.jpg" class="card-img-top" alt="Music Concerts" style="height: 220px; object-fit: cover; border-top-left-radius: 15px; border-top-right-radius: 15px;" />
                    <div class="card-body text-white p-3" style="background-color: #22223b;">
                        <h5 class="card-title font-weight-bold mb-1">Music Concerts</h5>
                        <small class="text-muted">Underground Rock & Pop</small>
                    </div>
                </div>
            </a>
        </div>
        
        <!-- Theatre -->
        <div class="col-md-3 col-sm-6 mb-4">
            <a href="{% url 'event_category' 'Workshop' %}" class="text-decoration-none">
                <div class="card bg-transparent border-0 shadow-sm event-category-card" style="transition: transform 0.3s; border-radius: 15px; overflow: hidden;" onmouseover="this.style.transform='scale(1.03)'" onmouseout="this.style.transform='scale(1)'">
                    <img src="https://storage.googleapis.com/a1aa/image/lAqCOht0TCaeSSLzw2ZGlPmDwvIEI3RtqajPoTYQN0ZOs8zJA.jpg" class="card-img-top" alt="Theatre Plays" style="height: 220px; object-fit: cover; border-top-left-radius: 15px; border-top-right-radius: 15px;" />
                    <div class="card-body text-white p-3" style="background-color: #22223b;">
                        <h5 class="card-title font-weight-bold mb-1">Theatre Plays</h5>
                        <small class="text-muted">Stage Plays & Dramas</small>
                    </div>
                </div>
            </a>
        </div>
        
        <!-- Sports -->
        <div class="col-md-3 col-sm-6 mb-4">
            <a href="{% url 'event_category' 'Sports' %}" class="text-decoration-none">
                <div class="card bg-transparent border-0 shadow-sm event-category-card" style="transition: transform 0.3s; border-radius: 15px; overflow: hidden;" onmouseover="this.style.transform='scale(1.03)'" onmouseout="this.style.transform='scale(1)'">
                    <img src="https://storage.googleapis.com/a1aa/image/EyIkuIxpLaLyHBDEuu5hezeydhw0mOSjKWX71bUiuTBiY5nTA.jpg" class="card-img-top" alt="Sports & Leagues" style="height: 220px; object-fit: cover; border-top-left-radius: 15px; border-top-right-radius: 15px;" />
                    <div class="card-body text-white p-3" style="background-color: #22223b;">
                        <h5 class="card-title font-weight-bold mb-1">Sports & Leagues</h5>
                        <small class="text-muted">Stadium screenings & tickets</small>
                    </div>
                </div>
            </a>
        </div>
    </div>
</div>

{% endblock %}
"""

new_html = before + new_ui
with open(home_html_path, 'w', encoding='utf-8') as f:
    f.write(new_html)

print("Updated home.html and views.py successfully!")
