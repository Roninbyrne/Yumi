from Yumi.core.bot import RoninBot
from Yumi.core.dir import dirr
from Yumi.core.git import git
from Yumi.misc import dbb, heroku

from .logging import LOGGER

dirr()
git()
dbb()
heroku()

app = RoninBot()
