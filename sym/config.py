""" configurations """

import os

class Config:

    OWNER_ID = int(os.environ.get("OWNER_ID", 0))
