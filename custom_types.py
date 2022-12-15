from typing import NamedTuple

class Node(NamedTuple):
    speaker: str
    text: list[str]

class SpeakerInfo(NamedTuple):
    speaker: str
    region: str
    party: str

    
class EnhancedNode(NamedTuple):
    speaker: str
    region: str
    party: str
    text: list[str]