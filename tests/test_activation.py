import ctypes
import datetime
import subprocess
import sys
import threading
import uuid
import winreg
from collections.abc import Iterator
from pathlib import Path

import pytest

from src.windows_toasts import (
    InteractableWindowsToaster,
    Toast,
    ToastActivatedEventArgs,
    ToastButton,
    ToastSystemButton,
    ToastSystemButtonAction,
    _com_server,
    activation,
    launched_by_toast,
)
from src.windows_toasts.events import _decode_arguments, _encode_arguments
from src.windows_toasts.register_hkey_aumid import (
    activator_clsid,
    main,
    read_activator_clsid,
    register_hkey,
    unregister_hkey,
)
from src.windows_toasts.toast_document import ToastDocument

TEST_AUMID = "WindowsToasts.Tests.Activator"


def _activate(clsid: uuid.UUID, arguments: str, inputs: dict[str, str]) -> None:
    """
    Call an activator the way Windows does, through COM
    """
    # Already initialised is fine, so this doesn't raise
    ctypes.windll.ole32.CoInitializeEx(None, 0)
    callback = ctypes.c_void_p()
    ctypes.OleDLL("ole32").CoCreateInstance(
        ctypes.byref(_com_server._GUID.from_uuid(clsid)),
        None,
        _com_server._CLSCTX_LOCAL_SERVER,
        ctypes.byref(_com_server._GUID.from_buffer_copy(_com_server._IID_INOTIFICATIONACTIVATIONCALLBACK)),
        ctypes.byref(callback),
    )
    vtable = ctypes.cast(ctypes.cast(callback, ctypes.POINTER(ctypes.c_void_p))[0], ctypes.POINTER(ctypes.c_void_p))
    data = (_com_server._NotificationUserInputData * len(inputs))(
        *(_com_server._NotificationUserInputData(key, value) for key, value in inputs.items())
    )
    # Activate is after IUnknown's three methods
    assert _com_server._Activate(vtable[3])(callback, TEST_AUMID, arguments, data, len(inputs)) == 0
    # Release
    _com_server._AddRefOrRelease(vtable[2])(callback)


@pytest.fixture
def activator_aumid(tmp_path: Path) -> Iterator[str]:
    script = tmp_path / "activator.py"
    script.touch()
    register_hkey(TEST_AUMID, "Activator test", None, script)
    yield TEST_AUMID

    _com_server.stop_server(activator_clsid(TEST_AUMID))
    activation._dispatchers.clear()
    unregister_hkey(TEST_AUMID)


def test_activator_clsid_is_stable():
    # Activators registered by earlier versions must keep the same CLSID, or toasters would ignore them
    assert activator_clsid(TEST_AUMID) == uuid.UUID("d4d1fb55-01a7-54a9-9e2e-9a5f94d4a43e")


def test_register_activator(tmp_path: Path):
    script = tmp_path / "activator.py"
    script.touch()
    executable = tmp_path / "activator.exe"
    executable.touch()

    with pytest.raises(ValueError, match="does not exist"):
        register_hkey(TEST_AUMID, "Activator test", None, tmp_path / "missing.py")
    wrongType = tmp_path / "activator.txt"
    wrongType.touch()
    with pytest.raises(ValueError, match="must be of type"):
        register_hkey(TEST_AUMID, "Activator test", None, wrongType)

    clsid = activator_clsid(TEST_AUMID)
    serverKeyPath = f"SOFTWARE\\Classes\\CLSID\\{{{str(clsid).upper()}}}\\LocalServer32"
    try:
        register_hkey(TEST_AUMID, "Activator test", None, script)
        assert read_activator_clsid(TEST_AUMID) == clsid
        with winreg.OpenKeyEx(winreg.HKEY_CURRENT_USER, serverKeyPath) as serverKey:
            command = winreg.QueryValueEx(serverKey, "")[0]
        interpreter = Path(sys.executable).with_name("pythonw.exe")
        if not interpreter.exists():
            interpreter = Path(sys.executable)
        assert command == f'"{interpreter}" "{script.resolve()}"'

        # Registering again keeps the CLSID
        register_hkey(TEST_AUMID, "Activator test", None, executable)
        assert read_activator_clsid(TEST_AUMID) == clsid
        with winreg.OpenKeyEx(winreg.HKEY_CURRENT_USER, serverKeyPath) as serverKey:
            assert winreg.QueryValueEx(serverKey, "")[0] == f'"{executable.resolve()}"'
    finally:
        unregister_hkey(TEST_AUMID)

    assert read_activator_clsid(TEST_AUMID) is None
    with pytest.raises(FileNotFoundError):
        winreg.OpenKeyEx(winreg.HKEY_CURRENT_USER, serverKeyPath)

    # Removing an AUMID that isn't registered does nothing
    unregister_hkey(TEST_AUMID)


