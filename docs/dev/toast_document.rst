:py:mod:`windows_toasts.toast_document`
=======================================

.. py:module:: windows_toasts.toast_document

.. autodoc2-docstring:: windows_toasts.toast_document
   :allowtitles:

Module Contents
---------------

Classes
~~~~~~~

.. list-table::
   :class: autosummary longtable
   :align: left

   * - :py:obj:`ToastDocument <windows_toasts.toast_document.ToastDocument>`
     - .. autodoc2-docstring:: windows_toasts.toast_document.ToastDocument
          :summary:

Data
~~~~

.. list-table::
   :class: autosummary longtable
   :align: left

   * - IXmlType
     - Either :py:obj:`IXmlNode <winsdk.windows.data.xml.dom.IXmlNode>` or
       :py:obj:`XmlElement <winsdk.windows.data.xml.dom.XmlElement>`,
       who have the same required XML functionality

API
~~~

.. py:class:: ToastDocument(xmlDocument: winsdk.windows.data.xml.dom.XmlDocument)
   :canonical: windows_toasts.toast_document.ToastDocument

   .. autodoc2-docstring:: windows_toasts.toast_document.ToastDocument

   .. rubric:: Initialization

   .. autodoc2-docstring:: windows_toasts.toast_document.ToastDocument.__init__

   .. py:attribute:: xmlDocument
      :canonical: windows_toasts.toast_document.ToastDocument.xmlDocument
      :type: winsdk.windows.data.xml.dom.XmlDocument
      :value: None

      .. autodoc2-docstring:: windows_toasts.toast_document.ToastDocument.xmlDocument

   .. py:method:: SetAttribute(nodeAttribute: windows_toasts.toast_document.IXmlType, attributeName: str, attributeValue: str) -> None
      :canonical: windows_toasts.toast_document.ToastDocument.SetAttribute

      .. autodoc2-docstring:: windows_toasts.toast_document.ToastDocument.SetAttribute

   .. py:method:: SetNodeStringValue(targetNode: windows_toasts.toast_document.IXmlType, newValue: str) -> None
      :canonical: windows_toasts.toast_document.ToastDocument.SetNodeStringValue

      .. autodoc2-docstring:: windows_toasts.toast_document.ToastDocument.SetNodeStringValue

   .. py:method:: SetAttributionText(attributionText: str) -> None
      :canonical: windows_toasts.toast_document.ToastDocument.SetAttributionText

      .. autodoc2-docstring:: windows_toasts.toast_document.ToastDocument.SetAttributionText

   .. py:method:: SetAudioAttributes(audioConfiguration: windows_toasts.toast_audio.ToastAudio) -> None
      :canonical: windows_toasts.toast_document.ToastDocument.SetAudioAttributes

      .. autodoc2-docstring:: windows_toasts.toast_document.ToastDocument.SetAudioAttributes

   .. py:method:: SetTextField(newValue: str, nodePosition: int) -> None
      :canonical: windows_toasts.toast_document.ToastDocument.SetTextField

      .. autodoc2-docstring:: windows_toasts.toast_document.ToastDocument.SetTextField

   .. py:method:: SetCustomTimestamp(customTimestamp: datetime.datetime) -> None
      :canonical: windows_toasts.toast_document.ToastDocument.SetCustomTimestamp

      .. autodoc2-docstring:: windows_toasts.toast_document.ToastDocument.SetCustomTimestamp

   .. py:method:: SetImageField(imagePath: str) -> None
      :canonical: windows_toasts.toast_document.ToastDocument.SetImageField

      .. autodoc2-docstring:: windows_toasts.toast_document.ToastDocument.SetImageField

   .. py:method:: SetInputField(placeholderText: str) -> None
      :canonical: windows_toasts.toast_document.ToastDocument.SetInputField

      .. autodoc2-docstring:: windows_toasts.toast_document.ToastDocument.SetInputField

   .. py:method:: SetDuration(duration: str) -> None
      :canonical: windows_toasts.toast_document.ToastDocument.SetDuration

      .. autodoc2-docstring:: windows_toasts.toast_document.ToastDocument.SetDuration

   .. py:method:: AddAction(buttonContent: str, arguments: str) -> None
      :canonical: windows_toasts.toast_document.ToastDocument.AddAction

      .. autodoc2-docstring:: windows_toasts.toast_document.ToastDocument.AddAction
