from proton_to_keepass.converter import Converter
from proton_to_keepass.kp_manager import KeePassManager
from getpass import getpass
import os

gnupath = input("Enter path to GnuPG/PGP binary (default: /usr/bin/gpg): ") or "/usr/bin/gpg"
filepath = input("Enter path to encrypted file: ")
passphrase = getpass("Enter passphrase for encrypted file: ")
outputPath = input("Desired path & filename for output KDBX file (default: ./proton-conversion.kdbx): ") or "./proton-conversion.kdbx"
kdbxPass = getpass("Password for new KDBX: ") or ""
mergeVaults = input("Merge vaults into root folder? (default: n) (y/n): ")
separateTOTP = input("Separate your TOTP/2FA into their own file? (default: n) (y/n): ") or False

keepManager = KeePassManager(outputPath, kdbxPass)
if separateTOTP == "y":
  separateTOTP = True
  totpOutputPath = input("Desired path for output TOTP KDBX file (default: ./proton-conversion-totp.kdbx): ") or "./proton-conversion-totp.kdbx"
  kdbxTotpPass = getpass("Password for TOTP KDBX (default: same as main file): ") or kdbxPass
  keepManagerTotp = KeePassManager(totpOutputPath, kdbxTotpPass)
converter = Converter(filepath, passphrase, gnupath)

converter.decrypt_convert_file()

for (_, vault) in converter.vaults:
  if mergeVaults != "y":
    group = keepManager.create_group(vault["name"])
  for item in vault["items"]:
    entry = converter.create_entry(item)
    keepManager.add_entry(group, entry)
    print(f"   Converted {entry.name}!")

    if separateTOTP and entry.totp:
      keepManagerTotp.add_entry(entry)
      print(f"   Separated {entry.name} TOTP!")

keepManager.save()
if separateTOTP:
  keepManagerTotp.save()

print(f"   Successfully converted {len(converter.vaults)} vaults!")
print(f"   Saved to {os.path.abspath(outputPath)}!")