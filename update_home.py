import re
import os

path = os.path.join('templates', 'home.html')

with open(path, 'r', encoding='utf-8') as f:
    html = f.read()

live_events_header = '<div class="section-title text-white mt-5 mb-4" style="border-bottom: 2px solid var(--accent-color); padding-bottom: 10px; font-size: 24px; font-weight: bold;">The Best of Live Events</div>'
premiere_header = '<div class="section-title text-white mt-5 mb-4" style="border-bottom: 2px solid var(--accent-color); padding-bottom: 10px; font-size: 24px; font-weight: bold;">Premiere</div>'

# Extract everything before Live Events and everything from Premiere onwards
if live_events_header in html and premiere_header in html:
    before = html.split(live_events_header)[0]
    after = premiere_header + html.split(premiere_header)[1]
    
    new_events_section = f"""{live_events_header}
    <div class="row">
      {{% if events %}}
      {{% for event in events %}}
      <div class="col-md-2 col-sm-4 mb-4">
        <a href="{{% url 'event_detail' event.id %}}" class="text-decoration-none text-dark">
          <div class="card border-0 shadow-sm" style="transition: transform 0.3s;" onmouseover="this.style.transform='scale(1.05)'" onmouseout="this.style.transform='scale(1)'">
            {{% if event.image %}}
            <img src="{{{{ event.image.url }}}}" class="card-img-top rounded" alt="{{{{ event.name }}}}" height="200" style="object-fit: cover;" />
            {{% else %}}
            <div class="card-img-top d-flex justify-content-center align-items-center bg-secondary" style="height: 200px;">
                <i class="fas fa-calendar-alt fa-3x text-light"></i>
            </div>
            {{% endif %}}
            <div class="card-body bg-dark text-white text-center p-2">
              <h6 class="card-title mb-0 text-truncate" style="font-size: 0.9rem;">{{{{ event.name }}}}</h6>
              <small class="text-muted">{{{{ event.category }}}}</small>
            </div>
          </div>
        </a>
      </div>
      {{% endfor %}}
      {{% else %}}
      <div class="col-12 text-center text-white my-4">
          <h5>No events available at the moment!</h5>
      </div>
      {{% endif %}}
    </div>
    
    """
    
    new_html = before + new_events_section + after
    
    with open(path, 'w', encoding='utf-8') as f:
        f.write(new_html)
    print("home.html successfully updated!")
else:
    print("Could not find headers to replace.")
