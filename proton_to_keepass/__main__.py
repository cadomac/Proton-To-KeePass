from proton_to_keepass.converter import Converter
from proton_to_keepass.kp_manager import KeePassManager
from proton_to_keepass.config import Config
import os
import sys

config = Config(sys.argv)

converter = Converter(config)
converter.decrypt_file_to_json()

keepManager = KeePassManager(config)

if config.separate_totp:
  keepManagerTotp = KeePassManager(config)

group = keepManager.root
for (_, vault) in converter.vaults:
  if config.verbose:
    print(f"   Opening {vault['name']}...")
  if config.merge_vaults != "y":
    group = keepManager.create_group(vault["name"])
  for item in vault["items"]:
    entry = converter.create_entry(item)
    keepManager.add_entry(group, entry)
    if config.verbose:
      print(f"   Converted {entry.name}!")

    if config.separate_totp and entry.totp:
      keepManagerTotp.add_entry(entry)
      if config.verbose:
        print(f"   Separated {entry.name} TOTP!")

keepManager.save()
if config.separate_totp:
  keepManagerTotp.save()

print(f"   Successfully converted {len(converter.vaults)} vaults!")
print(f"   Saved to {os.path.abspath(f'{config.output_file_path}/{config.output_file_name}')}!")

if config.separate_totp:
  print(f"   Saved TOTP to {os.path.abspath(f'{config.totp_output_file_path}/{config.totp_output_file_name}')}!")