import win32crypt
import base64
import json
import os
import settings


class CredentialManager:
    def __init__(self):
        self.creds_file = os.path.join(settings.USER_DATA_DIR, 'creds.dat')

    def encrypt_data(self, data: str) -> str:
        """使用 DPAPI 加密数据"""
        # 转换为字节并加密
        encrypted = win32crypt.CryptProtectData(
            data.encode('utf-16-le'),  # Windows 使用 UTF-16LE
            None,  # 可选描述
            None,  # 可选额外熵
            None,  # 保留
            None,  # 使用默认提示
        )
        return base64.b64encode(encrypted).decode('utf-8')

    def decrypt_data(self, encrypted_data: str) -> str:
        """使用 DPAPI 解密数据"""
        # 解码并解密
        decrypted = win32crypt.CryptUnprotectData(
            base64.b64decode(encrypted_data),
            None,
            None,
            None,
        )
        return decrypted[1].decode('utf-16-le')

    def save_credentials(self, username: str, password: str, remember_state: bool):
        """安全保存凭证"""
        encrypted_username = self.encrypt_data(username)
        encrypted_password = self.encrypt_data(password)

        if not encrypted_username or not encrypted_password:
            return False

        # 创建安全存储结构
        creds = {
            "username": encrypted_username,
            "password": encrypted_password,
            "remember_state": remember_state,
        }

        with open(self.creds_file, 'w') as f:
            json.dump(creds, f)
        # 设置文件权限 (Windows)
        os.chmod(self.creds_file, 0o600)  # 仅当前用户可读写
        return True


    def load_credentials(self):
        """加载保存的凭证"""
        if not os.path.exists(self.creds_file):
            return "", "", False
        with open(self.creds_file, 'r') as f:
            creds = json.load(f)

        username = self.decrypt_data(creds["username"])
        password = self.decrypt_data(creds["password"])
        remember_state = creds["remember_state"]
        return username, password, remember_state


    def clear_credentials(self):
        """清除保存的凭证"""
        if os.path.exists(self.creds_file):
            os.remove(self.creds_file)
        return True

if __name__ == '__main__':
    launch = CredentialManager()
    # launch.save_credentials("123","456",True)
    username, password ,remember_state = launch.load_credentials()
    print(username, password, remember_state)