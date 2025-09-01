#!/usr/bin/env python3
# stress_test.py
# coding=utf-8
import requests
import threading
import time
import random
import os

# 从环境变量获取服务地址，如果没有则使用默认值
NODE_IP = os.getenv('NODE_IP', '101.132.163.45')
NODE_PORT = os.getenv('NODE_PORT', '30008')
SERVICE_URL = f"http://{NODE_IP}:{NODE_PORT}"

# 测试参数
NUM_THREADS = 20
REQUESTS_PER_THREAD = 50
REQUEST_DELAY = 0.1  # 秒


def make_request(thread_id):
    """执行HTTP请求"""
    success_count = 0
    error_count = 0

    for i in range(REQUESTS_PER_THREAD):
        try:
            # 模拟不同的API请求

            endpoint = "/api/complaints/"
            response = requests.get(
                f"{SERVICE_URL}{endpoint}",
                timeout=5
            )

            if response.status_code == 200:
                success_count += 1
            else:
                error_count += 1

        except Exception as e:
            error_count += 1
            print(f"线程 {thread_id} 请求失败: {e}")

        # 控制请求频率
        time.sleep(REQUEST_DELAY + random.uniform(0, 0.1))

    print(f"线程 {thread_id} 完成: 成功 {success_count}, 失败 {error_count}")


def main():
    print(f"开始压力测试...")
    print(f"目标地址: {SERVICE_URL}")
    print(f"线程数: {NUM_THREADS}")
    print(f"每线程请求数: {REQUESTS_PER_THREAD}")
    print("=" * 50)

    start_time = time.time()

    # 创建并启动线程
    threads = []
    for i in range(NUM_THREADS):
        thread = threading.Thread(target=make_request, args=(i,))
        threads.append(thread)
        thread.start()
        time.sleep(0.1)  # 线程启动间隔

    # 等待所有线程完成
    for thread in threads:
        thread.join()

    end_time = time.time()

    print("=" * 50)
    print(f"压力测试完成!")
    print(f"总耗时: {end_time - start_time:.2f} 秒")


if __name__ == "__main__":
    main()