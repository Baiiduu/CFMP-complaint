# utils/service_client.py

import httpx
import random
from typing import Dict, Any, Optional
from config.nacos_heartbeat import client


class ServiceClient:
    """
    服务调用客户端，用于调用Nacos注册的其他服务
    """

    @staticmethod
    def get_service_instance(service_name: str) -> Optional[Dict[str, Any]]:
        """
        从Nacos获取服务实例信息

        Args:
            service_name: 服务名称

        Returns:
            服务实例信息字典或None
        """
        try:
            instances = client.list_naming_instance(service_name=service_name)

            if 'hosts' in instances and instances['hosts']:
                # 过滤出健康的实例
                healthy_hosts = [host for host in instances['hosts'] if host.get('healthy', False)]
                if healthy_hosts:
                    # 随机选择一个健康实例（负载均衡）
                    return random.choice(healthy_hosts)

            return None
        except Exception as e:
            print(f"获取服务实例失败: {e}")
            return None

    @staticmethod
    def build_service_url(instance: Dict[str, Any], endpoint: str) -> str:
        """
        构建服务URL

        Args:
            instance: 服务实例信息
            endpoint: 服务端点路径

        Returns:
            完整的服务URL
        """
        ip = instance.get('ip', '')
        port = instance.get('port', '')

        # 确保endpoint以/开头
        if not endpoint.startswith('/'):
            endpoint = '/' + endpoint

        return f"http://{ip}:{port}{endpoint}"

    @classmethod
    def call_service(cls, service_name: str, endpoint: str, method: str = 'GET',
                     params: Dict = None, data: Dict = None, json: Dict = None,
                     timeout: float = 5.0) -> Dict[str, Any]:
        """
        调用其他服务的API

        Args:
            service_name: 目标服务名称
            endpoint: 服务端点路径
            method: HTTP方法 (GET, POST, PUT, DELETE等)
            params: URL参数
            data: 表单数据
            json: JSON数据
            timeout: 超时时间

        Returns:
            服务调用结果
        """
        # 获取服务实例
        instance = cls.get_service_instance(service_name)
        if not instance:
            return {
                "success": False,
                "error": f"未找到可用的服务实例: {service_name}"
            }

        # 构建URL
        url = cls.build_service_url(instance, endpoint)

        try:
            # 发起HTTP请求
            with httpx.Client(timeout=timeout) as client:
                response = client.request(
                    method=method,
                    url=url,
                    params=params,
                    data=data,
                    json=json
                )

                response.raise_for_status()  # 检查HTTP错误

                # 尝试解析JSON响应
                try:
                    result = response.json()
                except:
                    result = {"content": response.text}

                return {
                    "success": True,
                    "data": result,
                    "status_code": response.status_code
                }

        except httpx.ConnectError as e:
            return {
                "success": False,
                "error": f"连接被拒绝: {str(e)}",
                "service_info": {
                    "service_name": service_name,
                    "ip": instance.get('ip'),
                    "port": instance.get('port')
                }
            }
        except httpx.TimeoutException as e:
            return {
                "success": False,
                "error": f"请求超时: {str(e)}",
                "service_info": {
                    "service_name": service_name,
                    "ip": instance.get('ip'),
                    "port": instance.get('port')
                }
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"请求失败: {str(e)}",
                "service_info": {
                    "service_name": service_name,
                    "ip": instance.get('ip'),
                    "port": instance.get('port')
                }
            }

    @classmethod
    def get(cls, service_name: str, endpoint: str, params: Dict = None, timeout: float = 5.0):
        """GET请求快捷方法"""
        return cls.call_service(service_name, endpoint, 'GET', params=params, timeout=timeout)

    @classmethod
    def post(cls, service_name: str, endpoint: str, data: Dict = None, json: Dict = None, timeout: float = 5.0):
        """POST请求快捷方法"""
        return cls.call_service(service_name, endpoint, 'POST', data=data, json=json, timeout=timeout)

    @classmethod
    def put(cls, service_name: str, endpoint: str, data: Dict = None, json: Dict = None, timeout: float = 5.0):
        """PUT请求快捷方法"""
        return cls.call_service(service_name, endpoint, 'PUT', data=data, json=json, timeout=timeout)

    @classmethod
    def delete(cls, service_name: str, endpoint: str, timeout: float = 5.0):
        """DELETE请求快捷方法"""
        return cls.call_service(service_name, endpoint, 'DELETE', timeout=timeout)
