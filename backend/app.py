from flask import Flask, request, jsonify
from agent_manager import AgentManager
from vector_manager import VectorManager
import time

app = Flask(__name__)

# managers
agent = AgentManager()
vector = VectorManager()

# track uptime
START_TIME = time.time()

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    query = data.get("query")
    model = data.get("model", "deepseek")
    response = agent.handle_query(query, model=model)
    return jsonify(response)

@app.route("/health", methods=["GET"])
def health():
    uptime = round(time.time() - START_TIME, 2)
    return jsonify({
        "status": "ok",
        "uptime_seconds": uptime,
        "version": "1.0.0"
    })

@app.route("/intents", methods=["POST"])
def intents():
    data = request.json
    query = data.get("query")
    intent = agent.detect_intent(query)  # assumes you expose detect_intent in AgentManager
    return jsonify({
        "query": query,
        "intent": intent
    })

@app.route("/search", methods=["POST"])
def search():
    data = request.json
    query = data.get("query")
    k = data.get("k", 5)
    results = vector.search(query, k=k)
    return jsonify({
        "query": query,
        "results": results
    })

# ----------------------

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
