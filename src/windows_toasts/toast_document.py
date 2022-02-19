from typing import Any

from .toast_audio import ToastAudio
from winsdk.windows.data.xml.dom import IXmlNode, XmlDocument


class ToastDocument:
    def __init__(self, xmlDocument: XmlDocument):
        self.xmlDocument = xmlDocument

    def SetAttribute(self, nodeAttribute: IXmlNode, attributeName: str, attributeValue: Any) -> None:
        nodeAttribute.attributes.set_named_item(self.xmlDocument.create_attribute(attributeName))
        nodeAttribute.attributes.get_named_item(attributeName).inner_text = str(attributeValue).lower()

    def SetNodeStringValue(self, newValue: str, targetNode: IXmlNode) -> None:
        newNode = self.xmlDocument.create_text_node(newValue)
        targetNode.append_child(newNode)

    def SetAudioAttributes(self, audioConfiguration: ToastAudio) -> None:
        audioNode: IXmlNode = self.xmlDocument.get_elements_by_tag_name("audio").item(0)
        if audioNode is None:
            audioNode = self.xmlDocument.create_element("audio")
            self.xmlDocument.select_single_node("/toast").append_child(audioNode)

        if audioConfiguration.silent:
            self.SetAttribute(audioNode, "silent", audioConfiguration.silent)
            return

        self.SetAttribute(audioNode, "src", f"ms-winsoundevent:Notification.{audioConfiguration.sound.value}")
        if audioConfiguration.looping:
            self.SetAttribute(audioNode, "loop", audioConfiguration.looping)
            # Looping audio requires the duration attribute in the audio element's parent toast element to be "long"
            self.AddDuration("long")

    def SetTextField(self, newValue: str, nodePosition: int) -> None:
        targetNode = self.xmlDocument.get_elements_by_tag_name("text").item(nodePosition)
        self.SetNodeStringValue(newValue, targetNode)

    def SetImageField(self, imagePath: str) -> None:
        imageNode = self.xmlDocument.get_elements_by_tag_name("image").item(0)
        self.SetNodeStringValue(f"file:///{imagePath}", imageNode.attributes.get_named_item("src"))

    def AddDuration(self, duration: str) -> None:
        durationNode = self.xmlDocument.get_elements_by_tag_name("toast").item(0)
        self.SetAttribute(durationNode, "duration", duration)
