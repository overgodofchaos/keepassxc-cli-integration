from keepassxc_cli_integration.backend.modules import *
from keepassxc_cli_integration.backend.autorization import get_autorization_data
from .cmdargs import CmdArgs

args = CmdArgs.get_args()
name, public_key = get_autorization_data()