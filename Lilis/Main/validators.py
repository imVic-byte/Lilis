from django import forms
from itertools import cycle
def validate_rut_format(rut_numero):
    rut = rut.upper().replace("-", "").replace(".", "")
    rut_aux = rut[:-1]
    dv = rut[-1:]

    if not rut_aux.isdigit() or not (1_000_000 <= int(rut_aux) <= 25_000_000):
        return False

    revertido = map(int, reversed(rut_aux))
    factors = cycle(range(2, 8))
    suma = sum(d * f for d, f in zip(revertido, factors))
    residuo = suma % 11

    if dv == 'K':
        return residuo == 1
    if dv == '0':
        return residuo == 11
    return residuo == 11 - int(dv)

def validate_phone_format(value):
    if not isinstance(value, str):
        value = str(value)

    if not value.isdigit():
        raise forms.ValidationError('El teléfono debe contener solo números.')
    
    if len(value) != 9:
        raise forms.ValidationError('El teléfono debe tener exactamente 9 dígitos.')
    
    return value

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