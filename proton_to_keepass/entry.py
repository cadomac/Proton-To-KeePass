from datetime import datetime

class Entry():
  def __init__(self, entry):
    data = entry["data"]
    metadata = data["metadata"]
    content = data["content"]
    self._name = metadata["name"]
    self._username = content.get("username", "")
    self._password = content.get("password", "").replace("\\", "\\\\").replace("\"", "\\\"").replace(",", "\\,")
    self._urls = ""
    self._add_urls = None
    self._note = metadata.get("note", "").replace("\n", "\\n").replace("\"", "\\\"")
    self._totp = content.get("totpUri", "")
    self._createTime = datetime.fromtimestamp(entry["createTime"]).isoformat()
    self._modifyTime = datetime.fromtimestamp(entry["modifyTime"]).isoformat()

    urls = content.get('urls', "")
    if len(urls) > 0:
      if len(urls) > 1:
        self._add_urls = urls[1:]
        self._urls = urls[0]
      else:
        self._urls = urls[0]

  @property
  def name(self) -> str:
    return self._name
  
  @name.setter
  def name(self, value):
    self._name = value
  
  @property
  def username(self):
    return self._username
  
  @property
  def password(self):
    return self._password
  
  @property
  def urls(self):
    return self._urls 
  
  @property
  def add_urls(self):
    return self._add_urls
  
  @property
  def note(self):
    return self._note
  
  @property
  def totp(self):
    return self._totp
  
  @property
  def createTime(self):
    return self._createTime
  
  @property
  def modifyTime(self):
    return self._modifyTime
    