import json
from gahelper import Gahelper

config = json.load(open("../config/config.json"))

ga = Gahelper(config)