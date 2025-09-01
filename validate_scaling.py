#!/usr/bin/env python3
# validate_scaling.py
# coding=utf-8
import subprocess
import time
import json
import sys

def get_pod_count():
    """获取当前Pod数量"""
    try:
        # Python 3.6.8 兼容版本，不使用 capture_output
        result = subprocess.run([
            "kubectl", "get", "deployment", "complaint-service",
            "-o", "jsonpath={.status.replicas}"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        if result.returncode == 0:
            return int(result.stdout.strip())
        else:
            print("获取Pod数量失败: " + result.stderr.strip())
            return 0
    except Exception as e:
        print("获取Pod数量失败: " + str(e))
        return 0

def get_hpa_status():
    """获取HPA状态"""
    try:
        # Python 3.6.8 兼容版本
        result = subprocess.run([
            "kubectl", "get", "hpa", "complaint-service-hpa",
            "-o", "json"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        if result.returncode == 0:
            return json.loads(result.stdout)
        else:
            print("获取HPA状态失败: " + result.stderr.strip())
            return None
    except Exception as e:
        print("获取HPA状态失败: " + str(e))
        return None

def get_pod_metrics():
    """获取Pod资源使用情况"""
    try:
        # Python 3.6.8 兼容版本
        result = subprocess.run([
            "kubectl", "top", "pods", "-l", "app=complaint-service"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        if result.returncode == 0:
            return result.stdout
        else:
            print("获取Pod指标失败: " + result.stderr.strip())
            return ""
    except Exception as e:
        print("获取Pod指标失败: " + str(e))
        return ""


def main():
    print("开始验证自动扩缩容功能...")
    print("=" * 50)

    # 初始状态
    print("初始Pod数量: {0}".format(get_pod_count()))
    print("初始HPA状态:")
    hpa_status = get_hpa_status()
    if hpa_status:
        current_replicas = hpa_status.get('status', {}).get('currentReplicas', 'N/A')
        desired_replicas = hpa_status.get('status', {}).get('desiredReplicas', 'N/A')
        print("  当前副本数: {0}".format(current_replicas))
        print("  期望副本数: {0}".format(desired_replicas))

    print("\n开始监控 (每10秒更新一次)...")
    print("=" * 50)

    # 监控5分钟
    for i in range(30):
        print("\n[{0}/{1}] 监控状态:".format(i + 1, 30))
        print("  Pod数量: {0}".format(get_pod_count()))
        print("  Pod资源使用情况:")
        metrics = get_pod_metrics()
        if metrics:
            print(metrics)
        else:
            print("  暂无数据")

        hpa_status = get_hpa_status()
        if hpa_status:
            current = hpa_status.get('status', {}).get('currentReplicas', 'N/A')
            desired = hpa_status.get('status', {}).get('desiredReplicas', 'N/A')
            print("  HPA状态 - 当前副本: {0}, 期望副本: {1}".format(current, desired))

            # 检查是否有指标
            if 'currentMetrics' in hpa_status.get('status', {}):
                metrics = hpa_status['status']['currentMetrics']
                for metric in metrics:
                    if 'resource' in metric:
                        name = metric['resource'].get('name', 'N/A')
                        current_value = metric['resource'].get('current', {}).get('averageUtilization', 'N/A')
                        print("    {0} 使用率: {1}%".format(name, current_value))

        if i < 29:  # 避免最后一次sleep
            time.sleep(10)

    print("\n" + "=" * 50)
    print("监控完成!")


if __name__ == "__main__":
    main()
