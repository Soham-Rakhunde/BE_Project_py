from encrypt_module.encryptor import EncryptionService

if __name__ == "__main__":
    cipher = EncryptionService.encrypt(b'datawedQDSDQWDSaWDQWDASDDf DfWDQvDasdSAD W')
    print("Decrypt:")
    EncryptionService.decrypt(cipher)