import os
from datetime import datetime as dt
from openpyxl import load_workbook
from pathlib import Path
import shutil
from modulos.motor_datos import lectura_csv, buscar_cedula
from modulos.motor_datos import log

CWD = Path.cwd()
plantilla: Path = CWD / 'archivos' / 'plantilla_oficial.xlsx'
archivo_temp: Path = CWD / 'archivos' / 'temp' / 'info_temp.xlsx'
BDD: Path = CWD / 'archivos' / 'departamento.csv'
archivo_logs: Path = CWD / 'archivos' / 'logs_acceso.txt'

def guardar_con_plantilla_temp(usuarios: list, cedula: str) -> str | None:
    archivo = load_workbook(plantilla, data_only=True)
    nombre_hoja: str = 'Sheet1'
    hoja = archivo[nombre_hoja]
    nombre_archivo: str = ''
    try:
        for usuario in usuarios:
            if usuario['Cedula'] == cedula.strip():
                nota1: int = int(usuario['Corte 1'])
                nota2: int = int(usuario['Corte 2'])
                nota3: int = int(usuario['Corte 3'])
                usuario['Nota Final'] = str(float(nota1*0.3 + nota2*0.3 + nota3*0.4))
                fila: list = list(usuario.values())
                hoja.append(fila)
                nombre_archivo = f'{usuario['Nombre']}_{usuario['Apellido']}_Notas.xlsx'
        archivo.save(archivo_temp)
        print('Archivo guardado exitosamente.')
        return nombre_archivo
    except Exception as e:
        print(log('No se pudo guardar el archivo.', 'guardar_con_plantilla_temp'
                  , 'motor_documento.py', e))
        return None

def proceso_guardado(cedula: str) -> tuple:
    archivo_final: Path = CWD / 'archivos'
    datos_usuarios = lectura_csv(BDD)
    validado, mensaje = buscar_cedula(datos_usuarios, cedula.strip())

    if not validado:
        return None, mensaje

    nombre_archivo = guardar_con_plantilla_temp(datos_usuarios, cedula)
    if nombre_archivo:
        try:
            ruta_final = archivo_final / nombre_archivo
            shutil.copy(archivo_temp, ruta_final)

            if archivo_temp.exists():
                os.remove(archivo_temp)
            return ruta_final, mensaje
        except Exception as e:
            print(log('Hubo un error al copiar el archivo final.', 'proceso_guardado'
                      , 'motor_documento.py', e))
            return None, mensaje
    else:
        print(log('No se pudo generar el archivo temporal.', 'proceso_guardado'
                  , 'motor_documento.py'))
        return None, mensaje

def escribir_actividad(usuario: str, mensaje: str):
    if archivo_logs.exists() and archivo_logs.is_file():
        try:
            with open(archivo_logs ,'a', encoding='utf-8') as log_acceso:
                log_acceso.write(f'{str(dt.now())}: El usuario {usuario} {mensaje}\n')
            print('Log registrado exitosamente.')
        except Exception as e:
            print(log('Ocurrio un error al abrir el archivo de logs.', 'escribir_actividad'
                      , 'motor_documento.py', e))