class ResponseManager:
    responses = {
        200: {"description": "OK"},
        404: {"description": "Item not found"},
        302: {"description": "The item was moved"},
        403: {"description": "Not enough privileges"},
    }

    @classmethod
    def get_response(cls, status_code: int):
        """Retrieve a response by status code."""
        return cls.responses.get(status_code, {"description": "Unknown status code"})