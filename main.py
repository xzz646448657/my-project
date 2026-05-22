import os
from flask import Flask, request, jsonify
from Demo3 import process_document_logic

app = Flask(__name__)


@app.route('/api/generate', methods=['POST'])
def generate():
    try:
        # 获取 Coze 传入的 JSON 参数
        params = request.get_json()
        if not params:
            return jsonify({"error": "Missing JSON body"}), 400

        # 调用业务逻辑，返回 String
        result_str = process_document_logic(params)

        return jsonify({
            "code": 200,
            "message": "Success",
            "data": result_str  # 这里就是您要输出的 String
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)