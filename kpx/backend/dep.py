from kpx.backend.modules import *
from kpx.backend.autorization import get_autorization_data
from .cmdargs import CmdArgs

args = CmdArgs.get_args()
name, public_key = get_autorization_data()