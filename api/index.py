from http.server import BaseHTTPRequestHandler
import json
import os
import requests

# 从环境变量获取API密钥
STEPFUN_API_KEY = os.environ.get("STEPFUN_API_KEY", "")

def call_stepfun(message):
    """调用阶跃星辰AI"""
    try:
        if not STEPFUN_API_KEY:
            return "错误：未配置STEPFUN_API_KEY环境变量"
      
        response = requests.post(
            "https://api.stepfun.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {STEPFUN_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "step-1-8k",
                "messages": [{"role": "user", "content": message}],
                "temperature": 0.7
            },
            timeout=30
        )
      
        if response.status_code == 200:
            result = response.json()
            return result['choices'][0]['message']['content']
        else:
            return f"AI调用失败: HTTP {response.status_code}"
    except Exception as e:
        return f"AI调用出错: {str(e)}"

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """处理GET请求 - 用于健康检查"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json; charset=utf-8')
        self.end_headers()
      
        response = {
            "status": "ok",
            "message": "飞书AI机器人服务运行中",
            "api_key_configured": bool(STEPFUN_API_KEY)
        }
        self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
  
    def do_POST(self):
        """处理POST请求 - 处理飞书消息"""
        try:
            # 读取请求体
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length == 0:
                self._send_error(400, "请求体为空")
                return
          
            post_data = self.rfile.read(content_length)
            body = json.loads(post_data.decode('utf-8'))
          
            # 获取用户消息
            user_message = body.get("message", "")
            if not user_message:
                self._send_error(400, "message字段不能为空")
                return
          
            # 调用AI获取回复
            ai_reply = call_stepfun(user_message)
          
            # 返回成功响应
            self.send_response(200)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.end_headers()
          
            response = {
                "reply": ai_reply,
                "message_type": "text",
                "success": True
            }
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
          
        except json.JSONDecodeError:
            self._send_error(400, "JSON解析失败")
        except Exception as e:
            self._send_error(500, f"服务器错误: {str(e)}")
  
    def _send_error(self, code, message):
        """发送错误响应"""
        self.send_response(code)
        self.send_header('Content-type', 'application/json; charset=utf-8')
        self.end_headers()
      
        response = {
            "error": message,
            "success": False
        }
        self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))