import argparse
import pathlib

# noinspection PyCompatibility
import winreg
from typing import Optional


def register_hkey(appId: str, appName: str, iconPath: Optional[pathlib.Path]):
    if iconPath is not None:  # pragma: no cover
        if not iconPath.exists():
            raise ValueError(f"Could not register the application: File {iconPath} does not exist")
        elif iconPath.suffix != ".ico":
            raise ValueError(f"Could not register the application: File {iconPath} must be of type .ico")

    winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
    keyPath = f"SOFTWARE\\Classes\\AppUserModelId\\{appId}"
    with winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, keyPath) as masterKey:
        winreg.SetValueEx(masterKey, "DisplayName", 0, winreg.REG_SZ, appName)
        if iconPath is not None:  # pragma: no cover
            winreg.SetValueEx(masterKey, "IconUri", 0, winreg.REG_SZ, str(iconPath.resolve()))


def main():  # pragma: no cover
    parser = argparse.ArgumentParser(description="Register AUMID in the registry for use in toast notifications")
    parser.add_argument("--app_id", "-a", type=str, required=True, help="Application User Model ID for identification")
    parser.add_argument("--name", "-n", type=str, required=True, help="Display name on notification")
    parser.add_argument("--icon", "-i", type=pathlib.Path, required=False, help="Path to image file for desired icon")
    args = parser.parse_args()

    register_hkey(args.app_id, args.name, args.icon)
    print(f"Successfully registered the application ID '{args.app_id}'")


if __name__ == "__main__":
    main()
