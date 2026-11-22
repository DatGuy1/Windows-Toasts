import argparse
import pathlib
import sys
import uuid
import winreg

from ._version import __url__

# Activator CLSIDs are derived from the AUMID, so registering the same AUMID again reuses its CLSID, and toasters can
# tell the activators register_hkey registered from other programs'. Changing __url__ changes them
_ACTIVATOR_NAMESPACE = uuid.uuid5(uuid.NAMESPACE_URL, __url__)
_ACTIVATOR_SUFFIXES = (".py", ".pyw", ".exe")


def _aumid_key_path(appId: str) -> str:
    return f"SOFTWARE\\Classes\\AppUserModelId\\{appId}"


def _clsid_string(clsid: uuid.UUID) -> str:
    """
    A CLSID the way Windows writes them, in upper case and braces
    """
    return f"{{{clsid}}}".upper()


def _clsid_key_path(clsid: uuid.UUID) -> str:
    return f"SOFTWARE\\Classes\\CLSID\\{_clsid_string(clsid)}"


def activator_clsid(appId: str) -> uuid.UUID:
    """
    The CLSID :func:`register_hkey` registers an AUMID's activator under
    """
    return uuid.uuid5(_ACTIVATOR_NAMESPACE, appId)


def _activator_command(activatorPath: pathlib.Path) -> str:
    """
    The command for Windows to run to deliver an activation while no process is listening for it. Windows adds
    -Embedding
    """
    if not activatorPath.is_file():
        raise ValueError(f"Could not register the activator: File {activatorPath} does not exist")
    if activatorPath.suffix.lower() not in _ACTIVATOR_SUFFIXES:
        raise ValueError(
            f"Could not register the activator: File {activatorPath} must be of type {', '.join(_ACTIVATOR_SUFFIXES)}"
        )

    activatorPath = activatorPath.resolve()
    if activatorPath.suffix.lower() == ".exe":
        return f'"{activatorPath}"'

    # Use pythonw to avoid opening a console window
    interpreter = pathlib.Path(sys.executable)
    windowedInterpreter = interpreter.with_name("pythonw.exe")
    if windowedInterpreter.exists():
        interpreter = windowedInterpreter

    return f'"{interpreter}" "{activatorPath}"'


def read_activator_clsid(appId: str) -> uuid.UUID | None:
    """
    The CLSID of the activator registered for an AUMID

    :return: None if the AUMID has no activator registered
    """
    try:
        with winreg.OpenKeyEx(winreg.HKEY_CURRENT_USER, _aumid_key_path(appId)) as aumidKey:
            value, valueType = winreg.QueryValueEx(aumidKey, "CustomActivator")
    except FileNotFoundError:
        return None

    if valueType != winreg.REG_SZ:
        return None

    try:
        return uuid.UUID(value)
    except ValueError:
        return None


def register_hkey(
    appId: str, appName: str, iconPath: pathlib.Path | None = None, activator: bool | pathlib.Path = False
) -> None:
    """
    Register an AUMID for the current user

    :param appId: The AUMID
    :param appName: The name toasts show for the app
    :param iconPath: An .ico file for toasts to show
    :param activator: True to register an activator, so that clicks on toasts from earlier runs and on background
        buttons also reach your script. Removes the command a file registered before. See :ref:`register-activator`.

        Pass a .py, .pyw or .exe file instead to also have Windows start it when one of the AUMID's toasts is clicked
        while nothing is listening for it; see :ref:`activation-after-exit`. This stores the command to start it in the
        registry, and Windows runs that command itself, adding ``-Embedding``. A script is started with the Python
        that's running this, using ``pythonw.exe`` if there is one, so the command stops working if that Python moves.

        False, the default, leaves any activator the AUMID already has as-is
    """
    if iconPath is not None:
        if not iconPath.exists():
            raise ValueError(f"Could not register the application: File {iconPath} does not exist")
        if iconPath.suffix != ".ico":
            raise ValueError(f"Could not register the application: File {iconPath} must be of type .ico")

    activatorCommand = None if isinstance(activator, bool) else _activator_command(pathlib.Path(activator))

    winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
    with winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, _aumid_key_path(appId)) as masterKey:
        winreg.SetValueEx(masterKey, "DisplayName", 0, winreg.REG_SZ, appName)
        if iconPath is not None:
            winreg.SetValueEx(masterKey, "IconUri", 0, winreg.REG_SZ, str(iconPath.resolve()))

        if activator is False:
            return

        clsid = activator_clsid(appId)
        if activatorCommand is None:
            _delete_activator_keys(clsid)
        else:
            with winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, f"{_clsid_key_path(clsid)}\\LocalServer32") as serverKey:
                winreg.SetValueEx(serverKey, "", 0, winreg.REG_SZ, activatorCommand)

        winreg.SetValueEx(masterKey, "CustomActivator", 0, winreg.REG_SZ, _clsid_string(clsid))


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


def _delete_activator_keys(clsid: uuid.UUID) -> None:
    _delete_key(_clsid_key_path(clsid))


def unregister_hkey(appId: str) -> None:
    """
    Remove an AUMID, along with the activator :func:`register_hkey` registered for it. An activator another program
    registered is left in place. Does nothing if the AUMID isn't registered
    """
    clsid = activator_clsid(appId)
    # Exclude activators not from us
    if read_activator_clsid(appId) == clsid:
        _delete_activator_keys(clsid)

    _delete_key(_aumid_key_path(appId))


def main() -> None:
    parser = argparse.ArgumentParser(description="Register AUMID in the registry for use in toast notifications")
    parser.add_argument("--app_id", "-a", type=str, required=True, help="Application User Model ID for identification")
    nameOrRemove = parser.add_mutually_exclusive_group(required=True)
    nameOrRemove.add_argument("--name", "-n", type=str, help="Display name on notification")
    nameOrRemove.add_argument("--remove", action="store_true", help="Remove the AUMID and its activator instead")
    parser.add_argument("--icon", "-i", type=pathlib.Path, required=False, help="Path to image file for desired icon")
    parser.add_argument(
        "--activator",
        nargs="?",
        const=True,
        default=False,
        type=pathlib.Path,
        metavar="PATH",
        help="Register an activator, so clicks on toasts from earlier runs and on background buttons reach your "
        "running script. Pass a script or executable to also have Windows start it when a toast is clicked while "
        "nothing is listening",
    )
    args = parser.parse_args()

    if args.remove and (args.icon is not None or args.activator is not False):
        parser.error("--remove can't be used with --icon or --activator")
    if args.remove:
        unregister_hkey(args.app_id)
        print(f"Successfully removed the application ID '{args.app_id}'")
        return

    register_hkey(args.app_id, args.name, args.icon, args.activator)
    print(f"Successfully registered the application ID '{args.app_id}'")


if __name__ == "__main__":
    main()
