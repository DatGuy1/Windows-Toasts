def test_register_hkey():
    import ctypes
    if ctypes.windll.shell32.IsUserAnAdmin() == 0:
        return

    from scripts.register_hkey_aumi import register_hkey
    appId = "Test.Notification"
    appName = "Notification Test"
    register_hkey(appId, appName, None)

    # noinspection PyCompatibility
    import winreg
    winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
    keyPath = f"SOFTWARE\\Classes\\AppUserModelId\\{appId}"
    with winreg.OpenKeyEx(winreg.HKEY_LOCAL_MACHINE, keyPath) as masterKey:
        displayValue = winreg.QueryValueEx(masterKey, "DisplayName")
        assert displayValue[1] == winreg.REG_SZ
        assert displayValue[0] == appName

        try:
            winreg.QueryValueEx(masterKey, "IconUri")
            assert False
        except FileNotFoundError:
            pass

        winreg.DeleteKeyEx(winreg.HKEY_LOCAL_MACHINE, keyPath)
        try:
            winreg.QueryInfoKey(masterKey)
            assert False
        except (FileNotFoundError, OSError):
            pass


# noinspection PyUnresolvedReferences
def test_create_shell_link():
    import pythoncom
    from pywintypes import IID
    from win32com.propsys import propsys
    from win32com.shell import shell
    from win32com.storagecon import STGM_READ
    from win32typing import PyIPersistFile, PyIShellLink

    from scripts.create_shell_link import create_shell_link
    appId = "Test.Notification"
    appName = "Notification Test"
    create_shell_link(appId, appName)

    import os
    from pathlib import Path
    linkPath = Path(os.getenv("APPDATA")) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / f"{appName}.lnk"
    assert linkPath.exists()

    # noinspection PyTypeChecker
    shellLink: PyIShellLink = pythoncom.CoCreateInstance(
        shell.CLSID_ShellLink,
        None,
        pythoncom.CLSCTX_INPROC_SERVER,
        shell.IID_IShellLink,
    )
    persistFile: PyIPersistFile = shellLink.QueryInterface(pythoncom.IID_IPersistFile)
    persistFile.Load(str(linkPath), STGM_READ)
    shellLink.Resolve(0, shell.SLR_ANY_MATCH | shell.SLR_NO_UI)

    # noinspection PyArgumentList
    assert shellLink.GetPath(shell.SLGP_SHORTPATH)[0] == ""
    assert shellLink.GetArguments() == ""
    assert shellLink.GetWorkingDirectory() == ""
    # noinspection PyArgumentList
    assert shellLink.GetIconLocation() == ("", 0)

    propertyStore = shellLink.QueryInterface(propsys.IID_IPropertyStore)
    assert propertyStore.GetCount() == 1
    propertyKey = propsys.PSGetPropertyKeyFromName("System.AppUserModel.ID")
    assert propertyKey == (IID("{9F4C2855-9F79-4B39-A8D0-E1D42DE1D5F3}"), 5)
    assert propertyStore.GetValue(propertyKey).ToString() == "Test.Notification"

    linkPath.unlink()
    assert linkPath.exists() is False
