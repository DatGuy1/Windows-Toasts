import datetime
from typing import Union, assert_never, cast

from winrt.windows.data.xml.dom import IXmlNode, XmlDocument, XmlElement

from .adaptive import ToastGroup, ToastGroupImage, ToastText
from .events import _encode_arguments
from .toast import Toast
from .toast_audio import ToastAudio
from .wrappers import (
    ToastButton,
    ToastButtonColour,
    ToastDisplayImage,
    ToastDuration,
    ToastHeader,
    ToastInputSelectionBox,
    ToastInputTextBox,
    ToastProgressBar,
    ToastScenario,
    ToastSystemButton,
    ToastSystemButtonAction,
)

# winrt is mocked in the docs build, and the mocks don't support |
IXmlType = Union[IXmlNode, XmlElement]  # noqa: UP007


class ToastDocument:
    """
    The XmlDocument wrapper for toasts, which applies all the
    attributes configured in :class:`~windows_toasts.toast.Toast`
    """

    xmlDocument: XmlDocument
    bindingNode: IXmlType
    """Binding node, as to avoid having to find it every time"""
    _inputFields: int
    """Tracker of number of input fields"""

    def __init__(self, toast: Toast) -> None:
        self.xmlDocument = XmlDocument()
        self.xmlDocument.load_xml("<toast><visual><binding></binding></visual></toast>")
        self.bindingNode = self.GetElementByTagName("binding")

        # Unclear whether this leads to issues regarding spacing
        for i in range(len(toast.text_fields)):
            textElement = self.xmlDocument.create_element("text")
            # Needed for WindowsToaster
            self.SetAttribute(textElement, "id", str(i + 1))
            self.bindingNode.append_child(textElement)

        # Not sure if this is the best way to do this along with the clone bit in AddImage()
        if len(toast.images) > 0:
            imageElement = self.xmlDocument.create_element("image")
            self.SetAttribute(imageElement, "src", "")
            # Needed for WindowsToaster
            self.SetAttribute(imageElement, "id", "1")
            self.bindingNode.append_child(imageElement)

        self._inputFields = 0

    @staticmethod
    def GetAttributeValue(nodeAttribute: IXmlType, attributeName: str) -> str:
        """
        Helper function that returns an attribute's value

        :param nodeAttribute: Node that has the attribute
        :type nodeAttribute: IXmlType
        :param attributeName: Name of the attribute, e.g. "duration"
        :type attributeName: str
        :return: The value of the attribute
        :rtype: str
        """
        return nodeAttribute.attributes.get_named_item(attributeName).inner_text

    def GetElementByTagName(self, tagName: str) -> IXmlType:
        """
        Helper function to get the first element by its tag name

        :param tagName: The name of the tag for the element
        :type tagName: str
        :rtype: IXmlType
        """
        # Is this way faster? Or is self.xmlDocument.select_single_node(f"/{tagName}") ?
        return self.xmlDocument.get_elements_by_tag_name(tagName).item(0)

    def SetAttribute(self, nodeAttribute: IXmlType, attributeName: str, attributeValue: str) -> None:
        """
        Helper function to set an attribute to a node. <nodeAttribute attributeName="attributeValue" />

        :param nodeAttribute: Node to apply attributes to
        :type nodeAttribute: IXmlType
        :param attributeName: Name of the attribute, e.g. "duration"
        :type attributeName: str
        :param attributeValue: Value of the attribute, e.g. "long"
        :type attributeValue: str
        """
        nodeAttribute.attributes.set_named_item(self.xmlDocument.create_attribute(attributeName))
        nodeAttribute.attributes.get_named_item(attributeName).inner_text = attributeValue

    def SetNodeStringValue(self, targetNode: IXmlType, newValue: str) -> None:
        """
        Helper function to set the inner value of a node. <text>newValue</text>

        :param targetNode: Node to apply attributes to
        :type targetNode: IXmlType
        :param newValue: Inner text of the node, e.g. "Hello, World!"
        :type newValue: str
        """
        newNode = self.xmlDocument.create_text_node(newValue)
        targetNode.append_child(newNode)

    def SetAttributionText(self, attributionText: str) -> None:
        """
        Set attribution text for the toast. This is used if we're using
        :class:`~windows_toasts.toasters.InteractableWindowsToaster` but haven't set up our own AUMID.
        `AttributionText on Microsoft.com
        <https://learn.microsoft.com/windows/apps/develop/notifications/app-notifications/app-notifications-content#attribution-text>`_

        :param attributionText: Attribution text to set
        """
        newElement = self.xmlDocument.create_element("text")
        self.bindingNode.append_child(newElement)
        self.SetAttribute(newElement, "placement", "attribution")
        self.SetNodeStringValue(newElement, attributionText)

    def SetHeader(self, header: ToastHeader) -> None:
        """
        Group the toast under a header in Action Center. `Toast headers on Microsoft.com
        <https://learn.microsoft.com/windows/apps/develop/notifications/app-notifications/app-notifications-headers>`_

        :type header: ToastHeader
        """
        headerNode = self.xmlDocument.create_element("header")
        self.SetAttribute(headerNode, "id", header.header_id)
        self.SetAttribute(headerNode, "title", header.title)
        if header.launch is None:
            # Windows requires the attribute. Without an activator, foreground activation does nothing anyway
            self.SetAttribute(headerNode, "arguments", "")
        else:
            self.SetAttribute(headerNode, "activationType", "protocol")
            self.SetAttribute(headerNode, "arguments", header.launch)

        toastNode = self.GetElementByTagName("toast")
        toastNode.insert_before(headerNode, toastNode.first_child)

    def SetAudioAttributes(self, audioConfiguration: ToastAudio) -> None:
        """
        Apply audio attributes for the toast. If a loop is requested, the toast duration has to be set to long. `Audio
        on Microsoft.com <https://learn.microsoft.com/windows/apps/develop/notifications/app-notifications/app-notifications-content#audio>`_
        """
        previousAudioNode = self.GetElementByTagName("audio")
        if previousAudioNode is not None:
            previousAudioNode.parent_node.remove_child(previousAudioNode)

        audioNode = self.xmlDocument.create_element("audio")
        self.GetElementByTagName("toast").append_child(audioNode)

        if audioConfiguration.silent:
            self.SetAttribute(audioNode, "silent", str(audioConfiguration.silent).lower())
            return

        self.SetAttribute(audioNode, "src", audioConfiguration.sound_value)
        if audioConfiguration.looping:
            self.SetAttribute(audioNode, "loop", str(audioConfiguration.looping).lower())
            # Looping audio requires the duration attribute in the audio element's parent toast element to be "long"
            self.SetDuration(ToastDuration.Long)

    def SetTextField(self, nodePosition: int) -> None:
        """
        Set a simple text field. `Text elements on Microsoft.com
        <https://learn.microsoft.com/windows/apps/develop/notifications/app-notifications/app-notifications-content#text-elements>`_

        :param nodePosition: Index of the text fields of the toast type for the text to be written in
        """
        targetNode = self.xmlDocument.get_elements_by_tag_name("text").item(nodePosition)

        # We used to simply set it to newValue, but since we've now switched to BindableString we just set it to text{i}
        # Set it to i + 1 just because starting at 1 rather than 0 is easier on the eye
        self.SetNodeStringValue(targetNode, f"{{text{nodePosition + 1}}}")

    def SetTextFieldStatic(self, nodePosition: int, newValue: str) -> None:
        """
        :meth:`SetTextField` but static, generally used for scheduled toasts

        :param nodePosition: Index of the text fields of the toast type for the text to be written in
        :param newValue: Content value of the text field
        """
        targetNode = self.xmlDocument.get_elements_by_tag_name("text").item(nodePosition)
        self.SetNodeStringValue(targetNode, newValue)

    def SetCustomTimestamp(self, customTimestamp: datetime.datetime) -> None:
        """
        Apply a custom timestamp to display on the toast and in Action Center. `Custom timestamp on
        Microsoft.com <https://learn.microsoft.com/windows/apps/develop/notifications/app-notifications/app-notifications-content?tabs=xml#custom-timestamp>`_

        :param customTimestamp: The target datetime
        :type customTimestamp: datetime.datetime
        """
        toastNode = self.GetElementByTagName("toast")
        self.SetAttribute(toastNode, "displayTimestamp", customTimestamp.strftime("%Y-%m-%dT%H:%M:%SZ"))

    def AddImage(self, displayImage: ToastDisplayImage) -> None:
        """
        Add an image to display. `Inline image on Microsoft.com
        <https://learn.microsoft.com/windows/apps/develop/notifications/app-notifications/app-notifications-content#inline-image>`_

        :type displayImage: ToastDisplayImage
        """
        imageNode = self.GetElementByTagName("image")
        if self.GetAttributeValue(imageNode, "src") != "":
            # For WindowsToaster
            imageNode = imageNode.clone_node(True)
            self.SetAttribute(imageNode, "id", "2")
            self.bindingNode.append_child(imageNode)

        self.SetAttribute(imageNode, "src", str(displayImage.image.path))

        if displayImage.altText is not None:
            self.SetAttribute(imageNode, "alt", displayImage.altText)

        self.SetAttribute(imageNode, "placement", displayImage.position.value)

        if displayImage.circleCrop:
            self.SetAttribute(imageNode, "hint-crop", "circle")

    def SetScenario(self, scenario: ToastScenario) -> None:
        """
        Set whether the notification should be marked as important. `Important Notifications on Microsoft.com
        <https://learn.microsoft.com/windows/apps/develop/notifications/app-notifications/app-notifications-content#important-notifications>`_

        :param scenario: Scenario to mark the toast as
        :type scenario: ToastScenario
        """
        toastNode = self.GetElementByTagName("toast")
        self.SetAttribute(toastNode, "scenario", scenario.value)

    def AddInput(self, toastInput: ToastInputTextBox | ToastInputSelectionBox) -> None:
        """
        Add a field for the user to input. `Inputs with button bar on Microsoft.com
        <https://learn.microsoft.com/windows/apps/develop/notifications/app-notifications/app-notifications-content#quick-reply-text-box>`_

        :type toastInput: Union[ToastInputTextBox, ToastInputSelectionBox]
        :raises: AssertionError: If the input isn't a :class:`~windows_toasts.wrappers.ToastInputTextBox` or
            :class:`~windows_toasts.wrappers.ToastInputSelectionBox`
        """
        self._inputFields += 1
        inputNode = self.xmlDocument.create_element("input")
        self.SetAttribute(inputNode, "id", toastInput.input_id)
        self.SetAttribute(inputNode, "title", toastInput.caption)

        match toastInput:
            case ToastInputTextBox():
                self.SetAttribute(inputNode, "type", "text")
                self.SetAttribute(inputNode, "placeHolderContent", toastInput.placeholder)
                # Undocumented for text boxes, but Windows prefills the box with it
                if toastInput.default_input is not None:
                    self.SetAttribute(inputNode, "defaultInput", toastInput.default_input)
            case ToastInputSelectionBox():
                self.SetAttribute(inputNode, "type", "selection")
                if toastInput.default_selection is not None:
                    self.SetAttribute(inputNode, "defaultInput", toastInput.default_selection.selection_id)

                for selection in toastInput.selections:
                    selectionElement = self.xmlDocument.create_element("selection")
                    self.SetAttribute(selectionElement, "id", selection.selection_id)
                    self.SetAttribute(selectionElement, "content", selection.content)
                    inputNode.append_child(selectionElement)
            case _:
                assert_never(toastInput)

        actionNodes = self.xmlDocument.get_elements_by_tag_name("actions")
        if actionNodes.length > 0:
            actionsNode = actionNodes.item(0)
            # actionsNode.insert_before(inputNode, actionsNode.first_child)
            actionsNode.append_child(inputNode)
        else:
            toastNode = self.GetElementByTagName("toast")

            actionsNode = self.xmlDocument.create_element("actions")
            toastNode.append_child(actionsNode)

            actionsNode.append_child(inputNode)

    def SetDuration(self, duration: ToastDuration) -> None:
        """
        Set the duration of the toast. If looping audio is enabled, it will automatically be set to long

        :type duration: ToastDuration
        """
        toastNode = self.GetElementByTagName("toast")
        self.SetAttribute(toastNode, "duration", duration.value)

    def AddAction(self, action: ToastButton | ToastSystemButton) -> None:
        """
        Adds a button to the toast. Only works on :obj:`~windows_toasts.toasters.InteractableWindowsToaster`

        :type action: Union[ToastButton, ToastSystemButton]
        :raises: ValueError: If a context menu button has no content
        :raises: AssertionError: If the action isn't a :class:`~windows_toasts.wrappers.ToastButton` or
            :class:`~windows_toasts.wrappers.ToastSystemButton`, or a
            :class:`~windows_toasts.wrappers.ToastSystemButton`'s action isn't a
            :class:`~windows_toasts.wrappers.ToastSystemButtonAction`
        """
        if isinstance(action, ToastButton) and action.inContextMenu and not action.content:
            raise ValueError("A ToastButton in the context menu must have content")

        actionNodes = self.xmlDocument.get_elements_by_tag_name("actions")
        if actionNodes.length > 0:
            actionsNode = actionNodes.item(0)
        else:
            actionsNode = self.xmlDocument.create_element("actions")
            self.GetElementByTagName("toast").append_child(actionsNode)

        actionNode = self.xmlDocument.create_element("action")
        self.SetAttribute(actionNode, "content", action.content)

        match action:
            case ToastButton():
                if action.launch is None:
                    self.SetAttribute(actionNode, "arguments", action.arguments)
                else:
                    self.SetAttribute(actionNode, "activationType", "protocol")
                    self.SetAttribute(actionNode, "arguments", action.launch)

                if action.inContextMenu:
                    self.SetAttribute(actionNode, "placement", "contextMenu")
                if action.tooltip is not None:
                    self.SetAttribute(actionNode, "hint-tooltip", action.tooltip)
            case ToastSystemButton():
                self.SetAttribute(actionNode, "activationType", "system")
                match action.action:
                    case ToastSystemButtonAction.Snooze:
                        self.SetAttribute(actionNode, "arguments", "snooze")
                    case ToastSystemButtonAction.Dismiss:
                        self.SetAttribute(actionNode, "arguments", "dismiss")
                    case _:
                        # Nothing stops .action from being assigned something else, which can't be shown as a button
                        assert_never(action.action)
            case _:
                assert_never(action)

        if action.image is not None:
            self.SetAttribute(actionNode, "imageUri", action.image.path)
        if action.relatedInput is not None:
            self.SetAttribute(actionNode, "hint-inputId", action.relatedInput.input_id)
        if action.colour is not ToastButtonColour.Default:
            self.SetAttribute(actionNode, "hint-buttonStyle", action.colour.value)

        actionsNode.append_child(actionNode)

    def AddActivationTags(self, toast: Toast) -> None:
        """
        Add the toast's tag and group to the arguments of the toast and its buttons, since Windows only gives an
        activator the arguments. Protocol and system activations are left as they are
        """
        actionNodes = self.xmlDocument.get_elements_by_tag_name("action")
        nodes = [self.GetElementByTagName("toast"), *(actionNodes.item(i) for i in range(actionNodes.length))]
        for node in nodes:
            # pywinrt's stubs don't say so, but get_named_item returns None for a missing attribute
            activationType = cast(IXmlNode | None, node.attributes.get_named_item("activationType"))
            if activationType is not None and activationType.inner_text in ("protocol", "system"):
                continue

            attributeName = "launch" if node.node_name == "toast" else "arguments"
            current = cast(IXmlNode | None, node.attributes.get_named_item(attributeName))
            arguments = "" if current is None else current.inner_text
            self.SetAttribute(node, attributeName, _encode_arguments(toast.tag, toast.group, arguments))

    def AddProgressBar(self) -> None:
        """
        Add a progress bar on your app notification to keep the user informed of the progress of operations.
        `Progress bar on Microsoft.com
        <https://learn.microsoft.com/windows/apps/develop/notifications/app-notifications/app-notifications-content#progress-bar>`_
        """
        progressBarNode = self.xmlDocument.create_element("progress")
        self.SetAttribute(progressBarNode, "status", "{status}")
        self.SetAttribute(progressBarNode, "value", "{progress}")

        self.SetAttribute(progressBarNode, "valueStringOverride", "{progress_override}")
        self.SetAttribute(progressBarNode, "title", "{caption}")

        self.bindingNode.append_child(progressBarNode)

    def AddStaticProgressBar(self, progressBar: ToastProgressBar) -> None:
        """
        :meth:`AddProgressBar` but static, generally used for scheduled toasts
        """
        progressBarNode = self.xmlDocument.create_element("progress")
        self.SetAttribute(progressBarNode, "status", progressBar.status)
        self.SetAttribute(
            progressBarNode, "value", "indeterminate" if progressBar.progress is None else str(progressBar.progress)
        )

        if progressBar.progress_override is not None:
            self.SetAttribute(progressBarNode, "valueStringOverride", progressBar.progress_override)
        if progressBar.caption is not None:
            self.SetAttribute(progressBarNode, "title", progressBar.caption)

        self.bindingNode.append_child(progressBarNode)

    def AddGroup(self, group: ToastGroup) -> None:
        """
        Add a row of columns with styled text and images. `Adaptive content on Microsoft.com
        <https://learn.microsoft.com/windows/apps/develop/notifications/app-notifications/app-notifications-content
        #adaptive-content>`_

        :type group: ToastGroup
        :raises: AssertionError: If a column's content isn't a :class:`~windows_toasts.adaptive.ToastText` or
            :class:`~windows_toasts.adaptive.ToastGroupImage`
        """
        groupNode = self.xmlDocument.create_element("group")
        for subgroup in group.subgroups:
            subgroupNode = self.xmlDocument.create_element("subgroup")
            if subgroup.weight is not None:
                self.SetAttribute(subgroupNode, "hint-weight", str(subgroup.weight))
            if subgroup.text_stacking.value:
                self.SetAttribute(subgroupNode, "hint-textStacking", subgroup.text_stacking.value)

            for content in subgroup.content:
                match content:
                    case ToastText():
                        subgroupNode.append_child(self._CreateGroupText(content))
                    case ToastGroupImage():
                        subgroupNode.append_child(self._CreateGroupImage(content))
                    case _:
                        assert_never(content)

            groupNode.append_child(subgroupNode)

        self.bindingNode.append_child(groupNode)

    def _CreateGroupText(self, text: ToastText) -> XmlElement:
        textNode = self.xmlDocument.create_element("text")
        self.SetNodeStringValue(textNode, text.text)
        if text.style.value:
            self.SetAttribute(textNode, "hint-style", text.style.value)
        if text.align.value:
            self.SetAttribute(textNode, "hint-align", text.align.value)
        if text.wrap:
            self.SetAttribute(textNode, "hint-wrap", "true")
        if text.max_lines is not None:
            self.SetAttribute(textNode, "hint-maxLines", str(text.max_lines))
        if text.min_lines is not None:
            self.SetAttribute(textNode, "hint-minLines", str(text.min_lines))

        return textNode

    def _CreateGroupImage(self, image: ToastGroupImage) -> XmlElement:
        imageNode = self.xmlDocument.create_element("image")
        self.SetAttribute(imageNode, "src", image.image.path)
        if image.alt_text is not None:
            self.SetAttribute(imageNode, "alt", image.alt_text)
        if image.circle_crop:
            self.SetAttribute(imageNode, "hint-crop", "circle")
        if image.remove_margin:
            self.SetAttribute(imageNode, "hint-removeMargin", "true")
        if image.align.value:
            self.SetAttribute(imageNode, "hint-align", image.align.value)

        return imageNode
