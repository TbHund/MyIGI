import requests
from django.conf import settings
from datetime import datetime

#рандомный факт о котах и рандомная фотка собаки

def get_random_dog():
    try:
        response = requests.get('https://dog.ceo/api/breeds/image/random')
        response.raise_for_status()
        data = response.json()
        
        if data['status'] == 'success':
            #получить породу собаки из URL
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
    try:
        response = requests.get('https://catfact.ninja/fact')
        response.raise_for_status()
        return response.json()['fact']
    except Exception as e:
        print(f"Error fetching cat fact: {str(e)}")
        return None 