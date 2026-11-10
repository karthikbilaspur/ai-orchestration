"""Sentiment Agent."""
import re
POS = {"love","great","excellent","amazing","awesome","perfect","fantastic","happy","good","best","smooth","fast","helpful","impressed","recommend","satisfied","easy","beautiful"}
NEG = {"bad","terrible","awful","poor","worst","disappointed","angry","frustrated","broken","defective","late","slow","rude","useless","damaged","missing","wrong","refund","cancel","hate","annoying"}
def classify(text):
    words = set(re.findall(r"[a-z]+", text.lower()))
    score = len(words & POS) - len(words & NEG)
    return "positive" if score > 0 else "negative" if score < 0 else "neutral"
def run(reviews):
    results = [{"id": r["id"], "sentiment": classify(r["text"])} for r in reviews]
    dist = {s: sum(1 for x in results if x["sentiment"] == s) for s in ["positive","negative","neutral"]}
    return {"agent": "sentiment", "distribution": dist, "details": results}
