from binascii import unhexlify

def tlv(tag: str, value: str) -> str:
    length = f"{len(value):02d}"
    return f"{tag}{length}{value}"

def crc16_ccitt(data: bytes, poly=0x1021, init=0xFFFF) -> int:
    crc = init
    for b in data:
        crc ^= b << 8
        for _ in range(8):
            if (crc & 0x8000) != 0:
                crc = (crc << 1) ^ poly
            else:
                crc <<= 1
            crc &= 0xFFFF
    return crc

def build_emvco_dynamic(payload_dict: dict) -> str:
    """
    payload_dict espera chaves mínimas:
      - merchant_name, city, country='MZ', currency='943', amount (str), merchant_account (str), ref (str)
    """
    items = []
    items.append(tlv("00", "01"))   # format
    items.append(tlv("01", "12"))   # dynamic QR

    # Merchant Account Information (usamos ID 26 com sub-tags 00=GUI,01=MerchantAccount,02=Ref)
    mai = tlv("00", "EMVCO") + tlv("01", payload_dict["merchant_account"]) + tlv("02", payload_dict["ref"])
    items.append(tlv("26", mai))

    items.append(tlv("52", payload_dict.get("mcc","5399")))  # MCC genérico
    items.append(tlv("53", payload_dict.get("currency","943")))
    items.append(tlv("54", payload_dict["amount"]))
    items.append(tlv("58", payload_dict.get("country","MZ")))
    items.append(tlv("59", payload_dict["merchant_name"][:25]))
    items.append(tlv("60", payload_dict["city"][:15]))

    # Additional Data Field Template (62): 05=Reference (intent_id), 07=Terminal ID
    adf = tlv("05", payload_dict["ref"]) + tlv("07", payload_dict.get("tid","T01"))
    items.append(tlv("62", adf))

    # CRC placeholder
    partial = "".join(items) + "6304"
    crc = crc16_ccitt(partial.encode("utf-8"))
    items.append(tlv("63", f"{crc:04X}"))

    return "".join(items)
