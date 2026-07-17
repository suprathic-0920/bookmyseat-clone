import os
import re

payment_html_path = os.path.join('templates', 'movies', 'payment.html')
with open(payment_html_path, 'r', encoding='utf-8') as f:
    html = f.read()

# Replace the Food section
food_section_start = '<h5>Add Food & Beverages <i class="fas fa-popcorn text-warning"></i></h5>'
food_section_end = '<!-- Total Amount div comes after this block -->'

# We can replace everything inside `<div class="mb-4 p-3 rounded" style="background-color: var(--surface-light); border: 1px solid var(--border-color);">`
# Up to `</div>\n\n                        <div class="mb-4 p-3 rounded text-center"`

old_block_pattern = r'<div class="mb-4 p-3 rounded"[^>]*>\s*<h5>Add Food.*?</div>\s*<div class="mb-4 p-3 rounded text-center"'

new_block = """<div class="mb-4 p-4 rounded shadow" style="background-color: #1a1a2e; border: 1px solid #16213e;">
                            <h5 class="mb-4 font-weight-bold text-white border-bottom border-secondary pb-3">Add Food & Beverages <i class="fas fa-popcorn text-warning ms-2"></i></h5>
                            {% if food_items %}
                                <div class="food-list">
                                {% for food in food_items %}
                                    <div class="d-flex align-items-center justify-content-between p-3 mb-3 rounded food-item-card" style="background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.05); transition: all 0.3s ease;">
                                        <div class="d-flex align-items-center">
                                            {% if food.image %}
                                                <img src="{{ food.image.url }}" alt="{{ food.name }}" class="rounded shadow-sm me-3" style="width: 65px; height: 65px; object-fit: cover; border: 2px solid rgba(255,255,255,0.1);">
                                            {% else %}
                                                <div class="bg-dark rounded shadow-sm me-3 d-flex justify-content-center align-items-center" style="width: 65px; height: 65px; border: 1px solid rgba(255,255,255,0.1);">
                                                    <i class="fas fa-hamburger text-white fa-lg" style="opacity: 0.7;"></i>
                                                </div>
                                            {% endif %}
                                            <div>
                                                <h6 class="mb-1 fw-bold text-white" style="letter-spacing: 0.5px;">{{ food.name }}</h6>
                                                <div class="text-success fw-bold small">₹{{ food.price }}</div>
                                            </div>
                                        </div>
                                        
                                        <!-- Custom Stepper -->
                                        <div class="d-flex align-items-center rounded-pill px-2 py-1 shadow-sm" style="background: rgba(0,0,0,0.4); border: 1px solid rgba(255,255,255,0.1);">
                                            <button type="button" class="btn btn-sm text-white rounded-circle d-flex justify-content-center align-items-center decrement-btn" data-id="{{ food.id }}" style="width: 32px; height: 32px; background: rgba(255,255,255,0.1); border: none; transition: 0.2s;">
                                                <i class="fas fa-minus" style="font-size: 12px;"></i>
                                            </button>
                                            
                                            <input type="number" class="form-control form-control-sm food-qty text-center mx-2 border-0 bg-transparent text-white" name="food_{{ food.id }}" id="food-input-{{ food.id }}" data-price="{{ food.price }}" value="0" min="0" max="10" style="width: 35px; font-weight: bold; font-size: 16px; pointer-events: none;" readonly>
                                            
                                            <button type="button" class="btn btn-sm btn-danger text-white rounded-circle d-flex justify-content-center align-items-center increment-btn" data-id="{{ food.id }}" style="width: 32px; height: 32px; border: none; transition: 0.2s; box-shadow: 0 4px 8px rgba(220, 53, 69, 0.4);">
                                                <i class="fas fa-plus" style="font-size: 12px;"></i>
                                            </button>
                                        </div>
                                    </div>
                                {% endfor %}
                                </div>
                            {% else %}
                                <p class="text-muted mb-0">No food items available at this theater.</p>
                            {% endif %}
                        </div>

                        <div class="mb-4 p-3 rounded text-center"""

html = re.sub(old_block_pattern, new_block, html, flags=re.DOTALL)

# Now, we must inject custom JavaScript for the increment/decrement logic since we disabled direct text input.
# The previous JS listened to 'input' event on '.food-qty'.
# Let's replace the script block logic for food calculations.

js_old = """    const foodInputs = document.querySelectorAll('.food-qty');
    const totalPriceEl = document.getElementById('total-price');
    const basePrice = parseFloat(totalPriceEl.getAttribute('data-base'));

    foodInputs.forEach(input => {
        input.addEventListener('input', updatePrice);
    });

    function updatePrice() {
        let total = basePrice;
        foodInputs.forEach(input => {
            const qty = parseInt(input.value) || 0;
            const price = parseFloat(input.getAttribute('data-price'));
            total += qty * price;
        });
        totalPriceEl.innerText = '₹' + total.toFixed(2);
    }"""

js_new = """    const foodInputs = document.querySelectorAll('.food-qty');
    const totalPriceEl = document.getElementById('total-price');
    const basePrice = parseFloat(totalPriceEl.getAttribute('data-base'));
    
    // Add hover effect via JS for a premium feel
    document.querySelectorAll('.food-item-card').forEach(card => {
        card.addEventListener('mouseenter', () => card.style.background = 'rgba(255,255,255,0.08)');
        card.addEventListener('mouseleave', () => card.style.background = 'rgba(255,255,255,0.03)');
    });

    document.querySelectorAll('.increment-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            const id = btn.getAttribute('data-id');
            const input = document.getElementById('food-input-' + id);
            let val = parseInt(input.value) || 0;
            if(val < 10) {
                input.value = val + 1;
                updatePrice();
            }
        });
    });

    document.querySelectorAll('.decrement-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            const id = btn.getAttribute('data-id');
            const input = document.getElementById('food-input-' + id);
            let val = parseInt(input.value) || 0;
            if(val > 0) {
                input.value = val - 1;
                updatePrice();
            }
        });
    });

    function updatePrice() {
        let total = basePrice;
        foodInputs.forEach(input => {
            const qty = parseInt(input.value) || 0;
            const price = parseFloat(input.getAttribute('data-price'));
            total += qty * price;
        });
        totalPriceEl.innerText = '₹' + total.toFixed(2);
    }"""

if js_old in html:
    html = html.replace(js_old, js_new)
else:
    print("WARNING: Could not find exact JS match to replace, trying regex")
    html = re.sub(r'const foodInputs.*?totalPriceEl\.innerText =.*?\}', js_new, html, flags=re.DOTALL)


with open(payment_html_path, 'w', encoding='utf-8') as f:
    f.write(html)

print("Food UI updated to look premium!")
