from fastapi import HTTPException, status

class TenantNotFoundError(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Tenant not found or inactive"
        )

class InsufficientPermissionsError(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Insufficient permissions"
        )

class HallucinationDetectedError(HTTPException):
    def __init__(self, detail: str = "Potential hallucination detected in model response"):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail
        )
