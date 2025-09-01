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
$KUBECTL apply -f k8s/complaint-deployment.yaml

# 等待启动
echo "等待应用启动..."
$KUBECTL wait --for=condition=ready pod -l app=complaint-service --timeout=300s 2>/dev/null || true
$KUBECTL wait --for=condition=ready pod -l app=complaint-db --timeout=300s 2>/dev/null || true


# 更完善的数据库等待逻辑
echo "等待数据库完全启动..."
max_attempts=30
attempt=0

while [ $attempt -lt $max_attempts ]; do
    if $KUBECTL exec deployment/complaint-db -- mysqladmin ping -h localhost -u root -p'xzw2qwQ~' --silent >/dev/null 2>&1; then
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

  max_app_attempts=10
   app_attempt=0
   while [ $app_attempt -lt $max_app_attempts ]; do
       if $KUBECTL exec deployment/complaint-service -- python manage.py shell -c "from django.db import connection; connection.ensure_connection()"; then
           echo "应用数据库连接成功"
           break
       fi
       echo "等待应用连接数据库... ($((app_attempt+1))/$max_app_attempts)"
       app_attempt=$((app_attempt+1))
       sleep 10
   done
# 等待几秒钟确保数据库完全可用
sleep 30

# 运行数据库迁移
echo "运行数据库迁移..."
$KUBECTL exec deployment/complaint-service -- python manage.py migrate


# 显示访问地址
echo ""
echo "部署完成！访问地址："
echo "服务端口: 30080 (NodePort)"
echo ""
$KUBECTL get pods
$KUBECTL get services
