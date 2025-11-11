class StatusByte:
    # Bit 0: Day/Night (0=Day, 1=Night)
    # Bit 1: Image Status (0=Fail, 1=Imaging)
    # Bit 2: Camera Power (0=Normal, 1=Resetting)
    # Bit 3: Shutter Status (0=Closed, 1=Open)

    def __init__(self):
        self.byte = 0b00000000
        self._status_file = os.path.expanduser("~/allsky_status.byte")
        self._write_status_file()

    def _write_status_file(self):
        try:
            with open(self._status_file, "w") as f:
                # write integer value and binary representation for convenience
                f.write(f"{self.byte}\n{self.byte:08b}\n")
        except Exception as e:
            logging.debug(f"Failed to write status file {self._status_file}: {e}")

    def _read_status_file(self):
        try:
            if not os.path.isfile(self._status_file):
                return
            with open(self._status_file, "r") as f:
                first = f.readline().strip()
                if not first:
                    return
                # try integer first
                try:
                    self.byte = int(first)
                    return
                except ValueError:
                    pass
                # try binary string
                try:
                    self.byte = int(first, 2)
                    return
                except ValueError:
                    pass
                # fallback: try parsing second line if file was written as int then binary
                second = f.readline().strip()
                if second:
                    try:
                        self.byte = int(second)
                        return
                    except ValueError:
                        try:
                            self.byte = int(second, 2)
                        except ValueError:
                            pass
        except Exception as e:
            logging.debug(f"Failed to read status file {self._status_file}: {e}")

    def set_bit(self, position):
        self.byte |= (1 << position)
        self._write_status_file()

    def clear_bit(self, position):
        self.byte &= ~(1 << position)
        self._write_status_file()

    def toggle_bit(self, position):
        self.byte ^= (1 << position)
        self._write_status_file()

    def check_bit(self, position):
        return (self.byte >> position) & 1