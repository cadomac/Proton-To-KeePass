import pykeepass

class KeePassManager():
  def __init__(self, db_file, db_pass):
    self._db = pykeepass.create_database(db_file, db_pass)

  @property
  def database(self):
    return self._db
  
  @property
  def root(self):
    return self._db.root_group
  
  def add_entry(self, group, entry):
    new_entry = self._db.add_entry(group, entry.name, entry.username, entry.password)
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