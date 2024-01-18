import json
import os
from datetime import datetime
path = input("Path to your Proton Pass JSON export (default: ./input.json): ") or "./input.json"
name = input("Desired name of the root folder (default: Vault): ")
outputPath = input("Desired path for output CSV file (default: ./output.csv): ") or "./output.csv"
separateTOTP = input("Separate your TOTP/2FA into their own file? (default: n) (y/n): ")

columnHeaders = [f'"Group"', f'"Title"', f'"Username"', f'"Password"', f'"URL"', f'"Notes"', f'"TOTP"', f'"Icon"', f'"Last Modified"', f'"Created"']

recordDict = {}

if separateTOTP == "y":
  separateTOTP = True
  totp_csv = [columnHeaders]
  totpOutputPath = input("Desired path for output TOTP CSV file (default: ./totp-output.csv): ") or "./totp-output.csv"
else:
  separateTOTP = False

with open(path, "r") as file:
  json_data = json.load(file)

csv_data = [columnHeaders]

def resolveDuplicate(newEntry, onlyTOTP):
  newInfo = False
  newEntryItemName = newEntry[1].replace("\"", "")
  print(f'Found duplicate entry for {newEntryItemName}, attempting to resolve...')
  currentEntry = recordDict[newEntryItemName]
  if onlyTOTP:
    if separateTOTP:
      return
    else:
      currentTOTP = currentEntry[6]
      newTOTP = newEntry[6]
      if currentTOTP == newTOTP:
        return
      elif currentTOTP == '""' and newTOTP != currentTOTP:
        currentEntry[6] = newTOTP
        recordDict[newEntryItemName] = currentEntry
  for i, _ in enumerate(currentEntry):
    if i == 0:
      continue
    newEntryItemSan = newEntry[i].replace("\"", "")
    currentEntryItemSan = currentEntry[i].replace("\"", "")
    if not newEntryItemSan:
      continue
    elif not currentEntryItemSan and newEntryItemSan:
      newInfo = True
      currentEntry[i] = newEntry[i]
    elif newEntryItemSan and currentEntryItemSan:
      if newEntryItemSan != currentEntryItemSan:
        if (columnHeaders[i] == '"Password"' or columnHeaders[i] == '"Username"' or columnHeaders[i] == '"TOTP"'):
          print(f"Separate {columnHeaders[i]} entry found under same name: {newEntryItemName}, creating duplicate entry...")
          print(f"Recommended for review: {newEntryItemName}")
          recordDict[f'{newEntryItemName}-{datetime.timestamp}'] = newEntry
          return
  if newInfo:
    recordDict[newEntryItemName] = currentEntry

for (_, vault) in json_data["vaults"].items():
  for item in vault["items"]:
    itemName = item["data"]["metadata"]["name"]
    if "Alias for" in itemName:
      continue
    username = item["data"]["content"].get("username", "")
    password = item["data"]["content"].get("password", "").replace("\\", "\\\\").replace("\"", "\\\"").replace(",", "\\,")
    urls = item["data"]["content"].get("urls", "")
    if len(urls) > 0:
      if len(urls) > 1:
        urls = ",".join(item["data"]["content"]["urls"])
      else:
        urls = urls[0]
    else:
      urls = ""
    note = item["data"]["metadata"].get("note", "").replace("\n", "\\n").replace("\"", "\\\"")
    totp = item["data"]["content"].get("totpUri", "")
    createTimeISO = datetime.fromtimestamp(item["createTime"]).isoformat()
    modifiedTimeISO = datetime.fromtimestamp(item["modifyTime"]).isoformat()

    onlyTOTP = (not username) and (not password) and (not urls) and (not note) and totp

    print(f"Converting {itemName}...")

    newEntry = [
      f'"{name or "Vault"}"',
      f'"{itemName}"',
      f'"{username}"',
      f'"{password}"',
      f'"{urls}"',
      f'"{note}"',
      f'"{totp if not separateTOTP else ""}"',
      f'"0"',
      f'"{modifiedTimeISO}"',
      f'"{createTimeISO}"'
    ]

    if separateTOTP and totp:
      print(f"TOTP found for {itemName}, separating...")
      totp_csv.append([
        f'"{name or "TOTP"}"',
        f'"{itemName}"',
        f'"{username}"',
        f'""',
        f'"{urls}"',
        f'"{note}"',
        f'"{totp}"',
        f'"0"',
        f'"{modifiedTimeISO}"',
        f'"{createTimeISO}"'
      ])

    if recordDict.get(itemName):
      resolveDuplicate(newEntry, onlyTOTP)
    else:
      if separateTOTP and onlyTOTP:
        continue
      else:
        recordDict[itemName] = newEntry

csv_data_final = [columnHeaders]
for _,v in recordDict.items():
  csv_data_final.append(v)

with open(outputPath, "w", newline="") as file:
  file.write("\n".join([",".join(row) for row in csv_data_final]))

if separateTOTP:
  with open(totpOutputPath, "w", newline="") as file:
    file.write("\n".join([",".join(row) for row in totp_csv]))


print(f'Conversion complete! Your file can be found here: {os.path.abspath(outputPath)}')
if separateTOTP:
  print(f'Conversion complete! Your TOTP file can be found here: {os.path.abspath(totpOutputPath)}')