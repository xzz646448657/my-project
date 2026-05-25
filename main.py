import os
from flask import Flask, request
from flask_cors import CORS
import Demo3

app = Flask(__name__)
CORS(app)

def handle_business(json_data: dict) -> str:
    resultStr = Demo3.main_with_base64(json_data)
    return resultStr

@app.route("/api", methods=["POST"])
def api_endpoint():
    try:
        # 1. 获取JSON
        request_data = request.get_json()
        # 2. 判空
        if not request_data:
            return "错误：请传入合法的JSON数据", 400
        # 3. 执行业务
        result = handle_business(request_data)
        # 4. 返回结果
        return result
    # ====================== 修复：缩进正确！======================
    except Exception as e:
        return f"服务器异常：{str(e)}", 500

@app.route("/", methods=["GET"])
def test():
    return "部署成功！服务运行正常！"

if __name__ == "__main__":
    server_port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=server_port, debug=False)