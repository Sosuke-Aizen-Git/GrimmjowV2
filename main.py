from bot import Bot
import sys
sys.path.append("/usr/local/lib/python3.10/dist-packages")

import pyrofork
print(pyrofork.__version__)

Bot().run()
