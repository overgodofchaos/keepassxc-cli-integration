from keepassxc_cli_integration import kpx
from keepassxc_cli_integration.backend import dep, utils, autorization


def main():
    match dep.args.mode:
        case "get":
            url = dep.args.url
            value = dep.args.value
            name = dep.args.name

            value = kpx.get_value(url, value, name)

            if dep.args.bat:
                print(utils.escape_for_bat(value))
                return

            print(value)

        # case "associate":
        #     if sum([
        #         dep.args.delete is not None,
        #         dep.args.clear,
        #         dep.args.show
        #     ]) == 0:
        #         kpx.associate()
        #         print("Association completed")
        #         return
        #
        #     if dep.args.show:
        #         print(autorization.read_settings_text())
        #         return
        #
        #     if dep.args.clear:
        #         kpx.delete_association(all_=True)
        #         return
        #
        #     if dep.args.delete is not None:
        #         id_ = dep.args.delete
        #         if id_ == "":
        #             id_ = "current"
        #         if id_ in ["current"]:
        #             kpx.delete_association(current=True)
        #         else:
        #             kpx.delete_association(id_=id_)
        #         print(f"Association deleted: {id_}")
        #         return

        case "associate":
            match [dep.args.command, dep.args.select]:
                case "add":
                    kpx.associate()

                case "delete", select:
                    match select:
                        case "current":
                            kpx.delete_association(current=True)
                        case "all":
                            kpx.delete_association(all_=True)
                        case _:
                            kpx.delete_association(id_=select)

                case "show", select:
                    print(autorization.read_settings_text())


if __name__ == '__main__':
    main()