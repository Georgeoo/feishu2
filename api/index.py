#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
飞书AI机器人 - 极速响应版
"""

import json
import os

# 从环境变量获取API密钥
STEPFUN_API_KEY = os.environ.get("STEPFUN_API_KEY", "")

def handler(request):
    """
    Vercel Serverless Function入口
    """
    method = request.get('method', 'GET')
  
    # GET请求 - 健康检查
    if method == 'GET':
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json; charset=utf-8"},
            "body": json.dumps({
                "status": "ok",
                "message": "狗腿子机器人运行中"
            }, ensure_ascii=False)
        }
  
    # POST请求 - 处理飞书回调
    if method == 'POST':
        try:
            body_str = request.get('body', '{}')
            if isinstance(body_str, str):
                body = json.loads(body_str)
            else:
                body = body_str
          
            # 获取事件类型
            header = body.get('header', {})
            event_type = header.get('event_type', '')
          
            # 1. URL验证事件 - 立即返回challenge
            if event_type == 'url_verification':
                challenge = body.get('challenge', '')
                return {
                    "statusCode": 200,
                    "headers": {"Content-Type": "application/json; charset=utf-8"},
                    "body": json.dumps({"challenge": challenge}, ensure_ascii=False)
                }
          
            # 2. 消息事件 - 立即返回成功，不等待AI处理
            if event_type == 'im.message.receive_v1':
                # 立即返回200，飞书会重试或等待
                return {
                    "statusCode": 200,
                    "headers": {"Content-Type": "application/json; charset=utf-8"},
                    "body": json.dumps({"success": True}, ensure_ascii=False)
                }
          
            # 其他事件
            return {
                "statusCode": 200,
                "headers": {"Content-Type": "application/json; charset=utf-8"},
                "body": json.dumps({"success": True}, ensure_ascii=False)
            }
          
        except Exception as e:
            return {
                "statusCode": 200,
                "headers": {"Content-Type": "application/json; charset=utf-8"},
                "body": json.dumps({"success": False, "error": str(e)}, ensure_ascii=False)
            }
  
    return {
        "statusCode": 405,
        "headers": {"Content-Type": "application/json; charset=utf-8"},
        "body": json.dumps({"error": "Method not allowed"}, ensure_ascii=False)
    }
# HTTP Handler兼容
from http.server import BaseHTTPRequestHandler

class HTTPHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        response = handler({'method': 'GET'})
        self.send_response(response['statusCode'])
        for key, value in response['headers'].items():
            self.send_header(key, value)
        self.end_headers()
        self.wfile.write(response['body'].encode('utf-8'))
  
    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode('utf-8')
      
        response = handler({
            'method': 'POST',
            'body': body
        })
      
        self.send_response(response['statusCode'])
        for key, value in response['headers'].items():
            self.send_header(key, value)
        self.end_headers()
        self.wfile.write(response['body'].encode('utf-8'))