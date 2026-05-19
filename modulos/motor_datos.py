from pathlib import Path
from datetime import datetime

def log(mensaje: str, funcion: str = '', modulo: str = 'main', error: Exception = 'ERROR') -> str:
    log_error: str = f'[{datetime.now}] - {error} - ({modulo}:{funcion}): {mensaje}'
    return log_error

def lectura_csv(path: Path) -> list:
    if not path.exists():
        print(f"El archivo no existe en: {path.absolute()}")
        return []
    try:
        with open(path, 'r', encoding='utf-8') as archivo:
            filas: list = archivo.read().strip().split('\n')
            llaves: list = [l.strip().replace('"', '') for l in filas[0].split(',')]
            lista_usuarios: list = []

            for i in range(1, len(filas)):
                valores: list = [l.strip().replace('"', '') for l in filas[i].split(',')]
                usuario_actual: dict = {}
                for j in range(len(llaves)):
                    columna = llaves[j].strip()
                    valor = valores[j].strip()
                    usuario_actual[columna] = valor
                lista_usuarios.append(usuario_actual)
            return lista_usuarios
    except Exception as e:
        print(log('No se pudo leer el archivo.', 'lectura_csv', 'motor_datos.py', e))
        return []

def buscar_cedula(lista: list, cedula: str) -> tuple:
    valido: bool = False
    mensaje: str = ''
    for usuario in lista:
        cedula_comparacion: str = usuario['Cedula'].strip()
        if cedula_comparacion == cedula:
            valido = True
            if usuario['Estatus'] == 'Activo':
                mensaje = 'El usuario se encuentra activo.'
                return True, mensaje
            else:
                mensaje = 'El usuario se encuentra inactivo. No se le puede hacer entrega de notas.'
                return False, mensaje
                break
    if not valido:
        mensaje = f'Cedula no registrada ({cedula}). Intente nuevamente.'
    return False, mensaje
