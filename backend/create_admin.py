"""创建管理员账号脚本"""
import sqlite3
import bcrypt
import os
from datetime import datetime, timedelta

DB_PATH = os.path.join(os.path.dirname(__file__), "predictedge.db")

def create_admin():
    admin_username = "admin"
    admin_password = "Li18926677747@"
    admin_email = "Li18926677747@hotmail.com"
    
    password_hash = bcrypt.hashpw(admin_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # 检查admin是否已存在
    c.execute("SELECT id FROM users WHERE username = ?", (admin_username,))
    existing = c.fetchone()
    
    if existing:
        print(f"管理员账号 {admin_username} 已存在，正在重置密码...")
        c.execute("""
            UPDATE users 
            SET password_hash = ?, 
                subscription_tier = 'agency',
                subscription_end_date = ?
            WHERE username = ?
        """, (
            password_hash,
            (datetime.utcnow() + timedelta(days=365*10)).isoformat(),
            admin_username
        ))
        print("密码重置成功！")
    else:
        print(f"正在创建管理员账号 {admin_username}...")
        c.execute("""
            INSERT INTO users 
            (username, email, password_hash, subscription_tier, subscription_end_date, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            admin_username,
            admin_email,
            password_hash,
            "agency",
            (datetime.utcnow() + timedelta(days=365*10)).isoformat(),
            datetime.utcnow().isoformat()
        ))
        print("管理员账号创建成功！")
    
    conn.commit()
    conn.close()
    
    print("\n" + "="*50)
    print("  管理员账号信息")
    print("="*50)
    print(f"  用户名: {admin_username}")
    print(f"  密码: {admin_password}")
    print(f"  权限: 机构版 (最高权限)")
    print(f"  有效期: 10年")
    print("="*50)
    print("\n请妥善保管密码，登录后建议及时修改！")

if __name__ == "__main__":
    create_admin()
