import re

class Phone:
    def __init__(self, owner, phoneNumber):
        self.owner = owner
        
        phone_str = re.sub(r'[^\d+]', '', str(phoneNumber))
        
        if '+' in phone_str:
            if not phone_str.startswith('+') or phone_str.count('+') > 1:
                raise ValueError("Wrong '+' position!")
            phone_digits = phone_str[1:]  
            if not phone_digits.isdigit():
                raise ValueError("После '+' должны быть только цифры")
            if len(phone_digits) < 9 or len(phone_digits) > 15:
                raise ValueError("Max length = [9, 15]")
        else:
            raise ValueError("There must be '+' in number!")
   
        self.phoneNumber = phone_str