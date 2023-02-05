import pinyin
import Levenshtein
import statistics


class RuleCheckResult:
    def __init__(self, name: str, log: str, result: float = 1, confidence: float = 1):
        self.name = name
        self.log = log
        self.result = result
        self.confidence = confidence


def test_reading_ref(lang: str, ref_reading: str, user_reading: str, confidence: float = 1) -> RuleCheckResult:
    """
    Compare the text user has read with the reference text

    :param lang: specified language code to apply specific rules to user reading
    :param ref_reading: reading to compare with
    :param user_reading: user reading in a latin variant
    :param confidence: stt-engine confidence
    """

    if lang == "cn":
        user_reading = pinyin.get(user_reading)
    result = Levenshtein.ratio(ref_reading, user_reading)

    return RuleCheckResult("Comparing ref reading and computer analysis result of user's speech",
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
    name = f"Total result (confidence is {confidence * 100})%:"

    return RuleCheckResult(name, log, result, confidence)
