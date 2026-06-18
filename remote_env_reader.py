# -*- coding: utf-8 -*-
import paramiko

host = '101.43.113.117'
password = input("输入远程服务器密码: ")

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, username='root', password=password, timeout=10)

sftp = ssh.open_sftp()
with sftp.file('/root/.env', 'r') as f:
    env_content = f.read().decode('utf-8')

ssh.close()

print("=== 远程 .env 文件内容 ===")
print(env_content)
