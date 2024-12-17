# myapp/views.py
from django.shortcuts import render

import requests
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt



def index(request):
    return render(request, 'index.html')


def about(request):
    return render(request, 'about.html')


# def imgr(request):
#     return render(request, 'imgr.html')


def med(request):
    return render(request, 'med.html')


def communite(request):
    return render(request, 'communite.html')

# Dictionnaire de mapping des codes de langue
LANGUAGE_MAPPING = {
    "en_EN": "en_XX",
    "fr_FR": "fr_XX",
    "ar_AR": "ar_AR",
    "de_DE": "de_DE",
    "es_ES": "es_XX",
    "it_IT": "it_IT",
    "zh_CN": "zh_CN",
    "ru_RU": "ru_RU",
    "ja_JA": "ja_XX",
    "tr_TR": "tr_TR"
}

# Vue pour afficher la page principale
def translation_assistant(request):
    languages = list(LANGUAGE_MAPPING.keys())
    return render(request, 'translation_assistant.html', {'languages': languages})

# Vue pour gérer la traduction
@csrf_exempt
def translate_text(request):
    if request.method == 'POST':
        try:
            # Récupérer les paramètres POST
            source_country = request.POST.get('sourceCountry')
            target_country = request.POST.get('targetCountry')
            text_to_translate = request.POST.get('textToTranslate')

            # Convertir les codes pays en codes langue standards
            src_lang = LANGUAGE_MAPPING.get(source_country, 'en_XX')
            target_lang = LANGUAGE_MAPPING.get(target_country, 'fr_XX')

            # Vérifier les paramètres
            if not all([source_country, target_country, text_to_translate]):
                return JsonResponse({
                    'success': False,
                    'error': 'Paramètres manquants'
                }, status=400)

            # URL de l'API de traduction
            link = "https://799a-34-125-161-197.ngrok-free.app/"
            url = f"{link}post_message"

            # Données à envoyer
            data = {
                "message": text_to_translate,
                "src_lang": src_lang,
                "target_lang": target_lang,
            }

            print(data)

            # Envoyer la requête
            response = requests.post(url, json=data)

            # Vérifier la réponse de l'API
            if response.status_code == 200:
                result = response.json()
                return JsonResponse({
                    'success': True,
                    'original_text': text_to_translate,
                    'source_language': source_country,
                    'target_language': target_country,
                    'translated_text': result.get('response', ''),
                    'transcription': result.get('transcription', '')
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'Service de traduction indisponible'
                }, status=500)

        except requests.RequestException as e:
            return JsonResponse({
                'success': False,
                'error': f'Erreur réseau : {str(e)}'
            }, status=500)

        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Erreur inattendue : {str(e)}'
            }, status=500)

    return JsonResponse({'success': False, 'error': 'Méthode non autorisée'}, status=405)





import pytesseract
from PIL import Image
from django.shortcuts import render
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.http import JsonResponse

 
import pytesseract
from PIL import Image
from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
from django.conf import settings
import os  # Assurez-vous que os est importé en haut de votre fichier

from pathlib import Path
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from PIL import Image
import pytesseract
import requests
import base64
from pprint import pp

from pathlib import Path
from django.conf import settings
from django.core.files.storage import FileSystemStorage
import base64
import requests
from PIL import Image
from io import BytesIO

# Fonction pour encoder l'image en base64
def file_to_base64(file_path):
    with open(file_path, "rb") as file:
        encoded_string = base64.b64encode(file.read()).decode('utf-8')
    return encoded_string

# Fonction pour redimensionner l'image avant envoi
def resize_image(file_path, max_size=500):
    image = Image.open(file_path)
    width, height = image.size
    if max(width, height) > max_size:
        scaling_factor = max_size / max(width, height)
        new_size = (int(width * scaling_factor), int(height * scaling_factor))
        image = image.resize(new_size, Image.Resampling.LANCZOS)
    return image

def imgr(request):
    extracted_text = ''
    image_url = ''
    system_prompt = 'Translate the text in this image to arabic:'  # Default system prompt

# system_prompt = "where is this place?"
# system_prompt = "is it day or night?"
# system_prompt = "Translate the text in this image to arabic"

    if request.method == 'POST' and request.FILES.get('image'):
        # Get the system prompt from the form (if provided)
        system_prompt = request.POST.get('system_prompt', system_prompt)
        print(system_prompt)

        # Get the uploaded image
        image = request.FILES['image']
        
        # Save the uploaded image
        fs = FileSystemStorage()
        filename = fs.save(image.name, image)
        file_url = fs.url(filename)

        # Get the image path
        image_path = Path(settings.MEDIA_ROOT) / filename
        
        # Resize image if necessary
        resized_image = resize_image(image_path)
        resized_image.save('resized_image.png', format="PNG")

        # Convert the image to base64
        buffered = BytesIO()
        resized_image.save(buffered, format="PNG")
        encoded_image = base64.b64encode(buffered.getvalue()).decode('utf-8')

        # Send the image and system prompt to the Flask OCR API
        url = 'http://localhost:5000/image'
        response = requests.post(url, json={'image': encoded_image, 'system_prompt': system_prompt})

        # Check the response
        if response.status_code == 200:
            response_data = response.json()
            extracted_text = response_data.get('result', 'No text extracted.')
        else:
            extracted_text = "Error extracting text."

        # Return the image URL and extracted text to the template
        image_url = file_url

    return render(request, 'imgr.html', {'extracted_text': extracted_text, 'image_url': image_url})