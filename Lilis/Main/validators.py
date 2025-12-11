from django import forms
from datetime import date
from itertools import cycle
import re

def validate_rut_format(rut_numero):

    blacklist = [
        '00000000', '11111111', '22222222', '33333333', 
        '44444444', '55555555', '66666666', '77777777', 
        '88888888', '99999999'
    ]

    rut = rut_numero.upper().replace("-", "").replace(".", "").replace(" ", "")
    
    if len(rut_numero) < 9 or len(rut_numero) > 12:
        raise forms.ValidationError('El formato del RUT es incorrecto.')
    
    rut_aux = rut[:-1]
    dv = rut[-1:]

    if rut_aux in blacklist:
        raise forms.ValidationError('El RUT no es válido.')

    if not rut_aux.isdigit():
        raise forms.ValidationError('El formato del RUT es incorrecto.')

    revertido = map(int, reversed(rut_aux))
    factors = cycle(range(2, 8))
    suma = sum(d * f for d, f in zip(revertido, factors))
    residuo = suma % 11

    if dv == 'K':
        if residuo != 1:
            raise forms.ValidationError('El formato del RUT es incorrecto.')
            
    elif dv == '0':
        if residuo != 0:
            raise forms.ValidationError('El formato del RUT es incorrecto.')
            
    else:
        try:
            if int(dv) != (11 - residuo):
                raise forms.ValidationError('El formato del RUT es incorrecto.')
        
        except ValueError:
            raise forms.ValidationError('El formato del RUT es incorrecto.')
    
    return f"{rut_aux}-{dv}"


def validate_phone_format(value):
    if not isinstance(value, str):
        value = str(value)

    # 1. Limpieza de la cadena: Quitamos espacios, guiones, paréntesis y el '+'
    # Solo dejamos los dígitos.
    numero_limpio = re.sub(r'\D', '', value) 
    numero_final = numero_limpio
    if numero_limpio.startswith('56'):
        parte_local = numero_limpio[2:]
        if len(parte_local) != 9:
            raise forms.ValidationError('El número de teléfono chileno (con código +56) debe tener 9 dígitos locales.')
        numero_final = parte_local
    elif len(numero_limpio) != 9:
        if len(numero_limpio) < 10 or len(numero_limpio) > 15:
             raise forms.ValidationError('El formato de número telefónico no es estándar (mínimo 10, máximo 15 dígitos internacionales).')
        numero_final = numero_limpio
    if len(numero_final) == 9 and not numero_final.startswith('9'):
        pass
    return numero_final

def validate_password(password):
    if len(password) < 8:
        raise forms.ValidationError('La contrasena debe tener al menos 8 caracteres.')

    if not any(char.isupper() for char in password):
        raise forms.ValidationError('La contrasena debe contener al menos una letra mayúscula.')

    if not any(char.islower() for char in password):
        raise forms.ValidationError('La contrasena debe contener al menos una letra minúscula.')

    if not any(char.isdigit() for char in password):
        raise forms.ValidationError('La contrasena debe contener al menos un número.')
    
    return password



def validate_email(email):
    patron = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    
    if not email:
        raise forms.ValidationError('El correo electrónico no puede estar vacío.')

    if not re.match(patron, email):
        raise forms.ValidationError('El formato del correo electrónico no es válido.')
    
    return email

def validate_text_length(value, min_length=2, max_length=100, field_name="El campo", allow_empty=False):
    if not value and allow_empty:
        return value
    if not value:
        raise forms.ValidationError(f'Se requiere un valor para {field_name}.')
    
    value_str = str(value).strip()
    
    if len(value_str) < min_length:
        raise forms.ValidationError(f'{field_name} debe tener al menos {min_length} caracteres.')
    if len(value_str) > max_length:
        raise forms.ValidationError(f'{field_name} no debe exceder los {max_length} caracteres.')
    return value

def validate_alphanumeric(value, field_name="El código", min_length=3):
    if not re.match(r'^[a-zA-Z0-9-]+$', str(value)):
        raise forms.ValidationError(f'{field_name} solo debe contener letras, números y guiones.')
    if len(str(value)) < min_length:
        raise forms.ValidationError(f'{field_name} debe tener al menos {min_length} caracteres.')
    return value

def validate_future_date(value, field_name="La fecha", allow_today=False):
    if not isinstance(value, date):
        raise forms.ValidationError(f'{field_name} debe ser una fecha válida.')
    
    if allow_today and value < date.today():
        raise forms.ValidationError(f'{field_name} no puede ser una fecha pasada.')
    if not allow_today and value <= date.today():
        raise forms.ValidationError(f'{field_name} debe ser una fecha futura.')
    return value

def validate_past_or_today_date(value, field_name="La fecha"):
    if not isinstance(value, date):
        raise forms.ValidationError(f'{field_name} debe ser una fecha válida.')
    
    if value > date.today():
        raise forms.ValidationError(f'{field_name} no puede ser una fecha futura.')
    return value

def validate_is_number(value, field_name="El valor"):
    try:
        float(value)
    except (ValueError, TypeError):
        raise forms.ValidationError(f'{field_name} debe ser un número válido.')
    return value

def validate_positive_number(value, field_name="El valor", allow_zero=True):
    try:
        val = float(value)
    except (ValueError, TypeError):
        raise forms.ValidationError(f'{field_name} debe ser un número válido.')
    
    if allow_zero:
        if val < 0:
            raise forms.ValidationError(f'{field_name} no puede ser negativo.')
    
    return value