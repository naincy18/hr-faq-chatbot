import hashlib

# Demo credential store. In a real system this would be a database table,
# never plaintext or hardcoded like this -- but for a hackathon demo,
# storing a HASHED password (not plaintext) is the right middle ground:
# it shows security awareness without needing a full user DB overnight.
#
# Default demo login -> username: admin   password: admin123
# CHANGE THIS before your demo if you want a different password.

def hash_password(password):
    """Turn a plaintext password into a SHA-256 hash (one-way, can't be reversed)."""
    return hashlib.sha256(password.encode()).hexdigest()


ADMIN_CREDENTIALS = {
    "admin": hash_password("admin123"),
}


def verify_admin_login(username, password):
    """
    Returns True if username/password match a stored HR Admin account.
    Never compares plaintext passwords directly -- always compares hashes.
    """
    if username not in ADMIN_CREDENTIALS:
        return False
    return ADMIN_CREDENTIALS[username] == hash_password(password)