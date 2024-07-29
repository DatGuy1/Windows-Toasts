import datetime
from typing import Union

from winrt.windows.data.xml.dom import IXmlNode, XmlDocument, XmlElement

from .toast import Toast
from .toast_audio import ToastAudio
from .wrappers import (
    ToastButton,
    ToastButtonColour,
    ToastDisplayImage,
    ToastDuration,
    ToastInputSelectionBox,
    ToastInputTextBox,
    ToastProgressBar,
    ToastScenario,
    ToastSystemButton,
    ToastSystemButtonAction,
)

IXmlType = Union[IXmlNode, XmlElement]


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
        `AttributionText on Microsoft.com <https://learn.microsoft.com/windows/apps/design/shell/tiles-and
        -notifications/adaptive-interactive-toasts#attribution-text>`_

        :param attributionText: Attribution text to set
        """
        newElement = self.xmlDocument.create_element("text")
        self.bindingNode.append_child(newElement)
        self.SetAttribute(newElement, "placement", "attribution")
        self.SetNodeStringValue(newElement, attributionText)

    def SetAudioAttributes(self, audioConfiguration: ToastAudio) -> None:
        """
        Apply audio attributes for the toast. If a loop is requested, the toast duration has to be set to long. `Audio
        on Microsoft.com <https://learn.microsoft.com/windows/apps/design/shell/tiles-and-notifications/adaptive
        -interactive-toasts#audio>`_
        """
        audioNode = self.GetElementByTagName("audio")
        if audioNode is None:
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
        <https://learn.microsoft.com/windows/apps/design/shell/tiles-and-notifications/adaptive-interactive-toasts#text-elements>`_

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
        Apply a custom timestamp to display on the toast and in the notification center. `Custom timestamp on
        Microsoft.com <https://learn.microsoft.com/windows/apps/design/shell/tiles-and-notifications/adaptive
        -interactive-toasts?tabs=xml#custom-timestamp>`_

        :param customTimestamp: The target datetime
        :type customTimestamp: datetime.datetime
        """
        toastNode = self.GetElementByTagName("toast")
        self.SetAttribute(toastNode, "displayTimestamp", customTimestamp.strftime("%Y-%m-%dT%H:%M:%SZ"))

    def AddImage(self, displayImage: ToastDisplayImage) -> None:
        """
        Add an image to display. `Inline image on Microsoft.com <https://learn.microsoft.com/windows/
        apps/design/shell/tiles-and-notifications/adaptive-interactive-toasts#inline-image>`_

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
        <https://learn.microsoft.com/windows/apps/design/shell/tiles-and-notifications/adaptive-interactive-toasts
        #important-notifications>`_

        :param scenario: Scenario to mark the toast as
        :type scenario: ToastScenario
        """
        toastNode = self.GetElementByTagName("toast")
        self.SetAttribute(toastNode, "scenario", scenario.value)

    def AddInput(self, toastInput: Union[ToastInputTextBox, ToastInputSelectionBox]) -> None:
        """
        Add a field for the user to input. `Inputs with button bar on Microsoft.com
        <https://learn.microsoft.com/windows/apps/design/shell/tiles-and-notifications/adaptive-interactive
        -toasts#quick-reply-text-box>`_

        :type toastInput: Union[ToastInputTextBox, ToastInputSelectionBox]
        """
        self._inputFields += 1
        inputNode = self.xmlDocument.create_element("input")
        self.SetAttribute(inputNode, "id", toastInput.input_id)
        self.SetAttribute(inputNode, "title", toastInput.caption)

        if isinstance(toastInput, ToastInputTextBox):
            self.SetAttribute(inputNode, "type", "text")
            # noinspection PyUnresolvedReferences
            self.SetAttribute(inputNode, "placeHolderContent", toastInput.placeholder)
        elif isinstance(toastInput, ToastInputSelectionBox):
            self.SetAttribute(inputNode, "type", "selection")
            if toastInput.default_selection is not None:
                self.SetAttribute(inputNode, "defaultInput", toastInput.default_selection.selection_id)

            for selection in toastInput.selections:
                selectionElement = self.xmlDocument.create_element("selection")
                self.SetAttribute(selectionElement, "id", selection.selection_id)
                self.SetAttribute(selectionElement, "content", selection.content)
                inputNode.append_child(selectionElement)

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

    def AddAction(self, action: Union[ToastButton, ToastSystemButton]) -> None:
        """
        Adds a button to the toast. Only works on :obj:`~windows_toasts.toasters.InteractableWindowsToaster`

        :type action: Union[ToastButton, ToastSystemButton]
        """
        actionNodes = self.xmlDocument.get_elements_by_tag_name("actions")
        if actionNodes.length > 0:
            actionsNode = actionNodes.item(0)
        else:
            actionsNode = self.xmlDocument.create_element("actions")
            self.GetElementByTagName("toast").append_child(actionsNode)

        actionNode = self.xmlDocument.create_element("action")
        self.SetAttribute(actionNode, "content", action.content)

        if isinstance(action, ToastButton):
            if action.launch is None:
                self.SetAttribute(actionNode, "arguments", action.arguments)
            else:
                self.SetAttribute(actionNode, "activationType", "protocol")
                self.SetAttribute(actionNode, "arguments", action.launch)

            if action.inContextMenu:
                self.SetAttribute(actionNode, "placement", "contextMenu")
            if action.tooltip is not None:
                self.SetAttribute(actionNode, "hint-tooltip", action.tooltip)
        elif isinstance(action, ToastSystemButton):
            self.SetAttribute(actionNode, "activationType", "system")
            if action.action == ToastSystemButtonAction.Snooze:
                self.SetAttribute(actionNode, "arguments", "snooze")
            elif action.action == ToastSystemButtonAction.Dismiss:
                self.SetAttribute(actionNode, "arguments", "dismiss")

        if action.image is not None:
            self.SetAttribute(actionNode, "imageUri", action.image.path)
        if action.relatedInput is not None:
            self.SetAttribute(actionNode, "hint-inputId", action.relatedInput.input_id)
        if action.colour is not ToastButtonColour.Default:
            self.SetAttribute(actionNode, "hint-buttonStyle", action.colour.value)

        actionsNode.append_child(actionNode)

    def AddProgressBar(self) -> None:
        """
        Add a progress bar on your app notification to keep the user informed of the progress of operations.
        `Progress bar on Microsoft.com <https://learn.microsoft.com/windows/apps/design/shell/tiles-and-notifications
        /adaptive-interactive-toasts#progress-bar>`_
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
