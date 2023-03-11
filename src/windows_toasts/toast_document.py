import datetime
from typing import TypeVar

from winsdk.windows.data.xml.dom import IXmlNode, XmlDocument, XmlElement

from .toast_audio import ToastAudio

IXmlType = TypeVar("IXmlType", IXmlNode, XmlElement)


class ToastDocument:
    """
    The meaty XmlDocument wrapper for toasts, which applies all the
    elements configured in :class:`Toast <windows_toasts.toast_types.Toast>`
    """

    xmlDocument: XmlDocument

    def __init__(self, xmlDocument: XmlDocument) -> None:
        self.xmlDocument = xmlDocument

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
        :class:`~windows_toasts.windows_toasts.InteractableWindowsToaster` but haven't set up our own AUMID.
        `AttributionText on Microsoft.com <https://learn.microsoft.com/windows/apps/design/shell/tiles-and
        -notifications/adaptive-interactive-toasts#attribution-text>`_

        :param attributionText: Attribution text to set
        """
        bindingNode = self.xmlDocument.get_elements_by_tag_name("binding").item(0)

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
        audioNode = self.xmlDocument.get_elements_by_tag_name("audio").item(0)
        if audioNode is None:
            audioNode = self.xmlDocument.create_element("audio")
            self.xmlDocument.select_single_node("/toast").append_child(audioNode)

        if audioConfiguration.silent:
            self.SetAttribute(audioNode, "silent", str(audioConfiguration.silent).lower())
            return

        self.SetAttribute(audioNode, "src", f"ms-winsoundevent:Notification.{audioConfiguration.sound.value}")
        if audioConfiguration.looping:
            self.SetAttribute(audioNode, "loop", str(audioConfiguration.looping).lower())
            # Looping audio requires the duration attribute in the audio element's parent toast element to be "long"
            self.SetDuration("long")

    def SetTextField(self, newValue: str, nodePosition: int) -> None:
        """
        Set a simple text field. `Text elements on Microsoft.com
        <https://learn.microsoft.com/windows/apps/design/shell/tiles-and-notifications/adaptive-interactive-toasts#text-elements>`_

        :param newValue: Text to be written
        :param nodePosition: Index of the text fields of the toast type for the text to be written in
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
        toastNode = self.xmlDocument.get_elements_by_tag_name("toast").item(0)
        self.SetAttribute(toastNode, "displayTimestamp", customTimestamp.strftime("%Y-%m-%dT%H:%M:%SZ"))

    def SetImageField(self, imagePath: str) -> None:
        """
        Set an image to display. Only works on ToastImageAndText toasts. `Inline image on Microsoft.com
        <https://learn.microsoft.com/windows/apps/design/shell/tiles-and-notifications/adaptive-interactive
        -toasts#inline-image>`_

        :param imagePath: Sanitised PathLike converted into string
        :type imagePath: str
        """
        imageNode = self.xmlDocument.get_elements_by_tag_name("image").item(0)
        self.SetNodeStringValue(imageNode.attributes.get_named_item("src"), imagePath)

    def SetInputField(self, placeholderText: str) -> None:
        """
        Set an input field for the user to write in. `Inputs with button bar on Microsoft.com
        <https://learn.microsoft.com/windows/apps/design/shell/tiles-and-notifications/adaptive-interactive
        -toasts#quick-reply-text-box>`_

        :param placeholderText: Hint about what to write, similarly to HTML
        """
        inputNode = self.xmlDocument.create_element("input")
        self.SetAttribute(inputNode, "id", "textBox")
        self.SetAttribute(inputNode, "type", "text")
        self.SetAttribute(inputNode, "placeHolderContent", placeholderText)

        actionNodes = self.xmlDocument.get_elements_by_tag_name("actions")
        actionsNode: IXmlType
        if actionNodes.length > 0:
            actionsNode = actionNodes.item(0)
            actionsNode.insert_before(inputNode, actionsNode.first_child)
        else:
            toastNode = self.xmlDocument.get_elements_by_tag_name("toast").item(0)

            actionsNode = self.xmlDocument.create_element("actions")
            toastNode.append_child(actionsNode)

            actionsNode.append_child(inputNode)

    def SetDuration(self, duration: str) -> None:
        """
        Set the duration of the toast. If looping audio is enabled, it will automatically be set to long

        :param duration: str
        :type duration: str
        """
        durationNode = self.xmlDocument.get_elements_by_tag_name("toast").item(0)
        self.SetAttribute(durationNode, "duration", duration)

    def AddAction(self, buttonContent: str, arguments: str) -> None:
        """
        Adds a button to the toast. Only works on :obj:`~windows_toasts.windows_toasts.InteractableWindowsToaster`

        :param buttonContent: Text to display on the button
        :type buttonContent: str
        :param arguments: Arguments that will be available in the callback
        :type arguments: str
        """
        actionNodes = self.xmlDocument.get_elements_by_tag_name("actions")
        actionsNode: IXmlType
        if actionNodes.length > 0:
            actionsNode = actionNodes.item(0)
        else:
            toastNode = self.xmlDocument.get_elements_by_tag_name("toast").item(0)
            self.SetAttribute(toastNode, "template", "ToastGeneric")
            self.SetDuration("long")

            actionsNode = self.xmlDocument.create_element("actions")
            toastNode.append_child(actionsNode)

        actionNode = self.xmlDocument.create_element("action")
        self.SetAttribute(actionNode, "content", buttonContent)
        self.SetAttribute(actionNode, "arguments", arguments)
        self.SetAttribute(actionNode, "activationType", "background")
        actionsNode.append_child(actionNode)
