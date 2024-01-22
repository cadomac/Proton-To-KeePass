import pykeepass
from proton_to_keepass.config import Config

class KeePassManager():
  def __init__(self, config: Config, totp=False):
    self._config = config
    self._output_path = config.output_file_path if not totp else config.totp_output_file_path
    self._output_name = config.output_file_name if not totp else config.totp_output_file_name
    self._passkey = config.output_file_passkey if not totp else config.totp_output_file_passkey
    self._db = pykeepass.create_database(f'{self._output_path}/{self._output_name}', password=self._passkey)
  
  @property
  def root(self):
    return self._db.root_group
  
  def add_entry(self, group, entry):
    try:
      new_entry = self._db.add_entry(group, entry.name, entry.username, entry.password)
    except Exception as e:
      if "already exists" in str(e):
        new_entry = self._db.add_entry(group, f'{entry.name}-{self._config.get_new_timestamp()}', entry.username, entry.password)
      else:
        raise e
    new_entry.url = entry.urls
    new_entry.notes = entry.note
    new_entry._set_times_property("creation_time", entry.createTime)
    new_entry._set_times_property("last_modification_time", entry.modifyTime)
    if entry.totp:
      new_entry.otp = entry.totp
    if entry.add_urls:
      if len(entry.add_urls) > 1:
        new_entry.set_custom_property("Additional URLs", "\n".join(entry.add_urls))
      else:
        new_entry.set_custom_property("Additional URLs", entry.add_urls[0])

  def create_group(self, group_name):
    return self._db.add_group(self.root, group_name)

  def save(self):
    self._db.save()