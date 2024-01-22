import gnupg
import json
from datetime import datetime
from proton_to_keepass.entry import Entry

class Converter():
  def __init__ (self, filepath, passphrase, gpg_path):
    self.gpg = gnupg.GPG(gpg_path)
    self.filepath = filepath
    self.passphrase = passphrase
    self.decrypted_file = None
    self.vaults = None
  
  def decrypt_convert_file(self):
    self.decrypted_file = self.gpg.decrypt_file(self.filepath, passphrase=self.passphrase)
    if self.decrypted_file.status == "bad passphrase" or self.decrypted_file.status == "decryption failed":
      print(f"   GnuPG Status: {self.decrypted_file.status}")
      print("   Error: Possible bad passphrase, try again.")
      exit()

    self.decrypted_file = json.loads(self.decrypted_file.data.decode("utf-8").replace("'", '"'))
    self.vaults = self.decrypted_file["vaults"].items()

  def create_entry(self, entry):
    return Entry(entry)

  