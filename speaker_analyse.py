from custom_types import Node, EnhancedNode, SpeakerInfo
from itertools import chain
from nltk import tokenize, download

# Sets up the punkt tokenizer
download("punkt")

speaker_cache: dict[str, SpeakerInfo] = {}

# I.e for Mr. Speaker do we grab their title or name as the speaker
USE_TITLED_SPEAKERS_NAME_INSTEAD_OF_TITLE = True


def get_speaker_info_from_raw_speaker(raw_speaker: str) -> SpeakerInfo:

    fragments = raw_speaker.split("(")

    match len(fragments):
        case 1:
            # Assume just the persons name is present
            actual_speaker = fragments[0].strip()
            region = ""
            party = ""
        case 2:
            # Assume is a titled role, and just use the speakers title as their name
            if USE_TITLED_SPEAKERS_NAME_INSTEAD_OF_TITLE:
                actual_speaker = fragments[1][0:-1]
            else:
                actual_speaker = fragments[0].strip()
            region = ""
            party = ""

        case 3:
            actual_speaker = fragments[0].strip()
            # Strip off ) from each fragment
            region = fragments[1][:-2]
            party = fragments[2][:-1]
        case _:
            # Should never be more than 3 fragments
            raise ValueError(
                f"Too many fragments generated from speaker line: {raw_speaker}"
            )

    speaker_info = SpeakerInfo(speaker=actual_speaker, region=region, party=party)
    return speaker_info


def add_to_cache(result: Node):

    speaker_info = get_speaker_info_from_raw_speaker(result.speaker)

    # Check if already in cache
    # Add region and party if not already present
    # Error if conflict occurs

    currently_stored_info = speaker_cache.get(speaker_info.speaker, None)

    if currently_stored_info is None or (
        currently_stored_info.region == "" and currently_stored_info.party == ""
    ):
        speaker_cache[speaker_info.speaker] = speaker_info
    else:
        if speaker_info.region != "" or speaker_info.party != "":
            # Check if there is any region or party info
            if speaker_info != currently_stored_info:
                raise ValueError(
                    f"Conflict between currently stored data: {currently_stored_info} and new data: {speaker_info}"
                )


def raw_text_to_sentences(text: list[str]) -> list[str]:

    # Use nltk to split into sentences. Allows handling punctuation, contractions etc correctly
    sentences = list(chain(*[tokenize.sent_tokenize(x) for x in text]))
    return sentences


def enchance_result_node(result: Node) -> EnhancedNode:
    raw_speaker_info = get_speaker_info_from_raw_speaker(result.speaker)
    speaker_info = speaker_cache[raw_speaker_info.speaker]
    processed_text = raw_text_to_sentences(result.text)
    return EnhancedNode(
        speaker=speaker_info.speaker,
        party=speaker_info.party,
        region=speaker_info.region,
        text=processed_text,
    )