def test_unregister_keeps_other_activators():
    otherClsid = uuid.uuid4()
    otherKeyPath = f"SOFTWARE\\Classes\\CLSID\\{{{otherClsid}}}\\LocalServer32"
    register_hkey(TEST_AUMID, "Activator test")
    with winreg.OpenKeyEx(
        winreg.HKEY_CURRENT_USER, f"SOFTWARE\\Classes\\AppUserModelId\\{TEST_AUMID}", access=winreg.KEY_SET_VALUE
    ) as aumidKey:
        winreg.SetValueEx(aumidKey, "CustomActivator", 0, winreg.REG_SZ, f"{{{otherClsid}}}")
    winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, otherKeyPath).Close()

    try:
        assert read_activator_clsid(TEST_AUMID) == otherClsid
        # Toasters leave another program's activator to it
        toaster = InteractableWindowsToaster("Python", TEST_AUMID)
        with pytest.raises(ValueError, match="no activator registered"):
            toaster.on_activated = print
        assert toaster._activation_dispatcher() is None
        assert otherClsid not in _com_server._serversByClsid

        unregister_hkey(TEST_AUMID)
        assert read_activator_clsid(TEST_AUMID) is None
        # Another program's activator is left alone
        winreg.OpenKeyEx(winreg.HKEY_CURRENT_USER, otherKeyPath).Close()
    finally:
        winreg.DeleteKey(winreg.HKEY_CURRENT_USER, otherKeyPath)
        winreg.DeleteKey(winreg.HKEY_CURRENT_USER, otherKeyPath.rsplit("\\", 1)[0])


def test_unreadable_activator_clsid():
    keyPath = f"SOFTWARE\\Classes\\AppUserModelId\\{TEST_AUMID}"
    try:
        for value, valueType in (("not a guid", winreg.REG_SZ), (1, winreg.REG_DWORD)):
            with winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, keyPath) as aumidKey:
                winreg.SetValueEx(aumidKey, "CustomActivator", 0, valueType, value)
            assert read_activator_clsid(TEST_AUMID) is None
    finally:
        unregister_hkey(TEST_AUMID)


def test_arguments_encoding():
    for tag, group, arguments in (("tag", None, "action=reply"), ("t", "g", ""), ("ü", "\"'", "windows_toasts:")):
        assert _decode_arguments(_encode_arguments(tag, group, arguments)) == (tag, group, arguments)

    # Arguments from toasts shown without an activator, or that only look encoded, are passed on as they are
    for arguments in ("action=reply", "", "windows_toasts:", "windows_toasts:[1,null,2]", "windows_toasts:{"):
        assert _decode_arguments(arguments) == (None, None, arguments)


def test_activation_tags():
    toast = Toast(["Hello"], tag="tag", group="group")
    toast.AddAction(ToastButton("Reply", "action=reply"))
    toast.AddAction(ToastButton("Website", launch="https://example.com"))
    toast.AddAction(ToastSystemButton(ToastSystemButtonAction.Dismiss))

    document = ToastDocument(toast)
    toastNode = document.GetElementByTagName("toast")
    document.SetAttribute(toastNode, "launch", "tag")
    for action in toast.actions:
        document.AddAction(action)
    document.AddActivationTags(toast)

    assert _decode_arguments(document.GetAttributeValue(toastNode, "launch")) == ("tag", "group", "tag")
    actions = document.xmlDocument.get_elements_by_tag_name("action")
    assert _decode_arguments(document.GetAttributeValue(actions.item(0), "arguments")) == (
        "tag",
        "group",
        "action=reply",
    )
    # Protocol and system activations don't reach the activator
    assert document.GetAttributeValue(actions.item(1), "arguments") == "https://example.com"
    assert document.GetAttributeValue(actions.item(2), "arguments") == "dismiss"

    # A toast that launches a protocol keeps its launch as it is
    protocolToast = Toast(["Hello"], launch_action="https://example.com")
    protocolDocument = InteractableWindowsToaster("Python")._setup_toast(protocolToast, True)
    protocolDocument.AddActivationTags(protocolToast)
    protocolNode = protocolDocument.GetElementByTagName("toast")
    assert protocolDocument.GetAttributeValue(protocolNode, "launch") == "https://example.com"


