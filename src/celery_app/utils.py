def is_ip_address(ip_address: str) -> bool:
    parts = ip_address.split('.', 3)
    for part in parts:
        try:
            num = int(part)
        except ValueError:
            return False
        else:
            if num > 255:
                return False
    return True
