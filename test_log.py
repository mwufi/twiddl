import logging
import datetime
import pytz
import emoji


class Formatter(logging.Formatter):
    """override logging.Formatter to use an aware datetime object"""

    def converter(self, timestamp):
        dt = datetime.datetime.fromtimestamp(timestamp)
        my_tz = pytz.timezone("America/Chicago")
        return dt.astimezone(my_tz)

    def formatTime(self, record, datefmt=None):
        dt = self.converter(record.created)
        if datefmt:
            s = dt.strftime(datefmt)
        else:
            try:
                s = dt.isoformat(timespec="milliseconds")
            except TypeError:
                s = dt.isoformat()
        return s


myFormatter = Formatter(
    "%(asctime)s - %(name)s %(levelname)s - %(message)s", "%y-%b-%Y %H:%M:%S"
)


# here, we make a new logger
logger = logging.getLogger(__name__)

handler = logging.FileHandler('test.log')
handler.setFormatter(myFormatter)
logger.addHandler(handler)

handler = logging.StreamHandler()
handler.setFormatter(myFormatter)
logger.addHandler(handler)

logger.setLevel(logging.DEBUG)


def log(*args):
    logger.debug(" ".join(map(str, args)))


class Puppy:
    def __init__(self, name):
        self.name = name

    def __str__(self) -> str:
        return f"I'm a puppy named {self.name}"


log({"a": 1, "b": 2})
log(myFormatter, "hi there!", 1 + 2)
log("simple.test", Puppy("jo"))
log(emoji.emojize("Python is :thumbs_up:"))
log("ok, pure emoji now 😻")
logger.info("So should this")
logger.error("And non-ASCII stuff, too, like Øresund and Malmö")
