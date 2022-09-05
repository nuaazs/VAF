from phone import Phone

def phone_info(phoneNum):
    info = Phone().find(phoneNum)
    if info == None:
        return {}
    return info