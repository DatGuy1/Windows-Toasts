import shutil

import pytest


def test_register_hkey_icon(example_image_path):
    from src.windows_toasts.register_hkey_aumid import register_hkey

    appId = "Test.Notification"
    appName = "Notification Test"

    with pytest.raises(ValueError, match="does not exist"):
        register_hkey(appId, appName, example_image_path.with_suffix(".nonexistant"))
    with pytest.raises(ValueError, match=r"must be of type \.ico"):
        register_hkey(appId, appName, example_image_path)

    exampleIcoPath = example_image_path.with_suffix(".ico")
    shutil.copy(example_image_path, exampleIcoPath)
    pathExists = exampleIcoPath.exists()
    register_hkey(appId, appName, exampleIcoPath if pathExists else None)

    import winreg

    winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
    keyPath = f"SOFTWARE\\Classes\\AppUserModelId\\{appId}"
    with winreg.OpenKeyEx(winreg.HKEY_CURRENT_USER, keyPath) as masterKey:
        displayValue = winreg.QueryValueEx(masterKey, "DisplayName")
        assert displayValue[1] == winreg.REG_SZ
        assert displayValue[0] == appName

        if pathExists:
            iconUri = winreg.QueryValueEx(masterKey, "IconUri")
            assert iconUri[1] == winreg.REG_SZ
            assert iconUri[0] == str(exampleIcoPath)
        else:
            with pytest.raises(FileNotFoundError):
                winreg.QueryValueEx(masterKey, "IconUri")

        winreg.DeleteKeyEx(winreg.HKEY_CURRENT_USER, keyPath)
        with pytest.raises(OSError, match="WinError 1018"):
            winreg.QueryInfoKey(masterKey)

    exampleIcoPath.unlink()


def test_register_hkey_no_icon():
    from src.windows_toasts.register_hkey_aumid import register_hkey

    appId = "Test.Notification"
    appName = "Notification Test"

    register_hkey(appId, appName, None)

    import winreg

    winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
    keyPath = f"SOFTWARE\\Classes\\AppUserModelId\\{appId}"
    with winreg.OpenKeyEx(winreg.HKEY_CURRENT_USER, keyPath) as masterKey:
        displayValue = winreg.QueryValueEx(masterKey, "DisplayName")
        assert displayValue[1] == winreg.REG_SZ
        assert displayValue[0] == appName

        with pytest.raises(FileNotFoundError):
            winreg.QueryValueEx(masterKey, "IconUri")

        winreg.DeleteKeyEx(winreg.HKEY_CURRENT_USER, keyPath)
        with pytest.raises(OSError, match="WinError 1018"):
            winreg.QueryInfoKey(masterKey)


def test_unregister_hkey():
    import winreg

    from src.windows_toasts.register_hkey_aumid import register_hkey, unregister_hkey

    appId = "Test.Notification.Remove"
    keyPath = f"SOFTWARE\\Classes\\AppUserModelId\\{appId}"
    register_hkey(appId, "Notification Test", None)
    # Keys something else added under it are removed too
    winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, f"{keyPath}\\Nested\\Deeper").Close()

    unregister_hkey(appId)
    with pytest.raises(FileNotFoundError):
        winreg.OpenKeyEx(winreg.HKEY_CURRENT_USER, keyPath)
    # Removing an AUMID that isn't registered does nothing
    unregister_hkey(appId)


def test_command_line(monkeypatch: pytest.MonkeyPatch, capsys):
    import sys
    import winreg

    from src.windows_toasts.register_hkey_aumid import main, unregister_hkey

    appId = "Test.Notification.CommandLine"
    keyPath = f"SOFTWARE\\Classes\\AppUserModelId\\{appId}"

    def run(*arguments: str) -> str:
        monkeypatch.setattr(sys, "argv", ["register_hkey_aumid", "--app_id", appId, *arguments])
        main()
        return capsys.readouterr().out

    try:
        assert "registered" in run("--name", "Notification Test")
        winreg.OpenKeyEx(winreg.HKEY_CURRENT_USER, keyPath).Close()

        assert "removed" in run("--remove")
        with pytest.raises(FileNotFoundError):
            winreg.OpenKeyEx(winreg.HKEY_CURRENT_USER, keyPath)
    finally:
        unregister_hkey(appId)

    # Either a name or --remove is needed, but not both, and --remove takes nothing else
    for arguments in ((), ("--name", "Notification Test", "--remove"), ("--remove", "--icon", "icon.ico")):
        with pytest.raises(SystemExit):
            run(*arguments)
