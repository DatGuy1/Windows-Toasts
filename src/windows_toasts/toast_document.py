import datetime
from typing import Optional, TypeVar, Union

from winsdk.windows.data.xml.dom import IXmlNode, XmlDocument, XmlElement

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
)

IXmlType = TypeVar("IXmlType", IXmlNode, XmlElement)


class ToastDocument:
    """
    The XmlDocument wrapper for toasts, which applies all the
    attributes configured in :class:`~windows_toasts.toast_types.Toast`
    """

    xmlDocument: XmlDocument

    def __init__(self, xmlDocument: XmlDocument) -> None:
        self.xmlDocument = xmlDocument
        self.inputFields = 0

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

    def GetElementByTagName(self, tagName: str) -> Optional[IXmlType]:
        """
        Helper function to get the first element by its tag name

        :param tagName: The name of the tag for the element
        :type tagName: str
        :rtype: IXmlType
        """
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
        bindingNode = self.GetElementByTagName("binding")

        newElement = self.xmlDocument.create_element("text")
        bindingNode.append_child(newElement)
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
            self.xmlDocument.select_single_node("/toast").append_child(audioNode)

        if audioConfiguration.silent:
            self.SetAttribute(audioNode, "silent", str(audioConfiguration.silent).lower())
            return

        self.SetAttribute(audioNode, "src", f"ms-winsoundevent:Notification.{audioConfiguration.sound_value}")
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

        # We used to simply set it to newValue, but since we've now switched to AdaptiveText we just set it to text{i}
        # self.SetNodeStringValue(targetNode, newValue)

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
        Add an image to display. Only works on ToastImageAndText toasts. `Inline image on Microsoft.com
        <https://learn.microsoft.com/windows/apps/design/shell/tiles-and-notifications/adaptive-interactive
        -toasts#inline-image>`_

        :type displayImage: ToastDisplayImage
        """
        imageNode = self.GetElementByTagName("image")
        if self.GetAttributeValue(imageNode, "src") != "":
            imageNode = imageNode.clone_node(True)
            self.SetAttribute(imageNode, "id", "2")
            self.GetElementByTagName("binding").append_child(imageNode)

        self.SetAttribute(imageNode, "src", str(displayImage.image.path))

        if displayImage.altText is not None:
            self.SetAttribute(imageNode, "alt", displayImage.altText)

        self.SetAttribute(imageNode, "placement", "hero" if displayImage.large else "appLogoOverride")
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
        isTextBox = isinstance(toastInput, ToastInputTextBox)

        self.inputFields += 1
        inputNode = self.xmlDocument.create_element("input")
        self.SetAttribute(inputNode, "id", toastInput.input_id)
        self.SetAttribute(inputNode, "title", toastInput.caption)

        if isTextBox:
            self.SetAttribute(inputNode, "type", "text")
            # noinspection PyUnresolvedReferences
            self.SetAttribute(inputNode, "placeHolderContent", toastInput.placeholder)
        else:
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
        durationNode = self.GetElementByTagName("toast")
        self.SetAttribute(durationNode, "duration", duration.value)

    def AddAction(self, action: ToastButton) -> None:
        """
        Adds a button to the toast. Only works on :obj:`~windows_toasts.toasters.InteractableWindowsToaster`

        :type action: ToastButton
        """
        actionNodes = self.xmlDocument.get_elements_by_tag_name("actions")
        if actionNodes.length > 0:
            actionsNode = actionNodes.item(0)
        else:
            toastNode = self.GetElementByTagName("toast")
            self.SetAttribute(toastNode, "template", "ToastGeneric")

            actionsNode = self.xmlDocument.create_element("actions")
            toastNode.append_child(actionsNode)

        actionNode = self.xmlDocument.create_element("action")
        self.SetAttribute(actionNode, "content", action.content)
        self.SetAttribute(actionNode, "arguments", action.arguments)
        self.SetAttribute(actionNode, "activationType", "background")

        if action.image is not None:
            self.SetAttribute(actionNode, "imageUri", action.image.path)
        if action.relatedInput is not None:
            self.SetAttribute(actionNode, "hint-inputId", action.relatedInput.input_id)
        if action.inContextMenu:
            self.SetAttribute(actionNode, "placement", "contextMenu")
        if action.tooltip is not None:
            self.SetAttribute(actionNode, "hint-tooltip", action.tooltip)
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

        self.GetElementByTagName("binding").append_child(progressBarNode)

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

        self.GetElementByTagName("binding").append_child(progressBarNode)
