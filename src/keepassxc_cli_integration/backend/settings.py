from keepassxc_protocol.models_associates import EncryptedAssociate, EncryptedAssociates

from .constants import ASSOCIATE_FILE, PROJECT_PATH
from .legacy import Settings


def update_old_config() -> None:
    #  Update from old version
    old_settings_file = PROJECT_PATH / "settings.json"
    if old_settings_file.exists() and not ASSOCIATE_FILE.exists():
        try:
            f = old_settings_file.read_text(encoding="utf-8")
            old_settings = Settings.model_validate_json(f)
            if old_settings.associates and old_settings.associates.entries:
                new_associates_list: list[EncryptedAssociate] = []

                for value in old_settings.associates.entries.values():
                    new_associates_list.append(
                        EncryptedAssociate(
                            db_hash=value.db_hash,
                            id=value.id,
                            key=f"encrypt-plaintext:{value.key}",
                        ),
                    )

                new_associates = EncryptedAssociates(
                    entries={
                        item.db_hash: item
                        for item in new_associates_list
                    },
                ).decrypt(encrypt_key="default")

                new_associates_json = new_associates.dumps(
                    encrypt_key="default",
                    encrypt_type="system",
                )

                ASSOCIATE_FILE.write_text(new_associates_json, encoding="utf-8")
                old_settings_file.unlink(missing_ok=True)
                print("Config updated to new format.")
        except Exception as e:  # noqa: BLE001
            print(f"Error updating old config.\n{e}\nDelete it manually from ~/.keepassxc-cli-integration")
