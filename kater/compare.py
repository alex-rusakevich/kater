import pinyin
import Levenshtein
import statistics
import re


class RuleCheckResult:
    def __init__(self, name: str, log: str, result: float = 1, confidence: float = 1):
        self.name = name
        self.log = log
        self.result = result
        self.confidence = confidence


def test_reading_levenstein(lang: str, ref_reading: str, user_reading: str, confidence: float = 1) -> RuleCheckResult:
    """
    Compare the text user has read with the reference text

    :param lang: specified language code to apply specific rules to user reading
    :param ref_reading: reading to compare with
    :param user_reading: user reading in a latin variant
    :param confidence: stt-engine confidence
    """

    def remove_spaces(text_in: str) -> str:
        if lang == "cn":
            words = text_in.split()
            if len(words) == 0:
                return ""
            elif len(words) == 1:
                return words[0]

            all_words_str = words[0].lower()

            for word in text_in.split()[1:]:
                if (all_words_str[-1] == "n" and word[0] == "g") or word[0].lower() not in "bcdfghjklmnpqrstvwxyz":
                    all_words_str += "'"
                all_words_str += word.lower()

            return all_words_str
        else:
            return re.sub(r"\s", "", text_in)

    if lang == "cn":
        user_reading = pinyin.get(user_reading)

    ref_reading_mass = remove_spaces(
        ref_reading)
    user_reading_mass = remove_spaces(user_reading)

    result = Levenshtein.ratio(ref_reading_mass, user_reading_mass)

    return RuleCheckResult("Comparing ref reading and computer analysis result of user's speech using Levenstein distance",
                           f"""Language: {lang}
Ref reading: {ref_reading}
User reading: {user_reading}
Levenstein distance ratio: {result}
Confidence: {confidence * 100}%""", result, confidence)


def calc_total_result(rules_results: [RuleCheckResult,]) -> RuleCheckResult:
    result = []
    confidence = []
    name = ""
    log = ""

    for rule_result in rules_results:
        result.append(rule_result.result)
        confidence.append(rule_result.confidence)
        log = f"{log}\n\n{rule_result.name}:\n{rule_result.log}"

    log = log.strip()
    result = statistics.mean(result)
    confidence = statistics.mean(confidence)

    # Giving points for VOSK confidence, bad mic etc (5% max)
    additional_points = (
        1 - confidence if (1 - confidence) < 0.5 else 0.5) / 10
    result += additional_points
    if result > 1.0:
        result = 1.0
    log = f"{log}\n\nAdditional points for confidence (5% max): {additional_points * 100}%"

    name = f"Total result (confidence is {confidence * 100}%): {result * 100}%"

    return RuleCheckResult(name, log, result, confidence)
