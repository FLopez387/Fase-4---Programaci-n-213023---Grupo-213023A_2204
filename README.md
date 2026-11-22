# Software FJ – Fase 4 | Programación (213023)

## Descripción
Proyecto colaborativo desarrollado para la Fase 4 del curso Programación (213023) de la UNAD. El sistema permite gestionar clientes, servicios y reservas de la empresa Software FJ, aplicando programación orientada a objetos, manejo de excepciones y registro de eventos mediante logs. No utiliza base de datos: la información se maneja con objetos y listas, y el único archivo generado es el registro de eventos y errores.

## Módulos
- `FASE_4.py`: punto de entrada del sistema, excepciones base (`SoftwareFJError`, `DatoInvalidoError`, `ServicioNoDisponibleError`) y configuración de logs.
- `Clase_cliente.py`: clase `Cliente` con encapsulación y validación de datos personales.
- `calculo_costos.py`: `CalculadoraCostos`, con cálculo de costos con parámetros opcionales (impuesto y descuento).
- `servicios.py`: clase abstracta `Servicio` y servicios especializados.
- `Reserva.py`: clase `Reserva`, estados y simulaciones de prueba.
- `config_logging.py`: configuración del registro de eventos.

## Arquitectura orientada a objetos
- **Abstracción:** `Servicio` (clase abstracta con `calcular_costo`, `describir_servicio` y `validar_parametros`).
- **Herencia y polimorfismo:** `ReservaSala`, `AlquilerEquipo` y `AsesoriaEspecializada` heredan de `Servicio` y sobrescriben sus métodos.
- **Encapsulación:** atributos protegidos con propiedades y validaciones en `Cliente`, `Servicio` y `Reserva`.
- **Sobrecarga (parámetros opcionales):** `CalculadoraCostos.calcular_costo(costo_base, impuesto=0, descuento=0)`.

## Manejo de excepciones
- **Excepciones personalizadas:** `DatoInvalidoError`, `DatoPersonalInvalidoError`, `ParametroServicioInvalidoError`, `DuracionInvalidaError`, `ServicioNoDisponibleError`, `ReservaError`, `EstadoReservaInvalidoError` y `ReservaDuplicadaError`.
- **Bloques utilizados:** `try/except`, `try/except/else` y `try/except/finally`.
- **Encadenamiento:** `raise ... from ...` para conservar la causa original del error.

## Estados de la reserva
`pendiente` → `confirmada` → `en_proceso` → `completada`. Una reserva puede pasar a `cancelada` desde `pendiente`, `confirmada` o `en_proceso`. Los estados `completada` y `cancelada` son finales; cualquier otra transición genera `EstadoReservaInvalidoError`.

## Logs
Los eventos y errores se registran en el archivo `sistema_fj.log`, que se crea al ejecutar el sistema. Cada línea incluye fecha y hora, nivel (`INFO`, `WARNING`, `ERROR`, `CRITICAL`) y mensaje.

## Ejecución
1. Clonar el repositorio:
   ```
   git clone https://github.com/FLopez387/Fase-4---Programaci-n-213023---Grupo-213023A_2204
   cd Fase-4---Programaci-n-213023---Grupo-213023A_2204
   ```
2. Ejecutar el archivo principal (requiere Python 3.8 o superior, sin librerías externas):
   ```
   python FASE_4.py
   ```
3. Revisar el archivo `sistema_fj.log` generado en la misma carpeta.

## Simulaciones
El sistema ejecuta simulaciones válidas e inválidas (creación, confirmación, procesamiento y cancelación de reservas, duraciones inválidas, transiciones de estado no permitidas, parámetros de servicio inválidos y correos con formato incorrecto), con evidencias en el documento PDF de la actividad.

## Flujo de trabajo en GitHub
- Cada integrante trabaja en su propia rama (por ejemplo `Nombre_Apellido/modulo`).
- Los cambios se hacen con commits pequeños y descriptivos.
- Se integran a la rama principal mediante pull requests revisados por otro integrante.

## Tecnologías
- Python
- Git y GitHub
- Programación orientada a objetos
- Manejo de excepciones
- Logging

## Equipo
Proyecto colaborativo – Grupo 213023A_2204, UNAD.

| Integrante | Aporte principal |
|---|---|
| Luisa Fernanda López Díaz | Creación del repositorio y clase abstracta base |
| Fredy Andrés Giraldo | `Clase_cliente.py` |
| Dilan Mateo Gómez Salcedo | `calculo_costos.py`, integración final y README |
| Jairo Martín Corrales Navarro | `servicios.py` |
| Harold David Muñoz Maldonado | `Reserva.py` |
