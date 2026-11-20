from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from enum import Enum

from .wrappers import ToastImage


class ToastTextStyle(Enum):
    """
    Styles for :class:`ToastText`, which control font size, weight, and opacity. Subtle opacity is 60% opaque.
    Descriptions are from `Microsoft's documentation
    <https://learn.microsoft.com/windows/apps/develop/notifications/app-notifications/app-notifications-schema#adaptivetextstyle>`_
    """

    Default = ""
    """Style is determined by the renderer"""
    Caption = "caption"
    """Smaller than paragraph font size"""
    CaptionSubtle = "captionSubtle"
    """Same as Caption but with subtle opacity"""
    Body = "body"
    """Paragraph font size"""
    BodySubtle = "bodySubtle"
    """Same as Body but with subtle opacity"""
    Base = "base"
    """Paragraph font size, bold weight. Essentially the bold version of Body"""
    BaseSubtle = "baseSubtle"
    """Same as Base but with subtle opacity"""
    Subtitle = "subtitle"
    """H4 font size"""
    SubtitleSubtle = "subtitleSubtle"
    """Same as Subtitle but with subtle opacity"""
    Title = "title"
    """H3 font size"""
    TitleSubtle = "titleSubtle"
    """Same as Title but with subtle opacity"""
    TitleNumeral = "titleNumeral"
    """Same as Title but with top/bottom padding reduced"""
    TitleNumeralSubtle = "titleNumeralSubtle"
    """Same as TitleNumeral but with subtle opacity"""
    Subheader = "subheader"
    """H2 font size"""
    SubheaderSubtle = "subheaderSubtle"
    """Same as Subheader but with subtle opacity"""
    SubheaderNumeral = "subheaderNumeral"
    """Same as Subheader but with top/bottom padding reduced"""
    SubheaderNumeralSubtle = "subheaderNumeralSubtle"
    """Same as SubheaderNumeral but with subtle opacity"""
    Header = "header"
    """H1 font size"""
    HeaderSubtle = "headerSubtle"
    """Same as Header but with subtle opacity"""
    HeaderNumeral = "headerNumeral"
    """Same as Header but with top/bottom padding reduced"""
    HeaderNumeralSubtle = "headerNumeralSubtle"
    """Same as HeaderNumeral but with subtle opacity"""


class ToastTextAlign(Enum):
    """
    Horizontal alignments for :class:`ToastText`
    """

    Default = ""
    Left = "left"
    Center = "center"
    Right = "right"


class ToastImageAlign(Enum):
    """
    Horizontal alignments for :class:`ToastGroupImage`
    """

    Default = ""
    Stretch = "stretch"
    Left = "left"
    Center = "center"
    Right = "right"


class ToastTextStacking(Enum):
    """
    Vertical alignments for the content of a :class:`ToastSubgroup`
    """

    Default = ""
    Top = "top"
    Center = "center"
    Bottom = "bottom"


@dataclass
class ToastText:
    """
    Styled text inside a :class:`ToastSubgroup`
    """

    text: str
    """The text to display"""
    style: ToastTextStyle = ToastTextStyle.Default
    """The size, weight and opacity of the text"""
    align: ToastTextAlign = ToastTextAlign.Default
    """How to align the text horizontally"""
    wrap: bool = False
    """Whether to wrap the text onto more lines, rather than cutting it off"""
    max_lines: int | None = None
    """The most lines the text can take up"""
    min_lines: int | None = None
    """The fewest lines the text takes up, even if it's shorter"""


@dataclass
class ToastGroupImage:
    """
    An image inside a :class:`ToastSubgroup`
    """

    image: ToastImage
    """An image file"""
    alt_text: str | None = None
    """A description of the image, for users of assistive technologies"""
    circle_crop: bool = False
    """Whether to crop the image as a circle"""
    remove_margin: bool = False
    """Whether to remove the space between the image and the content above it"""
    align: ToastImageAlign = ToastImageAlign.Default
    """How to align the image horizontally"""


@dataclass
class ToastSubgroup:
    """
    A column inside a :class:`ToastGroup`, holding text and images
    """

    content: Sequence[ToastText | ToastGroupImage]
    """The text and images in the column, from top to bottom"""
    weight: int | None = None
    """
    The width of the column relative to the others in its group. For example, a column with a weight of 2 is twice as
    wide as one with a weight of 1. If no column in the group has a weight, they share the width equally. Give either
    all of a group's columns a weight or none, since a column without one takes up the width its content needs and
    can squeeze the others to nothing
    """
    text_stacking: ToastTextStacking = ToastTextStacking.Default
    """How to align the column's content vertically"""


@dataclass
class ToastGroup:
    """
    A row of columns, shown below a toast's text. Only works on
    :class:`~windows_toasts.toasters.InteractableWindowsToaster`
    """

    subgroups: Sequence[ToastSubgroup]
    """The columns in the row, from left to right"""
