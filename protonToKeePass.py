import gnupg
import pykeepass
from getpass import getpass
import json
import os
from datetime import datetime

def emptyPassWarning():
  passphrase = ""
  ignoreWarning = False
  while passphrase == "" and not ignoreWarning:
    print("WARNING: You have entered an empty passphrase. This is strongly not recommended!")
    ignoreWarning = input("Continue? (y/n): ") or False
    if not ignoreWarning:
      passphrase = getpass("Password for new KDBX: ")
  return passphrase

gnupath = input("Enter path to GnuPG/PGP binary (default: /usr/bin/gpg): ") or "/usr/bin/gpg"
gpg = gnupg.GPG(gnupath)

filepath = input("Enter path to encrypted file: ") or "dummy_proton_export.json.gpg"
passphrase = getpass("Enter passphrase for encrypted file: ") or " "

decrypted_file = gpg.decrypt_file(filepath, passphrase=passphrase)

if decrypted_file.status == "bad passphrase" or decrypted_file.status == "decryption failed":
  print(f"   GnuPG Status: {decrypted_file.status}")
  print("   Error: Possible bad passphrase, try again.")
  exit()

converted_json_string = decrypted_file.data.decode("utf-8").replace("'", '"')
data = json.loads(converted_json_string)

outputPath = input("Desired path & filename for output KDBX file (default: ./proton-conversion.kdbx): ") or "./proton-conversion.kdbx"
kdbxPass = getpass("Password for new KDBX: ") or ""

if kdbxPass == "":
  kdbxPass = emptyPassWarning()
mergeVaults = input("Merge vaults into one folder? (default: n) (y/n): ")
separateTOTP = input("Separate your TOTP/2FA into their own file? (default: n) (y/n): ")

kdbx = pykeepass.create_database(outputPath, password=kdbxPass)

group = kdbx.root_group

if separateTOTP == "y":
  separateTOTP = True
  totpOutputPath = input("Desired path for output TOTP KDBX file (default: ./proton-conversion-totp.kdbx): ") or "./proton-conversion-totp.kdbx"
  kdbxTotpPass = getpass("Password for new KDBX (default: same as main file): ") or kdbxPass
  kdbxTotp = pykeepass.create_database(totpOutputPath, password=kdbxTotpPass)
else:
  separateTOTP = False

for (_, vault) in data["vaults"].items():
  if mergeVaults != "y":
    group = kdbx.add_group(kdbx.root_group, vault["name"])
  for item in vault["items"]:
    itemName = item["data"]["metadata"]["name"]
    username = item["data"]["content"].get("username", "")
    password = item["data"]["content"].get("password", "").replace("\\", "\\\\").replace("\"", "\\\"").replace(",", "\\,")
    
    urls = item["data"]["content"].get('urls', "")
    if len(urls) > 0:
      if len(urls) > 1:
        add_urls = urls[1:]
        urls = urls[0]
      else:
        urls = urls[0]
    else:
      urls = ""

    note = item["data"]["metadata"].get("note", "").replace("\n", "\\n").replace("\"", "\\\"")
    totp = item["data"]["content"].get("totpUri", "")
    createTimeISO = datetime.fromtimestamp(item["createTime"]).isoformat()
    modifiedTimeISO = datetime.fromtimestamp(item["modifyTime"]).isoformat()

    print(f"Converting {itemName}...")

    entry = kdbx.add_entry(group, itemName, username, password)
    entry.url = urls
    entry.notes = note
    entry._set_times_property("creation_time", createTimeISO)
    entry._set_times_property("last_modification_time", modifiedTimeISO)
    if totp and not separateTOTP:
      entry.otp = totp

    if 'add_urls' in locals():
      if len(add_urls) > 1:
        entry.set_custom_property("Additional URLs", "\n".join(add_urls))
      else:
        entry.set_custom_property("Additional URLs", add_urls[0])

    if separateTOTP and totp:
      print(f"TOTP found for {itemName}, separating...")
      totpEntry = kdbxTotp.add_entry(group, itemName, username, "")
      totpEntry.otp = totp

kdbx.save()
if separateTOTP:
  kdbxTotp.save()


print(f'Conversion complete! Your file can be found here: {os.path.abspath(outputPath)}')
if separateTOTP:
  print(f'Conversion complete! Your TOTP file can be found here: {os.path.abspath(totpOutputPath)}')