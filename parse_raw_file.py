from custom_types import Node, EnhancedNode
from speaker_analyse import add_to_cache, enchance_result_node
from pathlib import Path


KNOWN_BAD_SPEAKERS = ["Division 86", "Hon. Members"]

PUNCTUATION_MARKS = "“;"


def is_good_result(result: EnhancedNode) -> bool:

    if result.text == []:
        return False

    if "rose—" in result.text:
        return False

    # Custom for this text only
    if result.speaker in KNOWN_BAD_SPEAKERS:
        return False

    return True


def parse_file(filepath: Path) -> tuple[str, list[EnhancedNode]]:
    with open(filepath, "r", encoding="utf-8") as f:

        buffer = []
        results: list[Node] = []
        currently_buffering = False
        previous_line_blank = False

        raw_lines = f.read().splitlines()

        # Assume title is always first line of the file
        title = raw_lines[0]

        for line in raw_lines[1:]:
            # Find all words before the first ( in the line.
            potential_speaker_words = line.split("(")[0].split(" ")

            # Skip blank lines
            if line == "":
                previous_line_blank = True
                continue

            if (
                1 < len(potential_speaker_words) < 5
                and previous_line_blank
                and line[0] not in PUNCTUATION_MARKS
                and line[-1] not in PUNCTUATION_MARKS
            ):
                # Speaker found

                if currently_buffering:
                    result = Node(speaker=buffer[0], text=buffer[1:])
                    results.append(result)
                    buffer = []
                else:
                    # Start the buffering from the first speaker line found
                    currently_buffering = True

            if currently_buffering:
                buffer.append(line)

            previous_line_blank = False

        # At the end create a result node with the final speakers text
        result = Node(speaker=buffer[0], text=buffer[1:])
        results.append(result)

    # Adds each result node to the cache with the appropriate speaker info
    # This allows me to fill in the party and region appropriately for nodes without them
    [add_to_cache(x) for x in results]

    # Use that cache of information to get the correct speaker name, party and region for each speaker (where possible)
    enhanced_results = [enchance_result_node(x) for x in results]
    enhanced_results = [result for result in enhanced_results if is_good_result(result)]

    print(f"{len(enhanced_results) = }")

    return title, enhanced_results


if __name__ == "__main__":
    filepath = Path("scotdebate.txt")
    parse_file(filepath)