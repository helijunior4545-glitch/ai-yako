"""Identity services must be implemented before public API activation."""
class IdentityServiceUnavailable(RuntimeError):
    pass

def authenticate_device(*args, **kwargs):
    raise IdentityServiceUnavailable("Challenge-response device authentication not yet implemented")
