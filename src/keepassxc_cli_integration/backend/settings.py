import shutil
from pathlib import Path

from pydantic import BaseModel

from . import kpx_protocol, utils

settings_path = Path().home() / ".keepassxc-cli-integration"
settings_path.mkdir(exist_ok=True, parents=True)
settings_file = settings_path / "settings.json"


class Settings(BaseModel):
    associates: kpx_protocol.Associates = kpx_protocol.Associates()

    @classmethod
    def read(cls) -> "Settings":
        return read_settings()

    def write(self) -> None:
        write_settings(self)


def read_settings() -> Settings:
    if settings_file.exists():
        settings = Settings.model_validate_json(utils.read_text(settings_file))
    else:
        settings = Settings()

    return settings


def write_settings(settings: Settings) -> None:
    utils.write_text(settings_file, settings.model_dump_json(indent=2))


# def get_autorization_data() -> list[dict[str, bytes]]:
#     settings = read_settings()
#
#     connection = kpx_protocol.Connection()
#     connection.connect()
#
#     if connection.get_databasehash() not in settings:
#         connection.associate()
#         associate = connection.dump_associate()[0]
#         id_ = associate["id"]
#         public_key = associate["key"]
#
#         if id_.lower() in ["all", "current"]:
#             raise SystemError(f"Prohibited name for association: {id_}")
#
#         autorization_data = {
#             "id": id_,
#             "key": public_key.hex(),
#         }
#
#         settings[connection.get_databasehash()] = autorization_data
#         utils.write_toml(settings_file, settings)
#
#     associates = [
#         {
#             "id": settings[connection.get_databasehash()]["id"],
#             "key": bytes.fromhex(settings[connection.get_databasehash()]["key"])
#         }
#     ]
#
#     current = connection.get_databasehash()
#
#     for key, val in settings.items():
#         if key != current:
#             associates.append({
#                 "id": val["id"],
#                 "key": bytes.fromhex(val["key"])}
#             )
#
#     # noinspection PyTypeChecker
#     return associates
#
#
# def delete_autorization_data(
#         db_hash: str | None = None,
#         id_: str | None = None,
#         all_: bool = False,
#         current: bool = False) -> None:
#
#     if current:
#         connection = kpx_protocol.Connection()
#         connection.connect()
#         current_hash = connection.get_databasehash()
#         delete_autorization_data(db_hash=current_hash)
#         return
#
#     if all_:
#         shutil.rmtree(settings_path)
#         return
#
#     if id_:
#         settings = read_settings()
#
#         target = None
#         for key, val in settings.items():
#             if val["id"] == id_:
#                 target = key
#                 break
#
#         if target:
#             settings.pop(target)
#             utils.write_toml(settings_file, settings)
#         else:
#             raise Exception(f"Association with id not found: {id_}.")
#
#         return
#
#     if db_hash:
#         settings = read_settings()
#
#         if db_hash in settings:
#             settings.pop(db_hash)
#             utils.write_toml(settings_file, settings)
#         else:
#             raise Exception(f"Association with hash not found: {db_hash}.")
#
#         return
