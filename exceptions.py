"""
Excepciones específicas del proyecto PriceWatcher.

Todas las excepciones del proyecto deben heredar de
PriceMonitorError para poder capturarlas conjuntamente
cuando sea necesario.
"""


class PriceMonitorError(Exception):
    """Excepción base del proyecto."""


class UnsupportedStoreError(PriceMonitorError):
    """La URL pertenece a un comercio no soportado."""


class InvalidProductURLError(PriceMonitorError):
    """La URL pertenece al comercio, pero no a un producto."""


class ProductNotFoundError(PriceMonitorError):
    """El producto ya no existe (HTTP 404 o equivalente)."""


class PriceNotFoundError(PriceMonitorError):
    """No se ha podido localizar el precio del producto."""


class ProductNameNotFoundError(PriceMonitorError):
    """No se ha podido localizar el nombre del producto."""


class NetworkError(PriceMonitorError):
    """No se ha podido acceder a la página (timeout, DNS, SSL...)."""


class InvalidResponseError(PriceMonitorError):
    """La respuesta recibida del servidor es inválida."""
