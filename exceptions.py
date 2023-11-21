""" Define client and server side exceptions. """


class CustomError(Exception):

    def __init__(self, message, status_code):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class RequestNotFoundError(CustomError):

    def __init__(self, message="Request Not Found"):
        super().__init__(message, 404)


class BadRequestError(CustomError):

    def __init__(self, message="Bad Request"):
        super().__init__(message, 400)


class InternalError(CustomError):

    def __init__(self, message="Internal Server Error"):
        super().__init__(message, 500)
