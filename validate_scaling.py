#!/usr/bin/env python3
# validate_scaling.py
import subprocess
import time
import json

def get_pod_count():
    """获取当前Pod数量"""
    try:
        result = subprocess.run([
            "kubectl", "get", "deployment", "complaint-service",
            "-o", "jsonpath={.status.replicas}"
        ], capture_output=True, text=True, check=True)
        return int(result.stdout)
    except Exception as e:
        print(f"获取Pod数量失败: {e}")
        return 0

def get_hpa_status():
    """获取HPA状态"""
    try:
        result = subprocess.run([
            "kubectl", "get", "hpa", "complaint-service-hpa",
            "-o", "json"
        ], capture_output=True, text=True, check=True)
        return json.loads(result.stdout)
    except Exception as e:
        print(f"获取HPA状态失败: {e}")
        return None

def get_pod_metrics():
    """获取Pod资源使用情况"""
    try:
        result = subprocess.run([
            "kubectl", "top", "pods", "-l", "app=complaint-service"
        ], capture_output=True, text=True, check=True)
        return result.stdout
    except Exception as e:
        print(f"获取Pod指标失败: {e}")
        return ""


def main():
    print("开始验证自动扩缩容功能...")
    print("=" * 50)

    # 初始状态
    print(f"初始Pod数量: {get_pod_count()}")
    print("初始HPA状态:")
    hpa_status = get_hpa_status()
    if hpa_status:
        print(f"  当前副本数: {hpa_status.get('status', {}).get('currentReplicas', 'N/A')}")
        print(f"  期望副本数: {hpa_status.get('status', {}).get('desiredReplicas', 'N/A')}")

    print("\n开始监控 (每10秒更新一次)...")
    print("=" * 50)

    # 监控5分钟
    for i in range(30):
        print(f"\n[{i + 1}/30] 监控状态:")
        print(f"  Pod数量: {get_pod_count()}")
        print("  Pod资源使用情况:")
        print(get_pod_metrics())

        hpa_status = get_hpa_status()
        if hpa_status:
            current = hpa_status.get('status', {}).get('currentReplicas', 'N/A')
            desired = hpa_status.get('status', {}).get('desiredReplicas', 'N/A')
            print(f"  HPA状态 - 当前副本: {current}, 期望副本: {desired}")

            # 检查是否有指标
            if 'currentMetrics' in hpa_status.get('status', {}):
                metrics = hpa_status['status']['currentMetrics']
                for metric in metrics:
                    if 'resource' in metric:
                        name = metric['resource'].get('name', 'N/A')
                        current_value = metric['resource'].get('current', {}).get('averageUtilization', 'N/A')
                        print(f"    {name} 使用率: {current_value}%")

        if i < 29:  # 避免最后一次sleep
            time.sleep(10)

    print("\n" + "=" * 50)
    print("监控完成!")


if __name__ == "__main__":
    main()