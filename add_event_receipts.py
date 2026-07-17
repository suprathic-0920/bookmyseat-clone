import os

# users/views.py modifications
views_path = os.path.join('users', 'views.py')
with open(views_path, 'r', encoding='utf-8') as f:
    views_content = f.read()

old_profile_render = "return render(request, 'users/profile.html', {'u_form': u_form,'bookings':bookings})"
new_profile_render = "return render(request, 'users/profile.html', {'u_form': u_form,'bookings':bookings, 'event_bookings': event_bookings})"

views_content = views_content.replace(
    "bookings= Booking.objects.filter(user=request.user)",
    "bookings= Booking.objects.filter(user=request.user)\n    from movies.models import EventBooking\n    event_bookings = EventBooking.objects.filter(user=request.user, payment_status=True).order_by('-booking_time')"
)
views_content = views_content.replace(old_profile_render, new_profile_render)

with open(views_path, 'w', encoding='utf-8') as f:
    f.write(views_content)

# templates/users/profile.html modifications
profile_path = os.path.join('templates', 'users', 'profile.html')
with open(profile_path, 'r', encoding='utf-8') as f:
    html = f.read()

injection_marker = """            <div class="text-center py-5 rounded-4" style="background: rgba(255, 255, 255, 0.05); border: 1px dashed rgba(255,255,255,0.2);">
              <i class="fas fa-ticket-alt fa-4x text-muted mb-3 opacity-50"></i>
              <p class="lead mb-0 text-muted">No bookings yet. Time to plan your next movie night!</p>
            </div>
          {% endif %}
        </div>
      </div>"""

new_event_receipts = """
      <!-- Event Bookings Card -->
      <div class="mb-5 gsap-fade-up" style="animation-delay: 0.3s;">
        <h3 class="mb-4 text-white fw-bold d-flex align-items-center">
          <div style="width: 30px; height: 20px; background-color: #ff4b82; border-radius: 5px; margin-right: 15px; position: relative;">
            <div style="position: absolute; left: -10px; top: 0; bottom: 0; width: 5px; background-color: #00d2ff; border-radius: 5px;"></div>
          </div>
          Live Event Receipts
        </h3>
        
        <div class="booking-list">
          {% if event_bookings %}
            <div class="d-flex flex-column gap-4">
              {% for e_booking in event_bookings %}
                <div class="ticket-stub-wrapper d-flex w-100 shadow-lg">
                  
                  <!-- Left Side -->
                  <div class="ticket-left bg-white p-4 d-flex flex-column justify-content-between position-relative">
                    <div>
                      <div class="d-flex align-items-center mb-3">
                        <span class="badge text-white px-2 py-1 me-2" style="background-color: #00d2ff; font-size: 0.75rem; letter-spacing: 1px;">VIP PASS</span>
                        <span class="text-muted fw-bold" style="font-size: 0.8rem; letter-spacing: 1px;">{{ e_booking.event.category|upper }} EVENT</span>
                      </div>
                      
                      <h2 class="fw-bolder text-dark mb-1" style="font-size: 2rem;">{{ e_booking.event.name }}</h2>
                      <div class="text-muted d-flex align-items-center mb-4">
                        <i class="fas fa-map-marker-alt me-2"></i> {{ e_booking.event.venue }}
                      </div>
                    </div>
                    
                    <div class="ticket-info-box bg-light rounded-3 p-3 d-flex justify-content-between align-items-center">
                      <div>
                        <div class="text-muted mb-1" style="font-size: 0.7rem; font-weight: 600; letter-spacing: 1px;">DATE & TIME</div>
                        <div class="text-dark fw-bold">{{ e_booking.event.date_time }}</div>
                      </div>
                      <div class="text-end">
                        <div class="text-muted mb-1" style="font-size: 0.7rem; font-weight: 600; letter-spacing: 1px;">TICKETS</div>
                        <div class="fw-bold" style="color: #00d2ff; font-size: 1.25rem;">{{ e_booking.tickets_count }}</div>
                      </div>
                    </div>
                    
                    <!-- Top and bottom circles for the left piece -->
                    <div class="cutout cutout-top-left"></div>
                    <div class="cutout cutout-bottom-left"></div>
                  </div>
                  
                  <!-- Right Side -->
                  <div class="ticket-right bg-white p-4 d-flex flex-column align-items-center justify-content-center position-relative">
                    <img src="https://api.qrserver.com/v1/create-qr-code/?size=100x100&data=EVT-{{ e_booking.id }}-{{ request.user.username }}" alt="QR Code" class="mb-3 rounded border p-1" style="width: 90px; height: 90px;">
                    
                    <h3 class="fw-bolder text-dark mb-1">₹{{ e_booking.total_amount }}</h3>
                    <div class="text-muted mb-3" style="font-size: 0.7rem; font-family: monospace;">ID: EVT_{{ e_booking.id }}</div>
                    
                    <button class="btn btn-sm text-white fw-bold w-100" style="background-color: #00d2ff; border-radius: 20px;" disabled>
                      <i class="fas fa-check-circle me-1"></i> PAID
                    </button>
                    
                    <!-- Top and bottom circles for the right piece -->
                    <div class="cutout cutout-top-right"></div>
                    <div class="cutout cutout-bottom-right"></div>
                  </div>
                  
                </div>
              {% endfor %}
            </div>
          {% else %}
            <div class="text-center py-5 rounded-4" style="background: rgba(255, 255, 255, 0.05); border: 1px dashed rgba(255,255,255,0.2);">
              <i class="fas fa-calendar-times fa-4x text-muted mb-3 opacity-50"></i>
              <p class="lead mb-0 text-muted">No live event bookings yet. Catch a live show soon!</p>
            </div>
          {% endif %}
        </div>
      </div>
"""

if injection_marker in html:
    html = html.replace(injection_marker, injection_marker + "\n" + new_event_receipts)
    with open(profile_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print("Successfully added event receipts to profile!")
else:
    print("Could not find injection marker")
