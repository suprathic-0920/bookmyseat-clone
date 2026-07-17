import os
import re

# 1. Update views.py
views_path = os.path.join('movies', 'views.py')
with open(views_path, 'r', encoding='utf-8') as f:
    views_content = f.read()

if "def download_event_ticket_pdf(" not in views_content:
    new_view = """
@login_required(login_url='/login/')
def download_event_ticket_pdf(request, booking_id):
    booking = get_object_or_404(EventBooking, id=booking_id, user=request.user)
    template_path = 'users/event_ticket_pdf.html'
    context = {'booking': booking}
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="event_ticket_{booking.id}.pdf"'
    template = get_template(template_path)
    html = template.render(context)
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response
"""
    views_content = views_content.replace("def download_ticket_pdf(request, booking_id):", new_view + "\ndef download_ticket_pdf(request, booking_id):")
    with open(views_path, 'w', encoding='utf-8') as f:
        f.write(views_content)
    print("Added download_event_ticket_pdf to views.py")

# 2. Update urls.py
urls_path = os.path.join('movies', 'urls.py')
with open(urls_path, 'r', encoding='utf-8') as f:
    urls_content = f.read()

if "event_ticket_pdf" not in urls_content:
    urls_content = urls_content.replace(
        "path('event/<int:event_id>/', views.event_detail, name='event_detail'),",
        "path('event/booking/<int:booking_id>/ticket/', views.download_event_ticket_pdf, name='download_event_ticket'),\n    path('event/<int:event_id>/', views.event_detail, name='event_detail'),"
    )
    with open(urls_path, 'w', encoding='utf-8') as f:
        f.write(urls_content)
    print("Added download_event_ticket to urls.py")

# 3. Update profile.html to add download button
profile_path = os.path.join('templates', 'users', 'profile.html')
with open(profile_path, 'r', encoding='utf-8') as f:
    profile_content = f.read()

target_html = """<button class="btn btn-sm text-white fw-bold w-100" style="background-color: #00d2ff; border-radius: 20px;" disabled>
                      <i class="fas fa-check-circle me-1"></i> PAID
                    </button>"""

replacement_html = """<button class="btn btn-sm text-white fw-bold w-100 mb-2" style="background-color: #00d2ff; border-radius: 20px;" disabled>
                      <i class="fas fa-check-circle me-1"></i> PAID
                    </button>
                    <a href="{% url 'download_event_ticket' e_booking.id %}" class="btn btn-sm text-white fw-bold w-100" style="background-color: #ff4b82; border-radius: 20px;">
                      <i class="fas fa-download me-1"></i> PDF
                    </a>"""

if target_html in profile_content:
    profile_content = profile_content.replace(target_html, replacement_html)
    with open(profile_path, 'w', encoding='utf-8') as f:
        f.write(profile_content)
    print("Added PDF download button to profile.html")
else:
    print("Could not find button HTML in profile.html to replace")
