# Proton-To-KeePass
Convert encrypted Proton Pass exports into encrypted KeePass databases (kdbx) for offline password vault backups.

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/Z8Z2O191Z)

## Requirements

You must have **GnuPG** installed to utilize this module.

You can find more information on installing and configuring GnuPG on their website, [gnupg.org](https://www.gnupg.org/).

## Installation
```sh
python3 -m pip install proton_to_keepass
```

## How To Use

Open a terminal window and navigate to where your Proton Pass PGP file is located.

Once in the directory, run
```sh
python3 -m proton_to_keepass
```

You can optionally pass in the file directly via the `-p` flag:

```
python3 -m proton_to_keepass -p this-is-your-file.pgp
```

---

You will be prompted for the following:
- Path to your GnuPG binary
- Path to your encrypted (`.pgp`) Proton Pass export file (if you didn't enter it in the arguments)
- Passkey to the Proton Pass encrypted file in order to decrypt it 
  - *Only decrypted during processing, decrypted contents are never written to filesystem*
- KeePass Database (KDBX) filename
- Target directory to write KDBX
- Passkey for new KDBX directory
- Whether you would like to merge your vaults into one root directory
- Whether you would like to export your TOTP codes to a separate KDBX
  - If you opt to do this, you will be prompted for the following:
    - TOTP KDBX filename
    - Target directory to write TOTP KDBX
    - Passkey for TOTP KDBX

Once all of the necessary information is entered, the Proton Pass file will be decrypted and the entries will be converted and written *directly* into a new KDBX file! No plaintext touching the filesystem!

## Caveats
- KDBX only supports one "main" URL per entry, so additional URLs will be written into a custom field titled "Additional URLs"
- If duplicates are found (e.g. same entry name), they will be added in with a timestamp appended in order to create a unique entry name and preserve any alternate credentials.
- It is technically possible to create KDBX databases without passkeys. ***I strongly advise against this***.

## Reference

### Flags

`-p, --path <path>`

Pass path to `pgp` file directly into script from command line.

---

`-v, --version`

Print the module version.

---

`-vb, --verbose`

Enable extra processing logs to show active progress.