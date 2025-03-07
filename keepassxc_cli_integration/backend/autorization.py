from keepassxc_cli_integration.backend.modules import *


settings_path = Path().home() / ".keepassxc-cli-integration"
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
        associate = connection.dump_associate()[0]
        id_ = associate["id"]
        public_key = associate["key"]

        autorization_data = {
            "id": id_,
            "key": public_key.hex(),
        }

        settings[connection.get_databasehash()] = autorization_data
        utils.write_toml(settings_file, settings)

    associates = [
        {
            "id": settings[connection.get_databasehash()]["id"],
            "key": bytes.fromhex(settings[connection.get_databasehash()]["key"])
        }
    ]

    current = connection.get_databasehash()

    for key, val in settings.items():
        if key != current:
            associates.append({
                "id": val["id"],
                "key": bytes.fromhex(val["key"])}
            )

    # noinspection PyTypeChecker
    return associates





