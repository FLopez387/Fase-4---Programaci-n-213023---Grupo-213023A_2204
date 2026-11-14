import logging
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

from FASE_4 import DatoInvalidoError


logger = logging.getLogger(__name__)


class CalculadoraCostos:
    def calcular_costo(self, costo_base, impuesto=0, descuento=0):
        """
        Permite calcular el costo con diferentes cantidades de parámetros:
        calcular_costo(costo_base)
        calcular_costo(costo_base, impuesto)
        calcular_costo(costo_base, impuesto, descuento)

        El impuesto y el descuento se reciben como porcentajes.
        """
        try:
            base = Decimal(str(costo_base))
            iva = Decimal(str(impuesto))
            rebaja = Decimal(str(descuento))

            if not base.is_finite() or not iva.is_finite() or not rebaja.is_finite():
                raise ValueError("Los valores deben ser números finitos.")
            if base <= 0:
                raise ValueError("El costo base debe ser mayor que cero.")
            if iva < 0 or iva > 100:
                raise ValueError("El impuesto debe estar entre 0 y 100.")
            if rebaja < 0 or rebaja > 100:
                raise ValueError("El descuento debe estar entre 0 y 100.")

            valor_con_descuento = base * (Decimal("1") - rebaja / Decimal("100"))
            total = valor_con_descuento * (Decimal("1") + iva / Decimal("100"))
            total = total.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        except (InvalidOperation, TypeError, ValueError) as error:
            logger.exception("Error al calcular el costo.")
            raise DatoInvalidoError(
                "Revise el costo base, el impuesto y el descuento."
            ) from error

        logger.info("Costo calculado correctamente: %s", total)
        return total

    def calcular_costo_servicio(self, servicio, impuesto=0, descuento=0):
        try:
            costo_base = servicio.calcular_costo()
        except (AttributeError, TypeError) as error:
            logger.exception("El servicio no pudo entregar su costo base.")
            raise DatoInvalidoError(
                "El servicio seleccionado no tiene un cálculo de costo válido."
            ) from error

        return self.calcular_costo(costo_base, impuesto, descuento)


if __name__ == "__main__":
    calculadora = CalculadoraCostos()
    print("Costo básico:", calculadora.calcular_costo(100000))
    print("Costo con impuesto:", calculadora.calcular_costo(100000, 19))
    print(
        "Costo con impuesto y descuento:",
        calculadora.calcular_costo(100000, 19, 10),
    )

    try:
        calculadora.calcular_costo(-50000, 19, 10)
    except DatoInvalidoError as error:
        print("No se pudo realizar el cálculo:", error)
