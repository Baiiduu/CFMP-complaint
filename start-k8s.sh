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

# 部署应用
echo "部署应用..."
$KUBECTL delete -f k8s/ --ignore-not-found=true 2>/dev/null || true
sleep 3
$KUBECTL apply -f k8s/

# 等待启动
echo "等待应用启动..."
$KUBECTL wait --for=condition=ready pod -l app=complaint-service --timeout=300s 2>/dev/null || true
$KUBECTL wait --for=condition=ready pod -l app=complaint-db --timeout=300s 2>/dev/null || true

sleep 10

until $KUBECTL exec deployment/complaint-db -- mysqladmin ping -h localhost -u root -p'xzw2qwQ~' --silent; do
    echo "等待数据库连接..."
    sleep 5
done
# 运行数据库迁移
echo "运行数据库迁移..."
$KUBECTL exec deployment/complaint-service -- python manager.py migrate

# 显示访问地址
echo ""
echo "部署完成！访问地址："
echo "服务端口: 30080 (NodePort)"
echo ""
$KUBECTL get pods
$KUBECTL get services
