from assets.core.validation.base import BaseValidator
from assets.core.exceptions import ValidationError

class VersionSequenceValidator(BaseValidator):
    """Ensures versions for a specific asset/department increment by 1."""

    def validate(self, current_latest: int, incoming_version: int):
        expected = current_latest + 1

        # Prevent skipping versions
        if incoming_version != expected:
            raise ValidationError(
                f"Version sequence break: expected {expected}, "
                f"got {incoming_version}"
            )

        # Prevent overwriting versions
        if incoming_version <= current_latest:
            raise ValidationError(
                f"Version sequence break: incoming version would overwrite a "
                f"previous version {expected}"
            )