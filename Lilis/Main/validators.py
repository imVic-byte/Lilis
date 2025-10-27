from django import forms

def validate_rut_format(rut_numero):
    rut_str = str(rut_numero).zfill(8)
    multiplicadores = [2, 3, 4, 5, 6, 7]
    suma = 0
    for i, digito in enumerate(reversed(rut_str)):
        multiplicador = multiplicadores[i % 6]
        suma += int(digito) * multiplicador

    resto = suma % 11
    digito_verificador = 11 - resto

    if digito_verificador == 11:
        return '0'
    elif digito_verificador == 10:
        return 'K'
    else:
        return str(digito_verificador)

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