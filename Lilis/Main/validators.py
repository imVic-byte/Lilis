from django import forms
from itertools import cycle

def validate_rut_format(rut):
        reversed_digits = map(int, reversed(str(rut)))
        factors = cycle(range(2, 8))
        s = sum(d * f for d, f in zip(reversed_digits, factors))
        return (-s) % 11 if (-s) % 11 < 10 else 'K'

def validate_phone_format(value):

    if not isinstance(value, str):
        value = str(value)

    if not value.isdigit():
        raise forms.ValidationError('El teléfono debe contener solo números.')
    
    if len(value) != 9:
        raise forms.ValidationError('El teléfono debe tener exactamente 9 dígitos.')
    
    return value