#!/bin/bash
# start-k8s.sh

echo "启动 CFMP Kubernetes 应用..."

# 启动 minikube
echo "启动 minikube..."
minikube start

# 配置 Docker 环境
echo "配置 Docker 环境..."
eval $(minikube docker-env)

# 构建镜像
echo "构建投诉服务镜像..."
docker build -t complaint-service .

# 部署应用
echo "部署应用..."
minikube kubectl -- delete -f k8s/ --ignore-not-found=true
sleep 3
minikube kubectl -- apply -f k8s/

# 等待启动
echo "等待应用启动..."
minikube kubectl -- wait --for=condition=ready pod -l app=complaint-service --timeout=300s
minikube kubectl -- wait --for=condition=ready pod -l app=complaint-db --timeout=300s

# 运行数据库迁移
echo "运行数据库迁移..."
minikube kubectl -- exec deployment/complaint-service -- python manager.py migrate

# 显示访问地址
echo ""
echo "部署完成！访问地址："
echo "服务: $(minikube service complaint-service --url)"
echo ""
minikube kubectl -- get pods
minikube kubectl -- get services
