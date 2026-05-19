import telebot
from telebot.types import Message
import logging
import os
from dotenv import load_dotenv
from modulos.motor_documento import proceso_guardado, escribir_actividad
from modulos.motor_datos import log
load_dotenv()

class TelegramBot:
    # Clases
    def __init__(self):
        self.TELEGRAM_BOT_KEY=os.getenv('TELEGRAM_BOT_KEY', 'Sin valor.')
        self.bot = telebot.TeleBot(self.TELEGRAM_BOT_KEY)
        self.ADMIN_PASSWORD=os.getenv('ADMIN_PASSWORD', 'Error.')

        # Registro de Message Handlers

        #@ /start
        self.bot.register_message_handler(self.message_handler_inicio, commands=['start'])

        #@ /obtenerInformacionPropia
        self.bot.register_message_handler(self.mh_obtenerinfo, commands=['obtenerinfopropia'])

        #@ /notasCertificadas
        self.bot.register_message_handler(self.mh_obtener_notas_certificadas, commands=['notasCertificadas'])

        #@ Msg Handler General
        self.bot.register_message_handler(self.message_handler_general, func = lambda message: True)

    # Funciones
    def iniciar(self):
        self.bot.infinity_polling(
            timeout=60,
            long_polling_timeout=60,
            logger_level=logging.CRITICAL
        )

    # Acciones Message Handlers
    def message_handler_inicio(self, message: Message):
        escribir_actividad(message.from_user.username ,'ha iniciado el bot')
        self.bot.send_message(message.from_user.id,
    'Hola estimado usuario.\nPor favor, ingrese la clave de acceso:')
        self.bot.register_next_step_handler(message, self.control_acceso)

    def control_acceso(self, message: Message):
        password_in = message.text
        acceso: bool = False

        if password_in == self.ADMIN_PASSWORD:
            mensaje = 'Acceso Concedido'
            acceso = True
            escribir_actividad(message.from_user.username ,'inició sesión.')
        else:
            mensaje = 'Acceso denegado, intente nuevamente.'

        self.bot.send_message(message.chat.id, mensaje)

        if not acceso:
            self.bot.register_next_step_handler(message,
                                                self.control_acceso)

    def mh_obtenerinfo(self, message: Message):
        info: str = ''
        info += f'Chat ID: {message.from_user.id}\n'
        info += f'Nombre de usuario: {message.from_user.username}\n'
        info += f'Nombre: {message.from_user.first_name}\n'
        if message.from_user.last_name is not None:
            info += f'Apellido: {message.from_user.last_name}\n'

        self.bot.send_message(message.from_user.id, info)

    def mh_obtener_notas_certificadas(self, message: Message):
        self.bot.send_message(message.chat.id, 'Escriba su numero de cédula, por favor.')
        self.bot.register_next_step_handler(message, self.obtener_notas)

    def obtener_notas(self, message: Message):
        cedula: str = self.validacion_cedula(message)
        if cedula:
            self.bot.send_message(message.chat.id, 'Cédula válida.')
            archivo_notas, mensaje = proceso_guardado(cedula)
            if archivo_notas:
                self.bot.send_message(message.chat.id, mensaje)
                try:
                    self.bot.send_document(message.chat.id, open(archivo_notas, 'rb'))
                    os.remove(archivo_notas)
                    escribir_actividad(message.from_user.username ,'recibio sus notas.')
                except Exception as e:
                    msg_error: str = 'Ocurrio un error al enviar el archivo.'
                    print(log(msg_error, 'obtener_notas', 'telegram_bot.py', e))
                    self.bot.send_message(message.chat.id, msg_error)
            else:
                self.bot.send_message(message.chat.id, mensaje)
        else:
            self.bot.send_message(message.chat.id, 'Cédula inválida, intente nuevamente.')
            self.bot.register_next_step_handler(message, self.obtener_notas)

    def message_handler_general(self, message: Message):
        self.bot.send_message(message.from_user.id,'Esperando un comando válido.')

    # Metodos Estaticos

    @staticmethod
    def validacion_cedula(message: Message) -> str | None:
        cedula: str = message.text.strip()
        if cedula.upper().startswith('V'):
            cedula = cedula[1:]
        if cedula.isdigit() and len(cedula) in [6, 7, 8]:
            return cedula
        else:
            return None




