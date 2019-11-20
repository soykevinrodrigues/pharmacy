'''
    Sistema de Pedidos en Farmacias

'''

from modelo import *
from clases import *
import os


class Controlador:

    # TODO realizar de la siguiente manera
    # def __init__(self):
    #     self.modelo = Modelo()

    # TODO ver la forma de abstraer mas este metodo
    farmacia = None
    @staticmethod
    def inicializar():
        '''---------------------- INICIO DE LA APLICACION ---------------------------'''
        dir_ordenes = 'datos_ordenes/ordenes'
        dir_clientes = 'datos_clientes/clientes'
        dir_empleados = 'datos_empleados/empleados'
        dir_comprobantes = 'datos_comprobantes/comprobantes'
        dir_articulos = 'datos_articulos/articulos'

        modelo_app = Modelo()
        # Se cargan los articulos existentes
        if Controlador.existe_pickle(dir_articulos):
            list_articulos = modelo_app.buscar(dir_articulos)
        else:
            list_articulos = []
            modelo_app.crear(dir_articulos, list_articulos)
        farmacia = Farmacia(
            list_articulos, utiles.business_name, utiles.business_ruc)

        Controlador.farmacia = farmacia

        # se cargan los clientes existentes
        if Controlador.existe_pickle(dir_clientes):
            list_clientes = modelo_app.buscar(dir_clientes)
        else:
            list_clientes = []
            modelo_app.crear(dir_clientes, list_clientes)

        # se cargan los empleados existentes
        if Controlador.existe_pickle(dir_empleados):
            list_empleados = modelo_app.buscar(dir_empleados)
        else:
            list_empleados = []
            modelo_app.crear(dir_empleados, list_empleados)

        # se cargan las ordenes existentes
        if Controlador.existe_pickle(dir_ordenes):
            list_ordenes = modelo_app.buscar(dir_ordenes)
        else:
            list_ordenes = []
            modelo_app.crear(dir_ordenes, list_ordenes)
        Orden.numero_orden = len(list_ordenes) + 1
        # se cargan los comprobantes existentes
        if Controlador.existe_pickle(dir_comprobantes):
            list_comprobantes = modelo_app.buscar(dir_comprobantes)
        else:
            list_comprobantes = []
            modelo_app.crear(dir_comprobantes, list_comprobantes)

        farmacia.comprobantes = list_comprobantes
        farmacia.ordenes = list_ordenes
        farmacia.clientes = list_clientes
        farmacia.articulos = list_articulos
        farmacia.empleados = list_empleados
        return farmacia

    @staticmethod
    def filtrar_articulos():
        return Controlador.farmacia.obtener_articulos()

    @staticmethod
    def obtener_cliente_por_defecto():
        persona = Persona(Email(), 6000000, 'ElSEIS', 'MIL', 'Seattle ...', '6000000-1') # TODO quizas poner como constante
        return Cliente(persona)

    @staticmethod
    # TODO optimizar
    def filtrar_articulo_desde(lista, codigo):
        for articulo in lista:
            if articulo.codigo == codigo:
                return articulo
        raise Exception('No se encontro el articulo de codigo: ' + codigo)

    @staticmethod
    def crear_orden(articulos):
        numero_orden = len(Controlador.farmacia.ordenes)
        orden = Controlador.farmacia.realizar_pedido(numero_orden, articulos)
        return orden

    @staticmethod
    def registrar_cliente(cedula, nombre, apellido, ruc, direccion, contacto):
        cliente = Cliente(
            Persona(contacto, cedula, nombre, apellido, direccion, ruc))
        Controlador.farmacia.clientes.append(cliente)
        return cliente

    @staticmethod
    def obtener_nombre_categoria(identificador):
        return utiles.categoria_articulos[identificador]

    @staticmethod
    def obtener_metodo_pago_efectivo():
        return Efectivo('Efectivo', 'Pago mediante efectivo') # TODO poner en constante

    @staticmethod
    def obtener_metodo_pago_tarjeta():
        return Tarjeta('Tarjeta', 'Pago mediante tarjeta') # TODO poner en constante    

    @staticmethod
    def obtener_categorias_articulos():
        return [*(utiles.categoria_articulos)]

    @staticmethod
    def obtener_articulos_por_categoria(categoria):
        articulos = []
        try:
            articulos_categorizados = Controlador.filtrar_articulos()
            articulos = articulos_categorizados[categoria]
        except(KeyError):
            raise Exception('No existe la categoria: ' + str(categoria))
        return articulos

    @staticmethod
    def buscar_orden(identificador, estado_busqueda):
        ordenes = Controlador.farmacia.ordenes
        # TODO averiguar si hay otra forma mas eficiente para filtrar (lambdas?) FILTRAR por estado_busqueda
        for orden in ordenes:
            estado_orden = orden.estado
            if orden.numero_orden == identificador and estado_orden == estado_busqueda:
                return orden
            elif orden.numero_orden == identificador and not estado_orden == estado_busqueda:
                raise Exception('Estado de orden invalida.')

        raise Exception("No se encontro la orden: " + str(identificador))

    @staticmethod
    def buscar_cliente(numero_cedula):
        clientes = Controlador.farmacia.clientes
        for cliente in clientes:
            if cliente.persona.cedula == numero_cedula:
                return cliente
        return None

    @staticmethod
    def crear_comprobante(orden, medio_pago, cliente):
        comprobante = Controlador.farmacia.cobrar_pedido(
            orden, medio_pago, cliente)
        return comprobante

    @staticmethod
    def farmacia_existen_articulos():
        return not Controlador.farmacia.articulos.isEmpty()

    @staticmethod
    def guardar_comprobante(comprobante):
        '''
            Metodo encargado de guardar comprobante en la farmacia
        '''
        Controlador.farmacia.comprobantes.append(comprobante)

    @staticmethod
    def filtrar_comprobantes(condicion):
        return Controlador.farmacia.obtener_reporte(condicion)

    @staticmethod
    def definicion_filtro_comprobante_diario(anio, mes=1, dia=1):
        return (lambda factura: factura.fecha.year == anio
                and factura.fecha.month == mes
                and factura.fecha.day == dia)

    @staticmethod
    def numero_de_semana_por_mes(date_value):
        # Se obtiene la diferencia entre la semana del anio en base a la fecha y la semana del dia que comienza el mes
        # luego se adiciona 1
        return (date_value.isocalendar()[1] - date_value.replace(day=1).isocalendar()[1] + 1)

    @staticmethod
    def definicion_filtro_comprobante_semanal(semana, mes, anio):
        return (lambda factura: Controlador.numero_de_semana_por_mes(factura.fecha) == semana
                and factura.fecha.month == mes and factura.fecha.year == anio)

    @staticmethod
    def definicion_filtro_comprobante_mensual(anio, mes):
        return (lambda factura: factura.fecha.month == mes and factura.fecha.year == anio)

    @staticmethod
    def definicion_filtro_comprobante_anual(anio):
        return (lambda factura: factura.fecha.year == anio)

    @staticmethod
    def existe_pickle(archivopickle, extension='.pickle'):
        '''--------------------- verificar pickle ---------------------'''
        # Metodo estatico que verifica la existencia del archivo pickle
        if os.path.exists(archivopickle + extension):
            return True
        else:
            return False

    @staticmethod
    def guardar_nuevos_datos(farmacia):
        '''Guarda los datos nuevos en los archivos'''
        dir_ordenes = 'datos_ordenes/ordenes'
        dir_clientes = 'datos_clientes/clientes'
        dir_comprobantes = 'datos_comprobantes/comprobantes'
        dir_articulos = 'datos_articulos/articulos'

        modeloapp = Modelo()
        modeloapp.crear(dir_ordenes, farmacia.ordenes)
        modeloapp.crear(dir_clientes, farmacia.clientes)
        modeloapp.crear(dir_comprobantes, farmacia.comprobantes)
        modeloapp.crear(dir_articulos, farmacia.articulos)
