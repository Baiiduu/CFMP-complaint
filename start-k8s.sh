#!/bin/bash
# start-k8s.sh

echo "启动 CFMP Kubernetes 应用..."

# 构建镜像
echo "构建投诉服务镜像..."
docker build -t complaint-service .

export KUBECTL="k3s kubectl"

docker save complaint-service:latest > complaint-service.tar

echo "将镜像导入 K3s..."
k3s ctr images import complaint-service.tar

docker save mysql:8.0 > mysql.tar
echo "将镜像导入 K3s..."
k3s ctr images import mysql.tar

# 部署数据库
echo "部署数据库..."
$KUBECTL delete -f k8s/complaint-deployment.yaml --ignore-not-found=true 2>/dev/null || true
sleep 3

# 只部署数据库相关资源（创建一个临时文件只包含数据库部分）
$KUBECTL apply -f k8s/complaint-deployment.yaml -l app=complaint-db

# 等待数据库启动
echo "等待数据库启动..."
$KUBECTL wait --for=condition=ready pod -l app=complaint-db --timeout=300s 2>/dev/null || true

# 更完善的数据库等待逻辑
echo "等待数据库完全启动..."
max_attempts=30
attempt=0

while [ $attempt -lt $max_attempts ]; do
    if $KUBECTL exec deployment/complaint-db -- mysqladmin ping -h localhost -u root -p'123456' --silent >/dev/null 2>&1; then
        echo "数据库已准备就绪"
        break
    fi
    echo "等待数据库启动... ($((attempt+1))/$max_attempts)"
    attempt=$((attempt+1))
    sleep 10
done

if [ $attempt -eq $max_attempts ]; then
    echo "错误: 数据库启动超时"
    $KUBECTL get pods
    $KUBECTL describe pod -l app=complaint-db
    exit 1
fi

# 现在部署complaint-service
echo "部署投诉服务..."
$KUBECTL apply -f k8s/complaint-deployment.yaml -l app=complaint-service

# 等待complaint-service启动
echo "等待投诉服务启动..."
$KUBECTL wait --for=condition=ready pod -l app=complaint-service --timeout=300s 2>/dev/null || true

# 等待几秒钟确保数据库完全可用
sleep 10

# 添加应用连接失败重试机制
echo "验证应用与数据库的连接..."
max_app_attempts=15
app_attempt=0
while [ $app_attempt -lt $max_app_attempts ]; do
    if $KUBECTL exec deployment/complaint-service -- python manage.py shell -c "from django.db import connection; connection.ensure_connection()" >/dev/null 2>&1; then
        echo "应用成功连接到数据库"
        break
    fi
    echo "应用连接数据库失败，等待重试... ($((app_attempt+1))/$max_app_attempts)"
    app_attempt=$((app_attempt+1))
    sleep 10
done

if [ $app_attempt -eq $max_app_attempts ]; then
    echo "错误: 应用无法连接到数据库"
    $KUBECTL logs deployment/complaint-service
    exit 1
fi

# 运行数据库迁移
echo "运行数据库迁移..."
$KUBECTL exec deployment/complaint-service -- python manage.py migrate

# 显示访问地址
echo ""
echo "部署完成！访问地址："
echo "服务端口: 30008 (NodePort)"
echo ""
$KUBECTL get pods
$KUBECTL get services
