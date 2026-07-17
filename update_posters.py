import os
import django
import random
import shutil

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bookmyseat.settings')
django.setup()

from movies.models import Movie
from django.core.files import File

def update_posters():
    artifact_dir = r"C:\Users\supra\.gemini\antigravity-ide\brain\d57779be-28b4-4a89-bea8-86d0517efe0d"
    
    # Locate the generated images
    files = os.listdir(artifact_dir)
    scifi = next((f for f in files if f.startswith('scifi_poster')), None)
    action = next((f for f in files if f.startswith('action_poster')), None)
    horror = next((f for f in files if f.startswith('horror_poster')), None)
    comedy = next((f for f in files if f.startswith('comedy_poster')), None)
    
    posters = []
    for f in [scifi, action, horror, comedy]:
        if f:
            posters.append(os.path.join(artifact_dir, f))
            
    if not posters:
        print("No posters found!")
        return
        
    movies = Movie.objects.all()
    print(f"Updating posters for {movies.count()} movies...")
    
    for i, movie in enumerate(movies):
        # We don't overwrite the very first movie if the user wants to keep the original food image
        # Actually, let's just overwrite all the dummy movies (IDs > 1)
        if i == 0:
            continue
            
        random_poster = random.choice(posters)
        filename = os.path.basename(random_poster)
        
        with open(random_poster, 'rb') as img_file:
            movie.image.save(filename, File(img_file), save=True)
            
    print("Successfully updated posters!")

if __name__ == '__main__':
    update_posters()
