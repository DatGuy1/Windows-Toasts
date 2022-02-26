import datetime

from .toast_audio import ToastAudio
from winsdk.windows.data.xml.dom import IXmlNode, XmlDocument


class ToastDocument:
    def __init__(self, xmlDocument: XmlDocument):
        self.xmlDocument = xmlDocument

    def SetAttribute(self, nodeAttribute, attributeName, attributeValue):
        nodeAttribute.attributes.set_named_item(self.xmlDocument.create_attribute(attributeName))
        nodeAttribute.attributes.get_named_item(attributeName).inner_text = attributeValue

    def SetNodeStringValue(self, targetNode, newValue):
        newNode = self.xmlDocument.create_text_node(newValue)
        targetNode.append_child(newNode)

    def SetAttributionText(self, attributionText):
        bindingNode = self.xmlDocument.get_elements_by_tag_name("binding").item(0)

        newElement = self.xmlDocument.create_element("text")
        bindingNode.append_child(newElement)
        self.SetAttribute(newElement, "placement", "attribution")
        self.SetNodeStringValue(newElement, attributionText)

    def SetAudioAttributes(self, audioConfiguration: ToastAudio):
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
            self.AddDuration("long")

    def SetTextField(self, newValue, nodePosition: int):
        targetNode = self.xmlDocument.get_elements_by_tag_name("text").item(nodePosition)
        self.SetNodeStringValue(targetNode, newValue)

    def SetCustomTimestamp(self, customTimestamp: datetime.datetime):
        toastNode = self.xmlDocument.get_elements_by_tag_name("toast").item(0)
        self.SetAttribute(toastNode, "displayTimestamp", customTimestamp.strftime("%Y-%m-%dT%H:%M:%SZ"))

    def SetImageField(self, imagePath):
        imageNode = self.xmlDocument.get_elements_by_tag_name("image").item(0)
        self.SetNodeStringValue(imageNode.attributes.get_named_item("src"), f"file:///{imagePath}")

    def AddDuration(self, duration):
        durationNode = self.xmlDocument.get_elements_by_tag_name("toast").item(0)
        self.SetAttribute(durationNode, "duration", duration)

    def AddAction(self, buttonContent, arguments):
        actionNodes = self.xmlDocument.get_elements_by_tag_name("actions")
        actionsNode: IXmlNode
        if actionNodes.length > 0:
            actionsNode = actionNodes.item(0)
        else:
            toastNode = self.xmlDocument.get_elements_by_tag_name("toast").item(0)
            self.SetAttribute(toastNode, "template", "ToastGeneric")
            self.AddDuration("long")

            actionsNode = self.xmlDocument.create_element("actions")
            toastNode.append_child(actionsNode)

        actionNode = self.xmlDocument.create_element("action")
        self.SetAttribute(actionNode, "content", buttonContent)
        self.SetAttribute(actionNode, "arguments", arguments)
        self.SetAttribute(actionNode, "activationType", "background")
        actionsNode.append_child(actionNode)
