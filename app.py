import os
import uuid

from flask import Flask, jsonify, request
from flask_cors import CORS

import scubatrace

app = Flask(__name__)
CORS(app)

# 设置静态文件路径
app.config["UPLOAD_FOLDER"] = "static/cfgs"


# 确保UPLOAD_FOLDER目录存在
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)


def mock_generate_cfg(code):
    """模拟生成 CFG 图像并返回图像路径"""
    # 这里应该调用实际生成 CFG 图像的逻辑
    filename = f"{uuid.uuid4()}.png"
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)

    # 模拟生成一个图片文件
    with open(filepath, "wb") as f:
        f.write(os.urandom(1024))  # 写入随机字节来模拟图片文件

    return filepath


@app.route("/api/generate-cfg", methods=["POST"])
def generate_cfg():
    try:
        data = request.get_json()
        code = data.get("code", "")
        if not code:
            return jsonify({"success": False, "message": "代码不能为空"})

        # 调用图像生成函数
        cfg_path = mock_generate_cfg(code)

        # 返回图像的相对路径给前端
        cfg_url = f"/{cfg_path}"

        return jsonify({"success": True, "cfgImageUrl": cfg_url})
    except Exception as e:
        print(f"Error occurred: {e}")
        return jsonify({"success": False, "message": "服务器发生错误"})


if __name__ == "__main__":
    app.run(debug=True)
