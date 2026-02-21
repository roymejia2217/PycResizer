"""Excepciones personalizadas del sistema."""


class ImageProcessorError(Exception):
    """Excepcion base para errores del procesador de imagenes."""

    def __init__(self, message: str, code: str = None):
        super().__init__(message)
        self.message = message
        self.code = code

    def __str__(self):
        if self.code:
            return f"[{self.code}] {self.message}"
        return self.message


class ValidationError(ImageProcessorError):
    """Error de validacion de entrada."""
    pass


class ConversionError(ImageProcessorError):
    """Error de conversion de unidades."""
    pass


class ProcessingError(ImageProcessorError):
    """Error durante el procesamiento de imagen."""
    pass


class FileSystemError(ImageProcessorError):
    """Error del sistema de archivos."""
    pass