def test_on_activated_requires_activator():
    with pytest.raises(ValueError, match="no activator registered"):
        InteractableWindowsToaster("Python").on_activated = print
    with pytest.raises(ValueError, match="no activator registered"):
        InteractableWindowsToaster("Python", "WindowsToasts.Tests.Unregistered").on_activated = print

    toaster = InteractableWindowsToaster("Python")
    toaster.on_activated = None
    assert toaster.on_activated is None


def test_launched_by_toast(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(sys, "argv", ["script.py"])
    assert not launched_by_toast()
    monkeypatch.setattr(sys, "argv", ["script.py", "-Embedding"])
    assert launched_by_toast()


def test_activator_routing(activator_aumid: str):
    clsid = activator_clsid(activator_aumid)
    received: dict[str, ToastActivatedEventArgs] = {}
    activated = threading.Event()

    def recorder(name: str):
        def record(eventArgs: ToastActivatedEventArgs) -> None:
            received[name] = eventArgs
            activated.set()

        return record

    def activate(arguments: str, inputs: dict[str, str]) -> None:
        activated.clear()
        _activate(clsid, arguments, inputs)
        assert activated.wait(5)

    toaster = InteractableWindowsToaster("Python", activator_aumid)
    toaster.on_activated = recorder("toaster")
    toast = Toast(["Hello"], tag="routed", group="group", on_activated=recorder("toast"))
    toast.AddAction(ToastButton("Reply", "action=reply"))
    toaster.show_toast(toast)

    # A toast this process showed gets its own activations
    activate(_encode_arguments("routed", "group", "action=reply"), {"reply": "Hi"})
    assert received.pop("toast") == ToastActivatedEventArgs("action=reply", {"reply": "Hi"}, "routed", "group")

    # Any other toast's go to the toaster, such as one an earlier run of the script showed
    activate(_encode_arguments("earlier", None, "action=reply"), {})
    assert received.pop("toaster") == ToastActivatedEventArgs("action=reply", {}, "earlier", None)
    activate("not encoded", {})
    assert received.pop("toaster") == ToastActivatedEventArgs("not encoded", {}, None, None)

    # Showing a toast with the same tag and group without on_activated replaces the old one's
    toaster.show_toast(Toast(["Replaced"], tag="routed", group="group"))
    activate(_encode_arguments("routed", "group", "action=reply"), {})
    assert received.pop("toaster").tag == "routed"

    # Scheduled toasts' on_activated works through the activator too
    scheduled = Toast(["Later"], tag="scheduled", on_activated=recorder("scheduled"))
    toaster.schedule_toast(scheduled, datetime.datetime.now() + datetime.timedelta(minutes=1))
    activate(_encode_arguments("scheduled", None, "scheduled"), {})
    assert received.pop("scheduled").arguments == "scheduled"
    assert not received


def test_activator_server_restarts(activator_aumid: str):
    clsid = activator_clsid(activator_aumid)
    activated = threading.Event()
    toaster = InteractableWindowsToaster("Python", activator_aumid)
    toaster.on_activated = lambda _: activated.set()

    _com_server.stop_server(clsid)
    # Stopping a server that isn't running does nothing
    _com_server.stop_server(clsid)

    toaster.on_activated = lambda _: activated.set()
    _activate(clsid, "again", {})
    assert activated.wait(5)


@pytest.mark.parametrize("flag", ["_COINIT_MULTITHREADED", "_REGCLS_MULTIPLEUSE"])
def test_activator_server_errors(monkeypatch: pytest.MonkeyPatch, flag: str):
    # COM rejects flags it doesn't know, whether initialising the thread or registering the class
    monkeypatch.setattr(_com_server, flag, 0xFFFF0)
    clsid = uuid.uuid4()
    with pytest.raises(OSError, match="WinError -2147024809"):
        _com_server.start_server(clsid, lambda *_: None)
    assert clsid not in _com_server._serversByClsid


def test_activator_server_unexpected_error(monkeypatch: pytest.MonkeyPatch):
    # Any error on the server's thread reaches the caller, rather than leaving it waiting
    def fail(_):
        raise TypeError("unexpected")

    monkeypatch.setattr(_com_server._GUID, "from_uuid", fail)
    with pytest.raises(TypeError, match="unexpected"):
        _com_server.start_server(uuid.uuid4(), lambda *_: None)


def test_activator_rejects_bad_calls():
    clsid = uuid.uuid4()
    _com_server.start_server(clsid, lambda *_: None)
    try:
        server = _com_server._serversByClsid[clsid]
        factory = ctypes.addressof(server.factoryObject)
        callback = ctypes.addressof(server.callbackObject)
        iid = ctypes.pointer(_com_server._GUID.from_buffer_copy(_com_server._IID_INOTIFICATIONACTIVATIONCALLBACK))
        out = (ctypes.c_void_p * 1)()

        assert _com_server._factory_query_interface(factory, iid, None) == _com_server._E_POINTER
        assert _com_server._create_instance(factory, None, iid, None) == _com_server._E_POINTER
        assert _com_server._create_instance(factory, 1, iid, out) == _com_server._CLASS_E_NOAGGREGATION
        assert out[0] is None
        # An object that isn't one of the servers'
        assert _com_server._create_instance(None, None, iid, out) == _com_server._E_FAIL
        assert _com_server._activate(None, "aumid", "args", None, 0) == _com_server._E_FAIL
        # Input data that can't be read doesn't reach Python as an exception
        assert _com_server._activate(callback, "aumid", "args", None, 1) == _com_server._S_OK
        assert _com_server._activate(callback, "aumid", "args", 1, 1) == _com_server._E_FAIL
        assert _com_server._lock_server(factory, True) == _com_server._S_OK
    finally:
        _com_server.stop_server(clsid)

    # Windows may still hold the stopped server's objects
    assert _com_server._activate(callback, "aumid", "args", None, 0) == _com_server._E_FAIL


def test_activator_stops_at_exit():
    clsid = uuid.uuid4()
    _com_server.start_server(clsid, lambda *_: None)
    _com_server._stop_servers()
    assert clsid not in _com_server._serversByClsid
    # A server that was never started has nothing to stop
    _com_server.ActivatorServer(clsid, lambda *_: None).stop()


def test_activator_without_pythonw(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    interpreter = tmp_path / "python.exe"
    interpreter.touch()
    script = tmp_path / "activator.py"
    script.touch()
    monkeypatch.setattr(sys, "executable", str(interpreter))
    try:
        register_hkey(TEST_AUMID, "Activator test", None, script)
        clsid = activator_clsid(TEST_AUMID)
        serverKeyPath = rf"SOFTWARE\Classes\CLSID\{{{str(clsid).upper()}}}\LocalServer32"
        with winreg.OpenKeyEx(winreg.HKEY_CURRENT_USER, serverKeyPath) as serverKey:
            assert winreg.QueryValueEx(serverKey, "")[0] == f'"{interpreter}" "{script.resolve()}"'

        # Removing an activator whose command is already gone still removes the rest
        winreg.DeleteKey(winreg.HKEY_CURRENT_USER, serverKeyPath)
        # And keys something else added under it
        winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, serverKeyPath.replace("LocalServer32", "ProgID\\Nested")).Close()
    finally:
        unregister_hkey(TEST_AUMID)

    assert read_activator_clsid(TEST_AUMID) is None
    with pytest.raises(FileNotFoundError):
        winreg.OpenKeyEx(winreg.HKEY_CURRENT_USER, serverKeyPath.rsplit("\\", 1)[0])


def test_activation_without_toaster_handler(activator_aumid: str):
    clsid = activator_clsid(activator_aumid)
    activated = threading.Event()
    listening = InteractableWindowsToaster("Python", activator_aumid)
    listening.on_activated = lambda _: activated.set()
    silent = InteractableWindowsToaster("Python", activator_aumid)
    silent.show_toast(Toast(["Hello"]))
    # A toaster whose on_activated was unset while an activation was being delivered is skipped
    activation._dispatchers[clsid].toasters.add(silent)

    _activate(clsid, "earlier", {})
    assert activated.wait(5)


def test_activation_with_nowhere_to_go(activator_aumid: str):
    toaster = InteractableWindowsToaster("Python", activator_aumid)
    toaster.show_toast(Toast(["Hello"], tag="mine"))
    dispatcher = activation._dispatchers[activator_clsid(activator_aumid)]

    # Windows won't start the activator's command for a click this process received, so losing it pytest.warns
    with pytest.warns(UserWarning, match="no toaster's on_activated"):
        dispatcher.deliver_from_activator(_encode_arguments("earlier", None, ""), {})
    # Unlike a click on a toast this process showed without an on_activated
    dispatcher.deliver_from_activator(_encode_arguments("mine", None, ""), {})


def test_register_activator_without_command(tmp_path: Path):
    script = tmp_path / "activator.py"
    script.touch()
    clsid = activator_clsid(TEST_AUMID)
    clsidKeyPath = f"SOFTWARE\\Classes\\CLSID\\{{{str(clsid).upper()}}}"
    try:
        register_hkey(TEST_AUMID, "Activator test", None, True)
        assert read_activator_clsid(TEST_AUMID) == clsid
        with pytest.raises(FileNotFoundError):
            winreg.OpenKeyEx(winreg.HKEY_CURRENT_USER, clsidKeyPath)

        # Registering without a command removes the one registered before, so Windows has nothing to start
        register_hkey(TEST_AUMID, "Activator test", None, str(script))
        winreg.OpenKeyEx(winreg.HKEY_CURRENT_USER, clsidKeyPath).Close()
        register_hkey(TEST_AUMID, "Activator test", None, True)
        with pytest.raises(FileNotFoundError):
            winreg.OpenKeyEx(winreg.HKEY_CURRENT_USER, clsidKeyPath)

        # Registering without an activator leaves the AUMID's as it is
        register_hkey(TEST_AUMID, "Renamed")
        assert read_activator_clsid(TEST_AUMID) == clsid
    finally:
        unregister_hkey(TEST_AUMID)

    assert read_activator_clsid(TEST_AUMID) is None


def test_duplicate_deliveries(activator_aumid: str):
    received: list[ToastActivatedEventArgs] = []
    toaster = InteractableWindowsToaster("Python", activator_aumid)
    toaster.show_toast(Toast(["Hello"], tag="doubled", on_activated=received.append))
    dispatcher = activation._dispatchers[activator_clsid(activator_aumid)]
    encoded = _encode_arguments("doubled", None, "action=reply")
    eventArgs = ToastActivatedEventArgs("action=reply", {"reply": "Hi"}, "doubled", None)

    # A click on a toast on screen arrives both ways, in either order
    dispatcher.deliver_from_activator(encoded, {"reply": "Hi"})
    dispatcher.deliver_activated(eventArgs)
    dispatcher.deliver_activated(eventArgs)
    dispatcher.deliver_from_activator(encoded, {"reply": "Hi"})
    assert received == [eventArgs, eventArgs]

    # Clicks that only reach the activator, such as ones on toasts from earlier runs, are each delivered
    dispatcher.deliver_from_activator(encoded, {"reply": "Hi"})
    dispatcher.deliver_from_activator(encoded, {"reply": "Hi"})
    assert received == [eventArgs] * 4
    # As are clicks that only arrive from Activated, when another process registered the activator first
    received.clear()
    dispatcher._arrivals.clear()
    dispatcher.deliver_activated(eventArgs)
    dispatcher.deliver_activated(eventArgs)
    assert received == [eventArgs, eventArgs]

    # A click from long ago isn't taken for the same click
    received.clear()
    dispatcher._arrivals.clear()
    dispatcher.deliver_from_activator(encoded, {"reply": "Hi"})
    with pytest.MonkeyPatch.context() as monkeypatch:
        monkeypatch.setattr(activation, "_DUPLICATE_SECONDS", 0)
        dispatcher.deliver_activated(eventArgs)
    assert received == [eventArgs, eventArgs]


def test_toast_callbacks_limit(activator_aumid: str, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(activation, "_MAX_TOAST_CALLBACKS", 2)
    received: list[str] = []
    toaster = InteractableWindowsToaster("Python", activator_aumid)
    toaster.on_activated = lambda eventArgs: received.append(f"toaster {eventArgs.tag}")
    for tag in ("first", "second", "third"):
        toaster.show_toast(Toast([tag], tag=tag, on_activated=lambda eventArgs: received.append(eventArgs.tag)))

    dispatcher = activation._dispatchers[activator_clsid(activator_aumid)]
    for tag in ("first", "second", "third"):
        dispatcher.deliver_from_activator(_encode_arguments(tag, None, ""), {})
    # The oldest toast's on_activated is forgotten
    assert received == ["toaster first", "second", "third"]


def test_toaster_on_activated_lifetime(activator_aumid: str):
    toaster = InteractableWindowsToaster("Python", activator_aumid)
    toaster.on_activated = print
    dispatcher = activation._dispatchers[activator_clsid(activator_aumid)]
    assert toaster in dispatcher.toasters

    toaster.on_activated = None
    assert toaster not in dispatcher.toasters

    # A toaster whose AUMID lost its activator keeps the handler it had
    toaster.on_activated = print
    unregister_hkey(activator_aumid)
    with pytest.raises(ValueError, match="no activator registered"):
        toaster.on_activated = input
    assert toaster.on_activated is print
    assert toaster in dispatcher.toasters


def test_toaster_on_activated_errors(activator_aumid: str, monkeypatch: pytest.MonkeyPatch):
    clsid = activator_clsid(activator_aumid)
    toaster = InteractableWindowsToaster("Python", activator_aumid)
    toaster.on_activated = print
    _com_server.stop_server(clsid)

    # COM refusing the activator leaves the toaster as it was
    monkeypatch.setattr(_com_server, "_REGCLS_MULTIPLEUSE", 0xFFFF0)
    with pytest.raises(OSError, match="WinError -2147024809"):
        toaster.on_activated = input
    assert toaster.on_activated is print
    assert toaster in activation._dispatchers[clsid].toasters

    other = InteractableWindowsToaster("Python", activator_aumid)
    with pytest.raises(OSError, match="WinError -2147024809"):
        other.on_activated = print
    assert other.on_activated is None
    assert other not in activation._dispatchers[clsid].toasters

    # A toast is still shown, without the activator
    with pytest.warns(UserWarning, match="without the AUMID's activator"):
        other.show_toast(Toast(["Hello"]))


def test_shared_toaster_callbacks(activator_aumid: str):
    received: list[ToastActivatedEventArgs] = []
    # Such as when a script makes a toaster for each toast
    for _ in range(3):
        InteractableWindowsToaster("Python", activator_aumid).on_activated = received.append
    other: list[ToastActivatedEventArgs] = []
    InteractableWindowsToaster("Python", activator_aumid).on_activated = other.append

    activation._dispatchers[activator_clsid(activator_aumid)].deliver_from_activator("earlier", {})
    assert len(received) == 1
    assert len(other) == 1


def test_com_server_loads_lazily():
    # Importing the library doesn't load ctypes' COM server, which only toasters with an activator need. It's checked in
    # a new interpreter, since this one has already loaded it. -I keeps the environment and the working directory from
    # changing which windows_toasts is imported
    source = Path(__file__).parents[1] / "src"
    code = (
        "import sys; sys.path.insert(0, sys.argv[1]); import windows_toasts; "
        "print(windows_toasts.__file__); print('windows_toasts._com_server' in sys.modules)"
    )
    result = subprocess.run([sys.executable, "-I", "-c", code, str(source)], capture_output=True, text=True, check=True)
    importedFrom, loaded = result.stdout.splitlines()
    assert Path(importedFrom).is_relative_to(source)
    assert loaded == "False"


def test_command_line(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys):
    script = tmp_path / "activator.py"
    script.touch()
    clsidKeyPath = f"SOFTWARE\\Classes\\CLSID\\{{{str(activator_clsid(TEST_AUMID)).upper()}}}"

    def run(*arguments: str) -> str:
        monkeypatch.setattr(sys, "argv", ["register_hkey_aumid", "--app_id", TEST_AUMID, *arguments])
        main()
        return capsys.readouterr().out

    try:
        assert "registered" in run("--name", "Activator test")
        assert read_activator_clsid(TEST_AUMID) is None

        run("--name", "Activator test", "--activator")
        assert read_activator_clsid(TEST_AUMID) == activator_clsid(TEST_AUMID)
        with pytest.raises(FileNotFoundError):
            winreg.OpenKeyEx(winreg.HKEY_CURRENT_USER, clsidKeyPath)

        run("--name", "Activator test", "--activator", str(script))
        winreg.OpenKeyEx(winreg.HKEY_CURRENT_USER, f"{clsidKeyPath}\\LocalServer32").Close()

        assert "removed" in run("--remove")
        assert read_activator_clsid(TEST_AUMID) is None
    finally:
        unregister_hkey(TEST_AUMID)

    with pytest.raises(SystemExit):
        run("--remove", "--activator")
