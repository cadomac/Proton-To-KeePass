import gnupg
import json
import re
import sys
from datetime import datetime
from proton_to_keepass.entry import Entry
from proton_to_keepass.config import Config

class Converter():
  def __init__ (self, config: Config):
    self.gpg = gnupg.GPG(config.gnupg_path)
    self.filepath = config.encrypted_file_path
    self.passphrase = config.encrypted_file_passkey
    self.decrypted_file = None
    self.vaults = None
  
  def decrypt_file_to_json(self):
    self.decrypted_file = self.gpg.decrypt_file(self.filepath, passphrase=self.passphrase)
    if self.decrypted_file.status == "bad passphrase" or self.decrypted_file.status == "decryption failed":
      print(f"   GnuPG Status: {self.decrypted_file.status}")
      print("   Error: Possible bad passphrase, try again.")
      exit()

    self.strip_junk()
    self.decrypted_file = self.decrypted_file.decode("utf-8") + "}"
    self.decrypted_file = json.loads(self.decrypted_file)
    self.vaults = self.decrypted_file["vaults"].items()

  def strip_junk(self):
    front_binaries_pattern = re.compile(rb'}PK.+', flags=re.DOTALL)
    back_binaries_pattern = re.compile(rb'^[^{]*', flags=re.DOTALL)
    self.decrypted_file = re.sub(front_binaries_pattern, b'', re.sub(back_binaries_pattern, b'', self.decrypted_file.data))

  def create_entry(self, entry):
    return Entry(entry)

  