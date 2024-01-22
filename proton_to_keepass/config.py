from proton_to_keepass import __version__
from getpass import getpass
from datetime import datetime
import os

class Config():
  def __init__(self, args):
    self._args = args
    self._cwd = os.getcwd()
    self._gnupath = "/usr/bin/gpg"
    self._verbose = False
    self._encrypted_file_path = ""
    self._encrypted_file_passkey = ""
    self._output_file_path = ""
    self._output_file_name = ""
    self._output_file_passkey = ""
    self._totp_output_file_path = ""
    self._totp_output_file_name = ""
    self._totp_output_file_passkey = ""
    self._timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    self._default_output_file_name = f'./pp_convert_{self._timestamp}.kdbx'
    self._merge_vaults = False
    self._separate_totp = False

    self.parse_args()
    self.gather_input()

  def __str__(self):
    return f"Config(verbose={self.verbose})"
  
  def parse_args(self):
    arg_len = len(self._args)
    if arg_len <= 1:
      return
    
    if self._args[1] == "--version":
      print(f"{__version__}")
      exit()

    if "--path" in self._args or "-p" in self._args:
      self.parse_path("--path" if "--path" in self._args else "-p", arg_len)

    if "--verbose" in self._args or "-v" in self._args:
      self._verbose = True

  def parse_path(self, path_arg, arg_len):
    path_arg_idx = self._args.index(path_arg)

    if arg_len > path_arg_idx + 1:
      self._encrypted_file_path = os.path.abspath(self._args[path_arg_idx + 1].strip())
      
      if not self._encrypted_file_path[-4:].endswith(".gpg") and not self._encrypted_file_path.endswith(".pgp"):
        print("   Error: File must be encrypted with GnuPG/PGP.")
        exit()
    else:
      print("   Error: --path,-p flag requires a path argument.")
      exit()
  
  def empty_input_handler(self, message, err_msg, allow_ignore=False):
    curr_input = ""
    while curr_input == "":
      if allow_ignore:
        ignore = input("   WARNING: You have entered an empty value! This is not recommended for security reasons. Ignore and continue? (y/n): ")
        if ignore == "y":
          break
      else:
        print(f"   {err_msg}")

      curr_input = input(f"{message}: ")
      if curr_input == "":
        print(f"   {err_msg}")
    return curr_input
  
  def gather_input(self):
    self._gnupath = input("Enter path to GnuPG/PGP binary (/usr/bin/gpg): ") or self._gnupath

    self.gather_input_info()
    self.gather_output_info()

    self._merge_vaults = input("Merge vaults into root folder? (default: n) (y/n): ")
    self._separate_totp = input("Separate your TOTP/2FA into their own file? (default: n) (y/n): ") or False

    if self._separate_totp == "y":
      self.separate_totp = True
      self.initialize_totp_db()

  def gather_input_info(self):
    if self._encrypted_file_path != "":
      print(f"   Using file path from --path flag: {self._encrypted_file_path}")
    else:
      while self._encrypted_file_path == "":
        self._encrypted_file_path = input("Enter path to encrypted file: ")
        if self._encrypted_file_path == "":
          self._encrypted_file_path = self.empty_input_handler("Enter path to encrypted file", "Error: No path provided.")

    self._encrypted_file_passkey = getpass("Enter passphrase for encrypted file: ")

  def gather_output_info(self):
    self._output_file_name = input(f"Desired filename for output KDBX file ({self._default_output_file_name}): ") or self._default_output_file_name
    self._output_file_path = input(f"Desired path for output KDBX file ({self._cwd}): ") or self._cwd
    self._output_file_passkey = getpass("Password for new KDBX: ") or ""

    verify_pass = getpass("Enter password again: ") or ""

    while self._output_file_passkey != verify_pass:
      print("   Error: Passwords do not match.")
      verify_pass = getpass("Enter password again: ") or ""

    if self._output_file_passkey == "":
      self._output_file_passkey = self.empty_input_handler("Password for new KDBX", "Error: No password provided.", allow_ignore=True)

  def initialize_totp_db(self):
    default_totp_filename = f"./pp_convert_totp_{self._timestamp}.kdbx"
    self._totp_output_name = input(f"Desired name for output TOTP KDBX file ({default_totp_filename}): ") or default_totp_filename
    self._totp_output_path = input(f"Desired path for output TOTP KDBX file ({self._cwd}): ") or self._cwd
    self._kdbx_totp_pass = getpass("Password for TOTP KDBX (default: same as main file): ") or self._kdbx_pass
    if self._kdbx_totp_pass == self._kdbx_pass:
      diff_pass = input("   Using the same password is not as secure as using different passwords. Use different password? (y/n): ")
      if diff_pass == "y":
        self._kdbx_totp_pass = getpass("Password for TOTP KDBX: ")
        if self._kdbx_totp_pass == "":
          self._kdbx_totp_pass = self.empty_input_handler("Password for TOTP KDBX", "Error: No password provided.", allowIgnore=True)
  
  def get_new_timestamp(self):
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S-%f")[:-3]

  @property
  def gnupg_path(self):
    return self._gnupath

  @property
  def encrypted_file_path(self):
    return self._encrypted_file_path
  
  @encrypted_file_path.setter
  def encrypted_file_path(self, value):
    self._encrypted_file_path = value

  @property
  def output_file_path(self):
    return self._output_file_path
  
  @property
  def output_file_name(self):
    return self._output_file_name
  
  @property
  def output_file_passkey(self):
    return self._output_file_passkey
  
  @property
  def timestamp(self):
    return self._timestamp
  
  @property
  def totp_output_path(self):
    return self._totp_output_path
  
  @property
  def totp_output_name(self):
    return self._totp_output_name
  
  @property
  def totp_output_passkey(self):
    return self._totp_output_passkey

  @property
  def encrypted_file_passkey(self):
    return self._encrypted_file_passkey
  
  @property
  def merge_vaults(self):
    return self._merge_vaults

  @property
  def separate_totp(self):
    return self._separate_totp

  @property
  def verbose(self):
    return self._verbose
  
  @verbose.setter
  def verbose(self, value):
    self._verbose = value