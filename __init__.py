"""AScript stable bootstrap entry.

Keep this file small: application code is loaded by ``remote_loader`` and can
be updated independently from the AScript project imported by the user.
"""

from .remote_loader import start


start()
