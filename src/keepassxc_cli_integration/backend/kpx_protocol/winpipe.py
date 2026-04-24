import platform

if platform.system() == "Windows":
    import win32file


class WinNamedPipe:
    """ Unix socket API compatible class for accessing Windows named pipes """

    def __init__(self,
                 desired_access: int,
                 creation_disposition: int,
                 share_mode: int = 0,
                 security_attributes: bool | None = None,
                 flags_and_attributes: int = 0,
                 input_nullok: None = None) -> None:
        self.desired_access = desired_access
        self.creation_disposition = creation_disposition
        self.share_mode = share_mode
        self.security_attributes = security_attributes
        self.flags_and_attributes = flags_and_attributes
        self.input_nullok = input_nullok
        self.handle = None

    def connect(self, address: str) -> None:
        try:
            self.handle = win32file.CreateFile(
                fr'\\.\pipe\{address}',
                self.desired_access,
                self.share_mode,
                self.security_attributes,
                self.creation_disposition,
                self.flags_and_attributes,
                self.input_nullok
            )
        except Exception as e:
            raise Exception(  # noqa: B904
                f"Error: Connection could not be established to pipe {address}", e
            )

    def close(self) -> None:
        if self.handle:
            self.handle.close()

    def sendall(self, message: str | bytes) -> None:
        win32file.WriteFile(self.handle, message)

    def recv(self, buff_size: int) -> str:
        _, data = win32file.ReadFile(self.handle, buff_size)
        return data