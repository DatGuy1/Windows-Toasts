import argparse
import pathlib
import winreg


def _aumid_key_path(appId: str) -> str:
    return f"SOFTWARE\\Classes\\AppUserModelId\\{appId}"


def register_hkey(appId: str, appName: str, iconPath: pathlib.Path | None) -> None:
    """
    Register an AUMID for the current user

    :param appId: The AUMID
    :param appName: The name toasts show for the app
    :param iconPath: An .ico file for toasts to show
    """
    if iconPath is not None:
        if not iconPath.exists():
            raise ValueError(f"Could not register the application: File {iconPath} does not exist")
        if iconPath.suffix != ".ico":
            raise ValueError(f"Could not register the application: File {iconPath} must be of type .ico")

    winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
    with winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, _aumid_key_path(appId)) as masterKey:
        winreg.SetValueEx(masterKey, "DisplayName", 0, winreg.REG_SZ, appName)
        if iconPath is not None:
            winreg.SetValueEx(masterKey, "IconUri", 0, winreg.REG_SZ, str(iconPath.resolve()))


def _delete_key(keyPath: str) -> None:
    """
    Delete a key of the current user's and everything under it, if it exists
    """
    try:
        with winreg.OpenKeyEx(winreg.HKEY_CURRENT_USER, keyPath) as key:
            subkeys = [winreg.EnumKey(key, i) for i in range(winreg.QueryInfoKey(key)[0])]
    except FileNotFoundError:
        return

    for subkey in subkeys:
        _delete_key(f"{keyPath}\\{subkey}")
    winreg.DeleteKey(winreg.HKEY_CURRENT_USER, keyPath)


def unregister_hkey(appId: str) -> None:
    """
    Remove an AUMID. Does nothing if the AUMID isn't registered
    """
    _delete_key(_aumid_key_path(appId))


def main() -> None:
    parser = argparse.ArgumentParser(description="Register AUMID in the registry for use in toast notifications")
    parser.add_argument("--app_id", "-a", type=str, required=True, help="Application User Model ID for identification")
    nameOrRemove = parser.add_mutually_exclusive_group(required=True)
    nameOrRemove.add_argument("--name", "-n", type=str, help="Display name on notification")
    nameOrRemove.add_argument("--remove", action="store_true", help="Remove the AUMID instead")
    parser.add_argument("--icon", "-i", type=pathlib.Path, required=False, help="Path to image file for desired icon")
    args = parser.parse_args()

    if args.remove and args.icon is not None:
        parser.error("--remove can't be used with --icon")
    if args.remove:
        unregister_hkey(args.app_id)
        print(f"Successfully removed the application ID '{args.app_id}'")
        return

    register_hkey(args.app_id, args.name, args.icon)
    print(f"Successfully registered the application ID '{args.app_id}'")


if __name__ == "__main__":
    main()
