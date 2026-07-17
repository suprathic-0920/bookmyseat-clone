import re
import os

path = os.path.join('templates', 'home.html')
with open(path, 'r', encoding='utf-8') as f:
    html = f.read()

# We will replace everything from Premiere section title down to </div>\n  </div>\n\n\n\n{% endblock %}
premiere_start = '<div class="section-title text-white mt-5 mb-4" style="border-bottom: 2px solid var(--accent-color); padding-bottom: 10px; font-size: 24px; font-weight: bold;">Premiere</div>'

# Split the HTML at premiere start
if premiere_start in html:
    before = html.split(premiere_start)[0]
    
    new_sections = f"""{premiere_start}
    <div class="row">
      {{% if premieres %}}
      {{% for event in premieres %}}
      <div class="col-md-3 col-sm-6 mb-4">
        <a href="{{% url 'event_detail' event.id %}}" class="text-decoration-none text-dark">
          <div class="card border-0 shadow-sm" style="transition: transform 0.3s;" onmouseover="this.style.transform='scale(1.05)'" onmouseout="this.style.transform='scale(1)'">
            {{% if event.image %}}
            <img src="{{{{ event.image.url }}}}" class="card-img-top rounded" alt="{{{{ event.name }}}}" height="300" style="object-fit: cover;" />
            {{% else %}}
            <div class="card-img-top d-flex justify-content-center align-items-center bg-secondary" style="height: 300px;">
                <i class="fas fa-film fa-4x text-light"></i>
            </div>
            {{% endif %}}
            <div class="card-body bg-dark text-white text-center p-2">
              <h5 class="card-title mb-0 text-truncate">{{{{ event.name }}}}</h5>
            </div>
          </div>
        </a>
      </div>
      {{% endfor %}}
      {{% else %}}
      <div class="col-12 text-center text-white my-4">
          <h5>No Premieres available at the moment!</h5>
      </div>
      {{% endif %}}
    </div>
    
    <div class="section-title text-white mt-5 mb-4" style="border-bottom: 2px solid var(--accent-color); padding-bottom: 10px; font-size: 24px; font-weight: bold;">Your Music Studio</div>
    <div class="row">
      {{% if music_studios %}}
      {{% for event in music_studios %}}
      <div class="col-md-2 col-sm-4 mb-4">
        <a href="{{% url 'event_detail' event.id %}}" class="text-decoration-none text-dark">
          <div class="card border-0 shadow-sm" style="transition: transform 0.3s;" onmouseover="this.style.transform='scale(1.05)'" onmouseout="this.style.transform='scale(1)'">
            {{% if event.image %}}
            <img src="{{{{ event.image.url }}}}" class="card-img-top rounded" alt="{{{{ event.name }}}}" height="200" style="object-fit: cover;" />
            {{% else %}}
            <div class="card-img-top d-flex justify-content-center align-items-center bg-secondary" style="height: 200px;">
                <i class="fas fa-headphones fa-3x text-light"></i>
            </div>
            {{% endif %}}
            <div class="card-body bg-dark text-white text-center p-2">
              <h6 class="card-title mb-0 text-truncate" style="font-size: 0.9rem;">{{{{ event.name }}}}</h6>
            </div>
          </div>
        </a>
      </div>
      {{% endfor %}}
      {{% else %}}
      <div class="col-12 text-center text-white my-4">
          <h5>No Studio Events available at the moment!</h5>
      </div>
      {{% endif %}}
    </div>
  </div>

{{% endblock %}}
"""
    
    new_html = before + new_sections
    with open(path, 'w', encoding='utf-8') as f:
        f.write(new_html)
    print("home.html completely updated for all categories!")
else:
    print("Could not find Premiere section.")
