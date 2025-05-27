import requests
from django.conf import settings
from datetime import datetime

def get_random_dog():
    """
    Get a random dog image using Dog API
    """
    try:
        response = requests.get('https://dog.ceo/api/breeds/image/random')
        response.raise_for_status()
        data = response.json()
        
        if data['status'] == 'success':
            # Получаем породу собаки из URL изображения
            image_url = data['message']
            breed = image_url.split('/breeds/')[1].split('/')[0].replace('-', ' ').title()
            
            return {
                'image_url': image_url,
                'breed': breed
            }
    except Exception as e:
        print(f"Error fetching dog image: {str(e)}")
        return None

def get_random_cat_fact():
    """
    Get a random cat fact using Cat Facts API
    """
    try:
        response = requests.get('https://catfact.ninja/fact')
        response.raise_for_status()
        return response.json()['fact']
    except Exception as e:
        print(f"Error fetching cat fact: {str(e)}")
        return None 