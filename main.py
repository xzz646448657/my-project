import os
from flask import Flask, request
from flask_cors import CORS  # 解决跨域问题，前端/第三方调用无报错
import Demo3

# 初始化Flask应用（Render部署固定配置）
app = Flask(__name__)
CORS(app)  # 允许所有跨域请求


# ====================== 👇 在这里替换成你的业务代码 👇 ======================
def handle_business(json_data: dict) -> str:
    """
    你的业务逻辑函数
    :param json_data: 前端/用户传入的JSON数据（Python字典格式）
    :return: 必须返回 字符串 （符合你的需求）
    """
    # ------------------- 示例代码（删除后替换为你的代码） -------------------
    # 示例：解析传入的JSON，返回处理后的字符串
    resultStr = Demo3.main_with_base64(json_data)
    return f"业务处理完成！接收到的数据："+resultStr
    # -------------------------------------------------------------------
# ======================================================================

# 定义POST接口（用户调用的API地址）
@app.route("/api", methods=["POST"])
def api_endpoint():
    try:
        # 1. 获取用户POST提交的JSON数据
        request_data = request.get_json()

        # 2. 校验数据是否为空
        if not request_data:
            return "错误：请传入合法的JSON数据", 400

        # 3. 调用你的业务代码
        result = handle_business(request_data)
        # 4. 直接返回字符串（满足你的需求）
        return result

    # 全局异常捕获，返回错误字符串
    except Exception as e:
        return f"服务器异常：{str(e)}", 500


# Render部署必须的启动配置（固定写法，不要修改）
if __name__ == "__main__":
    server_port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=server_port, debug=False)
