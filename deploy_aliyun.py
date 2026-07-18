#!/usr/bin/env python3
"""
火星简历 · 阿里云自动部署脚本 (v2 - 优化版)
"""

import paramiko
import time
import sys
import socket

HOST = "47.83.4.213"
PORT = 22
USER = "root"
PASSWORD = "Password@123"

COMMANDS = [
    ("更新系统包列表", "apt update -qq"),
    ("升级系统包", "apt upgrade -y -qq 2>/dev/null; echo 'DONE'"),
    ("安装 Git", "apt install -y -qq git 2>/dev/null; echo 'DONE'"),
    ("安装 Docker", """
if ! command -v docker &>/dev/null; then
    curl -fsSL https://get.docker.com | bash
    echo 'DOCKER_INSTALLED'
else
    echo 'DOCKER_ALREADY_EXISTS'
fi
"""),
    ("安装 Docker Compose", """
apt-get install -y -qq docker-compose-plugin 2>/dev/null; echo 'DONE'
"""),
    ("克隆 MarsResume 项目", """
cd /root
if [ -d MarsResume ]; then
    echo 'DIR_EXISTS'
    cd MarsResume && git pull
else
    git clone https://github.com/samkmfc/MarsResume.git
    echo 'CLONED'
fi
"""),
    ("写入 .env 配置", """
cat > /root/MarsResume/.env << 'ENVEOF'
LLM_API_KEY=sk-rM8UXzMeEulrjfeWUwrfGvKBhWgyIykp
LLM_BASE_URL=https://token.sensenova.cn/v1
LLM_MODEL=deepseek-v4-flash
CORS_ORIGINS=http://47.83.4.213
AI_RATE_LIMIT=30
AI_RATE_WINDOW_SEC=3600
SERVER_PORT=8000
ENVEOF
echo 'ENV_CONFIGURED'
"""),
]


def run_ssh():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    print("[连接] 正在连接服务器 {}:{}...".format(HOST, PORT))

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(30)
    sock.connect((HOST, PORT))
    print("[OK] TCP 连接已建立")

    transport = paramiko.Transport(sock)
    transport.connect(
        username=USER,
        password=PASSWORD,
    )
    print("[OK] SSH 认证成功\n")

    ssh._transport = transport

    total = len(COMMANDS)

    for i, (title, cmd) in enumerate(COMMANDS, 1):
        print("[{}/{}] {}...".format(i, total, title))
        print("    $ {}".format(cmd.strip()[:80]))

        stdin, stdout, stderr = ssh.exec_command(cmd, timeout=120)
        exit_code = stdout.channel.recv_exit_status()

        output = stdout.read().decode('utf-8', errors='replace').strip()
        err = stderr.read().decode('utf-8', errors='replace').strip()

        if output:
            for line in output.split('\n')[-3:]:
                print("    {}".format(line.strip()))
        if exit_code == 0:
            print("    [OK]\n")
        else:
            print("    [WARN] exit code: {}".format(exit_code))
            if err:
                print("    [WARN] {}".format(err[:200]))
            print()

    # Docker Compose 构建
    print("[{}/{}] Docker Compose 构建...".format(total+1, total+1))
    stdin, stdout, stderr = ssh.exec_command(
        "cd /root/MarsResume && docker compose build 2>&1",
        timeout=300
    )
    exit_code = stdout.channel.recv_exit_status()
    build_output = stdout.read().decode('utf-8', errors='replace').strip()
    if build_output:
        print("    {}".format(build_output[-500:]))
    if exit_code == 0:
        print("    [OK] 构建完成\n")
    else:
        print("    [WARN] 构建可能有问题\n")

    # Docker Compose 启动
    print("[{}/{}] Docker Compose 启动...".format(total+2, total+2))
    stdin, stdout, stderr = ssh.exec_command(
        "cd /root/MarsResume && docker compose up -d 2>&1",
        timeout=60
    )
    exit_code = stdout.channel.recv_exit_status()
    up_output = stdout.read().decode('utf-8', errors='replace').strip()
    if up_output:
        print("    {}".format(up_output))

    # 检查状态
    time.sleep(3)
    stdin, stdout, stderr = ssh.exec_command(
        "cd /root/MarsResume && docker compose ps 2>&1",
        timeout=30
    )
    stdout.channel.recv_exit_status()
    ps_output = stdout.read().decode('utf-8', errors='replace').strip()
    print("\n    [容器状态]:")
    for line in ps_output.split('\n'):
        print("    {}".format(line))

    # API 健康检查
    time.sleep(5)
    stdin, stdout, stderr = ssh.exec_command(
        "curl -s http://localhost:8000/api/status 2>&1 || echo 'CURL_FAILED'",
        timeout=30
    )
    stdout.channel.recv_exit_status()
    api_check = stdout.read().decode('utf-8', errors='replace').strip()
    print("\n    [API健康检查]:")
    print("    {}".format(api_check))

    ssh.close()
    transport.close()

    print("""
================================================
  部署完成！
================================================

  访问地址: http://47.83.4.213
  API 文档: http://47.83.4.213/api/docs

  注意：请确保阿里云安全组已放行 80 端口！
================================================
""")


if __name__ == "__main__":
    try:
        run_ssh()
    except paramiko.AuthenticationException:
        print("[错误] SSH 认证失败，请检查密码是否正确")
        sys.exit(1)
    except paramiko.SSHException as e:
        print("[错误] SSH 连接失败: {}".format(e))
        sys.exit(1)
    except Exception as e:
        print("[错误] {}".format(e))
        sys.exit(1)