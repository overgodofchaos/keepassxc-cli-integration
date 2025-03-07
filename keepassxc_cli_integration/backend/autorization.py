from keepassxc_cli_integration.backend.modules import *


settings_path = Path().home() / ".kpx"
settings_path.mkdir(exist_ok=True, parents=True)
settings_file = settings_path / "settings.toml"


def get_autorization_data() -> list[dict[str, bytes]]:
    if settings_file.exists():
        settings = utils.read_toml(settings_file)
    else:
        utils.write_toml(settings_file, {})
        settings = utils.read_toml(settings_file)

    connection = kpx_protocol.Connection()
    connection.connect()

    if connection.get_databasehash() not in settings:
        connection.associate()
        id_, public_key = connection.dump_associate()

        autorization_data = {
            "id": id_,
            "public_key": public_key.hex(),
        }

        settings[connection.get_databasehash()] = autorization_data
        utils.write_toml(settings_file, settings)

    associates = [
        {
            "id": settings[connection.get_databasehash()]["id"],
            "key": bytes.fromhex(settings[connection.get_databasehash()]["public_key"])
        }
    ]

    current = settings[connection.get_databasehash()]["id"]

    for key, val in settings.items():
        if val["id"] != current:
            associates.append({
                "id": val["id"],
                "key": bytes.fromhex(val["public_key"])}
            )

    # noinspection PyTypeChecker
    return associates





