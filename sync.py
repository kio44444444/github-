"""
Git 协同同步管理网页工具
跨端代码同步利器 - 公司/家两用
作者: Claude Code
"""

import os
import subprocess
import json
from datetime import datetime
from pathlib import Path
import streamlit as st

# 页面配置 - 必须在第一个 st 命令之前
st.set_page_config(
    page_title="Git 同步工具",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义 CSS - Tailwind 风格 + 深色模式
st.markdown("""
<style>
    /* 全局样式 - 深色主题 */
    .main {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        color: #eaeaea;
        min-height: 100vh;
    }

    /* 标题样式 */
    .title-container {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 1rem;
    }

    .subtitle {
        text-align: center;
        color: #a0aec0;
        font-size: 1rem;
        margin-bottom: 2rem;
    }

    /* 卡片容器 */
    .status-card {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 0.5rem 0;
        border: 1px solid rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
    }

    .status-card:hover {
        border-color: rgba(102, 126, 234, 0.5);
        transform: translateY(-2px);
    }

    /* 状态指示器 */
    .status-badge {
        display: inline-block;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.9rem;
        margin: 0.25rem;
    }

    .status-success {
        background: linear-gradient(135deg, #48bb78 0%, #38a169 100%);
        color: white;
    }

    .status-warning {
        background: linear-gradient(135deg, #ed8936 0%, #dd6b20 100%);
        color: white;
    }

    .status-danger {
        background: linear-gradient(135deg, #f56565 0%, #e53e3e 100%);
        color: white;
    }

    .status-info {
        background: linear-gradient(135deg, #4299e1 0%, #3182ce 100%);
        color: white;
    }

    /* 按钮样式 */
    .stButton > button {
        width: 100%;
        padding: 0.75rem 1.5rem;
        border-radius: 8px;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
        margin: 0.25rem 0;
    }

    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
    }

    .stButton > button[kind="primary"]:hover {
        transform: scale(1.02);
        box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
    }

    .stButton > button[kind="secondary"] {
        background: linear-gradient(135deg, #48bb78 0%, #38a169 100%);
        color: white;
        border: none;
    }

    /* 控制台输出区域 */
    .console-container {
        background: #0d1117;
        border-radius: 8px;
        padding: 1rem;
        margin-top: 1rem;
        font-family: 'Courier New', monospace;
        font-size: 0.85rem;
        max-height: 400px;
        overflow-y: auto;
        border: 1px solid #30363d;
    }

    .console-line {
        padding: 0.25rem 0;
        border-bottom: 1px solid #21262d;
    }

    .console-command {
        color: #58a6ff;
    }

    .console-output {
        color: #8b949e;
    }

    .console-error {
        color: #f85149;
    }

    .console-success {
        color: #3fb950;
    }

    /* 提示框 */
    .info-box {
        background: rgba(66, 153, 225, 0.1);
        border-left: 4px solid #4299e1;
        padding: 1rem;
        border-radius: 4px;
        margin: 1rem 0;
    }

    .warning-box {
        background: rgba(237, 137, 54, 0.1);
        border-left: 4px solid #ed8936;
        padding: 1rem;
        border-radius: 4px;
        margin: 1rem 0;
    }

    .error-box {
        background: rgba(245, 101, 101, 0.1);
        border-left: 4px solid #f56565;
        padding: 1rem;
        border-radius: 4px;
        margin: 1rem 0;
    }

    /* 文件列表 */
    .file-list {
        background: rgba(0, 0, 0, 0.2);
        border-radius: 8px;
        padding: 1rem;
        margin-top: 0.5rem;
    }

    .file-item {
        padding: 0.5rem;
        margin: 0.25rem 0;
        background: rgba(255, 255, 255, 0.03);
        border-radius: 4px;
        font-family: 'Courier New', monospace;
        font-size: 0.85rem;
    }

    /* 侧边栏 */
    .css-1d391kg {
        background: rgba(26, 26, 46, 0.95);
    }

    /* 滚动条样式 */
    ::-webkit-scrollbar {
        width: 8px;
    }

    ::-webkit-scrollbar-track {
        background: #1a1a2e;
    }

    ::-webkit-scrollbar-thumb {
        background: #4a5568;
        border-radius: 4px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: #667eea;
    }

    /* 帮助文本 */
    .help-text {
        font-size: 0.85rem;
        color: #a0aec0;
        font-style: italic;
    }
</style>
""", unsafe_allow_html=True)


# ==================== Git 操作类 ====================

class GitOperations:
    """Git 命令执行核心类"""

    def __init__(self, repo_path="."):
        self.repo_path = Path(repo_path).resolve()
        self.console_output = []

    def _run_command(self, command, capture_output=True):
        """
        执行 Git 命令
        对应底层: subprocess.run() 执行原生 Git 命令
        """
        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=self.repo_path,
                capture_output=capture_output,
                text=True,
                encoding='utf-8',
                errors='replace',  # 替换无法解码的字符，避免中文文件名报错
                timeout=60  # 60秒超时
            )
            return result
        except subprocess.TimeoutExpired:
            return None
        except Exception as e:
            return None

    def is_git_repo(self):
        """
        检查是否为 Git 仓库
        对应命令: git rev-parse --is-inside-work-tree
        """
        result = self._run_command("git rev-parse --is-inside-work-tree 2>&1")
        return result and result.returncode == 0

    def get_current_branch(self):
        """
        获取当前分支名
        对应命令: git branch --show-current
        """
        result = self._run_command("git branch --show-current")
        if result and result.returncode == 0:
            return result.stdout.strip()
        return "未知"

    def get_remote_url(self):
        """
        获取远程仓库地址
        对应命令: git remote get-url origin
        """
        result = self._run_command("git remote get-url origin")
        if result and result.returncode == 0:
            return result.stdout.strip()
        return None

    def get_status(self):
        """
        获取工作区状态
        对应命令: git status --porcelain
        """
        result = self._run_command("git status --porcelain")
        if result and result.returncode == 0:
            return result.stdout.strip().split('\n') if result.stdout.strip() else []
        return []

    def get_ahead_behind(self):
        """
        获取与远程的领先/落后状态
        对应命令: git rev-list --count --left-right @{upstream}...HEAD
        """
        result = self._run_command("git rev-list --count --left-right @{upstream}...HEAD 2>&1")
        if result and result.returncode == 0 and result.stdout.strip():
            parts = result.stdout.strip().split('\t')
            if len(parts) == 2:
                behind, ahead = parts
                return int(ahead), int(behind)
        return 0, 0

    def fetch(self):
        """
        获取远程更新信息（不合并）
        对应命令: git fetch
        """
        result = self._run_command("git fetch")
        return result and result.returncode == 0

    def pull(self):
        """
        拉取远程更新并合并
        对应命令: git pull
        """
        result = self._run_command("git pull")
        if result:
            self.console_output.append(("", f">>> git pull\n", "command"))
            if result.stdout:
                self.console_output.append(("", result.stdout, "output"))
            if result.stderr:
                self.console_output.append(("", result.stderr, "error"))
        return result and result.returncode == 0

    def has_uncommitted_changes(self):
        """检查是否有未提交的更改"""
        status = self.get_status()
        return len(status) > 0

    def add_all(self):
        """
        添加所有更改到暂存区
        对应命令: git add .
        """
        result = self._run_command("git add .")
        if result:
            self.console_output.append(("", f">>> git add .\n", "command"))
        return result and result.returncode == 0

    def commit(self, message):
        """
        提交更改
        对应命令: git commit -m "message"
        """
        # 转义消息中的特殊字符
        safe_message = message.replace('"', '\\"')
        result = self._run_command(f'git commit -m "{safe_message}"')
        if result:
            self.console_output.append(("", f'>>> git commit -m "{message}"\n', "command"))
            if result.stdout:
                self.console_output.append(("", result.stdout, "output"))
            if result.stderr:
                self.console_output.append(("", result.stderr, "output"))
        return result and result.returncode == 0

    def push(self, force=False, set_upstream=True):
        """
        推送到远程仓库
        对应命令: git push 或 git push --force
        对应命令: git push -u origin <branch> (新分支设置上游)
        """
        current_branch = self.get_current_branch()

        # 检查是否有 upstream
        has_upstream = self._run_command(f"git rev-parse --abbrev-ref --symbolic-full-name @{u} 2>/dev/null").returncode == 0

        if not has_upstream and set_upstream:
            # 新分支，使用 -u 设置上游
            cmd = f"git push -u origin {current_branch}"
            if force:
                cmd = f"git push -u origin {current_branch} --force"
        else:
            cmd = "git push --force" if force else "git push"

        result = self._run_command(cmd)
        if result:
            self.console_output.append(("", f">>> {cmd}\n", "command"))
            if result.stdout:
                self.console_output.append(("", result.stdout, "output"))
            if result.stderr:
                self.console_output.append(("", result.stderr, "output"))
        return result and result.returncode == 0

    def check_remote_has_updates(self):
        """
        检查远程是否有新提交
        对应命令: git rev-parse HEAD @{u}
        """
        behind, _ = self.get_ahead_behind()
        return behind > 0

    def get_config_files_status(self):
        """
        检查环境配置文件是否有变化
        对应文件: package.json, requirements.txt, .env.example
        """
        config_files = ['package.json', 'requirements.txt', '.env.example', 'pom.xml', 'build.gradle']
        status = self.get_status()
        changed_config = []

        for file_status in status:
            if file_status:
                file_name = file_status[3:] if file_status[2:] == '  ' else file_status[3:]
                for config in config_files:
                    if config in file_name:
                        changed_config.append(file_name)

        return changed_config

    def set_remote_url(self, url, remote_name="origin"):
        """
        设置远程仓库地址
        对应命令: git remote set-url origin <url>
        """
        result = self._run_command(f'git remote set-url {remote_name} "{url}"')
        if result:
            self.console_output.append(("", f'>>> git remote set-url {remote_name} "{url}"\n', "command"))
            if result.stdout:
                self.console_output.append(("", result.stdout, "output"))
            if result.stderr:
                self.console_output.append(("", result.stderr, "output"))
        return result and result.returncode == 0

    def get_all_branches(self):
        """
        获取所有分支（本地和远程）
        对应命令: git branch -a
        """
        result = self._run_command("git branch -a")
        if result and result.returncode == 0:
            branches = []
            for line in result.stdout.strip().split('\n'):
                if line.strip():
                    is_current = line.strip().startswith('*')
                    branch_name = line.strip().replace('*', '').strip()
                    # 去掉 remote 前缀
                    if branch_name.startswith('remotes/origin/'):
                        branch_name = branch_name.replace('remotes/origin/', '')
                    elif branch_name.startswith('remotes/'):
                        continue
                    branches.append({
                        'name': branch_name,
                        'current': is_current,
                        'is_remote': 'remotes/' in line
                    })
            return branches
        return []

    def get_local_branches(self):
        """
        获取本地分支列表
        对应命令: git branch
        """
        result = self._run_command("git branch")
        if result and result.returncode == 0:
            branches = []
            for line in result.stdout.strip().split('\n'):
                if line.strip():
                    is_current = line.strip().startswith('*')
                    branch_name = line.strip().replace('*', '').strip()
                    branches.append({
                        'name': branch_name,
                        'current': is_current
                    })
            return branches
        return []

    def get_remote_branches(self):
        """
        获取远程分支列表
        对应命令: git branch -r
        """
        result = self._run_command("git branch -r")
        if result and result.returncode == 0:
            branches = []
            for line in result.stdout.strip().split('\n'):
                if line.strip() and 'HEAD' not in line:
                    branch_name = line.strip().replace('origin/', '').strip()
                    if branch_name and branch_name not in [b['name'] for b in branches]:
                        branches.append(branch_name)
            return branches
        return []

    def create_branch(self, branch_name):
        """
        创建新分支
        对应命令: git checkout -b <branch_name>
        """
        result = self._run_command(f'git checkout -b {branch_name}')
        if result:
            self.console_output.append(("", f'>>> git checkout -b {branch_name}\n', "command"))
            if result.stdout:
                self.console_output.append(("", result.stdout, "output"))
            if result.stderr:
                self.console_output.append(("", result.stderr, "output"))
        return result and result.returncode == 0

    def switch_branch(self, branch_name):
        """
        切换分支
        对应命令: git checkout <branch_name>
        """
        result = self._run_command(f'git checkout {branch_name}')
        if result:
            self.console_output.append(("", f'>>> git checkout {branch_name}\n', "command"))
            if result.stdout:
                self.console_output.append(("", result.stdout, "output"))
            if result.stderr:
                self.console_output.append(("", result.stderr, "output"))
        return result and result.returncode == 0

    def delete_branch(self, branch_name, force=False):
        """
        删除本地分支
        对应命令: git branch -d/-D <branch_name>
        """
        flag = '-D' if force else '-d'
        result = self._run_command(f'git branch {flag} {branch_name}')
        if result:
            self.console_output.append(("", f'>>> git branch {flag} {branch_name}\n', "command"))
            if result.stdout:
                self.console_output.append(("", result.stdout, "output"))
            if result.stderr:
                self.console_output.append(("", result.stderr, "output"))
        return result and result.returncode == 0

    def create_and_checkout_branch(self, branch_name, start_point=None):
        """
        创建并切换到新分支
        对应命令: git checkout -b <branch_name> [start_point]
        """
        if start_point:
            cmd = f'git checkout -b {branch_name} {start_point}'
        else:
            cmd = f'git checkout -b {branch_name}'
        result = self._run_command(cmd)
        if result:
            self.console_output.append(("", f'>>> {cmd}\n', "command"))
            if result.stdout:
                self.console_output.append(("", result.stdout, "output"))
            if result.stderr:
                self.console_output.append(("", result.stderr, "output"))
        return result and result.returncode == 0


# ==================== UI 组件函数 ====================

def render_status_card(git_ops):
    """渲染状态卡片"""
    st.markdown('<div class="title-container">Git 同步工具</div>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">跨端代码同步利器 | 公司与家之间无缝切换</p>', unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        branch = git_ops.get_current_branch()
        st.markdown(f"""
        <div class="status-card">
            <div style="font-size: 0.8rem; color: #a0aec0;">当前分支</div>
            <div style="font-size: 1.5rem; font-weight: bold; color: #667eea;">
                <span class="status-badge status-info">{branch}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        status = git_ops.get_status()
        uncommitted_count = len([s for s in status if s.strip()])
        color = "status-success" if uncommitted_count == 0 else "status-warning"
        st.markdown(f"""
        <div class="status-card">
            <div style="font-size: 0.8rem; color: #a0aec0;">未提交文件</div>
            <div style="font-size: 1.5rem; font-weight: bold;">
                <span class="status-badge {color}">{uncommitted_count}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col3, col4:
        ahead, behind = git_ops.get_ahead_behind()
        with col3:
            st.markdown(f"""
            <div class="status-card">
                <div style="font-size: 0.8rem; color: #a0aec0;">领先远程</div>
                <div style="font-size: 1.5rem; font-weight: bold;">
                    <span class="status-badge status-success">{ahead} 提交</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

        with col4:
            color = "status-success" if behind == 0 else "status-danger"
            st.markdown(f"""
            <div class="status-card">
                <div style="font-size: 0.8rem; color: #a0aec0;">落后远程</div>
                <div style="font-size: 1.5rem; font-weight: bold;">
                    <span class="status-badge {color}">{behind} 提交</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # 远程仓库地址
    remote_url = git_ops.get_remote_url()
    if remote_url:
        st.markdown(f"""
        <div class="info-box">
            <strong>远程仓库:</strong> <code style="background: rgba(0,0,0,0.3); padding: 2px 8px; border-radius: 4px;">{remote_url}</code>
        </div>
        """, unsafe_allow_html=True)


def render_file_changes(git_ops):
    """渲染文件变更列表"""
    status = git_ops.get_status()
    if status:
        st.markdown("### 📝 未提交的文件变更")
        st.markdown('<div class="file-list">', unsafe_allow_html=True)

        for line in status:
            if not line.strip():
                continue

            status_code = line[:2]
            file_path = line[3:]
            status_icon = "🟢"  # Modified
            status_text = "已修改"

            if status_code[0] == '?':
                status_icon = "⚪"
                status_text = "未跟踪"
            elif status_code[0] == 'A':
                status_icon = "🟡"
                status_text = "已添加"
            elif status_code[0] == 'D':
                status_icon = "🔴"
                status_text = "已删除"
            elif status_code[0] == 'R':
                status_icon = "🔵"
                status_text = "已重命名"
            elif status_code[0] == 'M':
                status_icon = "🟠"
                status_text = "已修改(暂存)"

            st.markdown(f"""
            <div class="file-item">
                {status_icon} <strong>{status_text}</strong> - <code>{file_path}</code>
            </div>
            """, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)


def render_console_output(console_output):
    """渲染控制台输出"""
    if not console_output:
        return

    st.markdown("### 💻 命令执行记录")
    st.markdown('<div class="console-container">', unsafe_allow_html=True)

    for prefix, content, msg_type in console_output:
        if not content:
            continue

        lines = content.split('\n')
        for line in lines:
            if not line:
                continue
            css_class = "console-command"
            if msg_type == "error":
                css_class = "console-error"
            elif msg_type == "output":
                css_class = "console-output"
            elif msg_type == "success":
                css_class = "console-success"

            # 转义 HTML
            safe_line = line.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            st.markdown(f'<div class="console-line {css_class}">{safe_line}</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)


def render_config_warning(changed_configs):
    """渲染配置文件变更警告"""
    if changed_configs:
        st.markdown(f"""
        <div class="warning-box">
            <strong>⚠️ 依赖配置已变更!</strong><br>
            以下配置文件有变化，请执行依赖安装:<br>
            {'<br>'.join([f'• <code>{f}</code>' for f in changed_configs])}
        </div>
        """, unsafe_allow_html=True)


def render_error_box(title, message):
    """渲染错误提示框"""
    st.markdown(f"""
    <div class="error-box">
        <strong>❌ {title}</strong><br>
        {message}
    </div>
    """, unsafe_allow_html=True)


def render_success_box(title, message):
    """渲染成功提示框"""
    st.markdown(f"""
    <div class="info-box" style="border-left-color: #48bb78; background: rgba(72, 187, 120, 0.1);">
        <strong>✅ {title}</strong><br>
        {message}
    </div>
    """, unsafe_allow_html=True)


# ==================== 主程序 ====================

def main():
    # 初始化 session state
    if 'console_output' not in st.session_state:
        st.session_state.console_output = []
    if 'last_action' not in st.session_state:
        st.session_state.last_action = None
    if 'location' not in st.session_state:
        st.session_state.location = 'Office'

    # 初始化 Git 操作类
    git_ops = GitOperations()

    # 检查是否为 Git 仓库
    if not git_ops.is_git_repo():
        st.markdown("""
        <div class="error-box">
            <strong>❌ 当前目录不是 Git 仓库!</strong><br><br>
            请先初始化 Git 仓库:<br>
            <code>git init</code><br><br>
            或连接到远程仓库:<br>
            <code>git remote add origin &lt;your-repo-url&gt;</code>
        </div>
        """, unsafe_allow_html=True)
        st.stop()

    # 侧边栏配置
    with st.sidebar:
        st.markdown("""
        <h2 style="color: #667eea; text-align: center;">⚙️ 设置</h2>
        """, unsafe_allow_html=True)

        st.session_state.location = st.selectbox(
            "📍 当前位置",
            ['Office', 'Home', 'Other'],
            label_visibility="collapsed"
        )

        st.markdown("---")

        # 远程仓库管理
        st.markdown("### 🔗 远程仓库")
        remote_url = git_ops.get_remote_url()
        if remote_url:
            st.markdown(f"""
            <div style="font-size: 0.75rem; color: #a0aec0; margin-bottom: 0.5rem;">
            当前远程:<br>
            <code style="word-break: break-all;">{remote_url}</code>
            </div>
            """, unsafe_allow_html=True)

        with st.expander("修改远程仓库地址"):
            new_remote_url = st.text_input(
                "新仓库地址",
                placeholder="https://github.com/用户名/仓库名.git",
                value=remote_url or "",
                key="remote_url_input"
            )
            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("应用", use_container_width=True, key="apply_remote"):
                    if new_remote_url and new_remote_url != remote_url:
                        git_ops.console_output = []
                        if git_ops.set_remote_url(new_remote_url):
                            st.session_state.console_output = git_ops.console_output
                            st.session_state.last_action = "remote_updated"
                            st.rerun()
                        else:
                            st.session_state.console_output = git_ops.console_output
                            st.session_state.last_action = "remote_error"
                            st.rerun()
            with col_b:
                if st.button("重置", use_container_width=True, key="reset_remote"):
                    st.rerun()

        st.markdown("---")

        # 分支管理
        st.markdown("### 🌿 分支管理")

        # 获取本地和远程分支
        local_branches = git_ops.get_local_branches()
        remote_branches = git_ops.get_remote_branches()
        current_branch = git_ops.get_current_branch()

        # 显示当前分支
        st.markdown(f"""
        <div style="font-size: 0.75rem; color: #a0aec0; margin-bottom: 0.5rem;">
        当前分支: <span style="color: #667eea; font-weight: bold;">{current_branch}</span>
        </div>
        """, unsafe_allow_html=True)

        # 切换分支
        with st.expander("切换分支"):
            if local_branches:
                branch_names = [b['name'] for b in local_branches]
                switch_to = st.selectbox(
                    "选择要切换的分支",
                    branch_names,
                    index=branch_names.index(current_branch) if current_branch in branch_names else 0,
                    key="switch_branch_select"
                )
                if st.button("切换", use_container_width=True, key="switch_branch_btn"):
                    if switch_to != current_branch:
                        git_ops.console_output = []
                        if git_ops.switch_branch(switch_to):
                            st.session_state.console_output = git_ops.console_output
                            st.session_state.last_action = "branch_switched"
                            st.rerun()
                        else:
                            st.session_state.console_output = git_ops.console_output
                            st.session_state.last_action = "branch_switch_error"
                            st.rerun()

        # 创建新分支
        with st.expander("创建新分支"):
            new_branch_name = st.text_input(
                "新分支名称",
                placeholder="feature/new-feature",
                key="new_branch_input"
            )
            if st.button("创建分支", use_container_width=True, key="create_branch_btn"):
                if new_branch_name:
                    git_ops.console_output = []
                    if git_ops.create_branch(new_branch_name):
                        st.session_state.console_output = git_ops.console_output
                        st.session_state.last_action = "branch_created"
                        st.rerun()
                    else:
                        st.session_state.console_output = git_ops.console_output
                        st.session_state.last_action = "branch_create_error"
                        st.rerun()

        # 从远程创建本地分支
        if remote_branches:
            with st.expander("从远程创建分支"):
                checkout_remote = st.selectbox(
                    "选择远程分支",
                    [b for b in remote_branches if b != current_branch],
                    key="checkout_remote_select"
                )
                if st.button("检出并创建", use_container_width=True, key="checkout_remote_btn"):
                    git_ops.console_output = []
                    if git_ops.create_and_checkout_branch(checkout_remote, f"origin/{checkout_remote}"):
                        st.session_state.console_output = git_ops.console_output
                        st.session_state.last_action = "branch_created_from_remote"
                        st.rerun()
                    else:
                        st.session_state.console_output = git_ops.console_output
                        st.session_state.last_action = "branch_create_error"
                        st.rerun()

        # 删除分支
        if len(local_branches) > 1:
            with st.expander("删除分支"):
                deletable_branches = [b['name'] for b in local_branches if not b['current']]
                if deletable_branches:
                    delete_branch = st.selectbox(
                        "选择要删除的分支",
                        deletable_branches,
                        key="delete_branch_select"
                    )
                    col_d1, col_d2 = st.columns(2)
                    with col_d1:
                        if st.button("删除", use_container_width=True, key="delete_branch_btn"):
                            git_ops.console_output = []
                            if git_ops.delete_branch(delete_branch):
                                st.session_state.console_output = git_ops.console_output
                                st.session_state.last_action = "branch_deleted"
                                st.rerun()
                            else:
                                st.session_state.console_output = git_ops.console_output
                                st.session_state.last_action = "branch_delete_error"
                                st.rerun()
                    with col_d2:
                        if st.button("强制删除", use_container_width=True, key="force_delete_branch_btn"):
                            git_ops.console_output = []
                            if git_ops.delete_branch(delete_branch, force=True):
                                st.session_state.console_output = git_ops.console_output
                                st.session_state.last_action = "branch_deleted"
                                st.rerun()
                            else:
                                st.session_state.console_output = git_ops.console_output
                                st.session_state.last_action = "branch_delete_error"
                                st.rerun()
                else:
                    st.info("没有可删除的分支")

        st.markdown("---")

        st.markdown("""
        <div class="help-text">
            <p><strong>使用说明:</strong></p>
            <ul>
                <li><strong>上班准备</strong> = 从 GitHub 拉取最新代码</li>
                <li><strong>下班交接</strong> = 把今天的改动推送到 GitHub</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")

        if st.button("🔄 刷新状态", use_container_width=True):
            st.rerun()

    # 主界面
    render_status_card(git_ops)

    st.markdown("---")

    # 文件变更展示
    render_file_changes(git_ops)

    # 配置文件变更警告
    changed_configs = git_ops.get_config_files_status()
    if changed_configs:
        render_config_warning(changed_configs)

    st.markdown("---")

    # 操作按钮区域
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 🌅 上班准备")
        st.markdown('<p class="help-text">从 GitHub 拉取最新代码到本地</p>', unsafe_allow_html=True)

        if st.button("📥 一键拉取", type="secondary", use_container_width=True):
            with st.spinner("正在从远程拉取代码..."):
                git_ops.console_output = []
                git_ops.fetch()  # 先更新远程信息

                # 检查是否有冲突可能
                behind, ahead = git_ops.get_ahead_behind()

                if git_ops.pull():
                    st.session_state.console_output = git_ops.console_output
                    st.session_state.last_action = "pull_success"
                    st.rerun()
                else:
                    st.session_state.console_output = git_ops.console_output
                    st.session_state.last_action = "pull_error"
                    st.rerun()

    with col2:
        st.markdown("### 🌙 下班交接")
        st.markdown('<p class="help-text">把今天的改动推送到 GitHub 保管</p>', unsafe_allow_html=True)

        # 推送前检查
        has_changes = git_ops.has_uncommitted_changes()
        remote_has_updates = git_ops.check_remote_has_updates()

        if remote_has_updates:
            st.markdown("""
            <div class="warning-box">
                <strong>⚠️ 远程有新内容!</strong><br>
                请先执行"一键拉取"，避免代码冲突。
            </div>
            """, unsafe_allow_html=True)

        if st.button("📤 一键推送", type="primary", use_container_width=True, disabled=remote_has_updates):
            if not has_changes:
                st.markdown("""
                <div class="info-box">
                    没有需要提交的更改，所有内容已是最新。
                </div>
                """, unsafe_allow_html=True)
            else:
                with st.spinner("正在推送到远程仓库..."):
                    git_ops.console_output = []

                    # 生成提交信息
                    now = datetime.now().strftime("%Y-%m-%d %H:%M")
                    location = st.session_state.location
                    commit_msg = f"Sync from {location} - {now}"

                    # 执行 git add .
                    if not git_ops.add_all():
                        st.session_state.last_action = "add_error"
                        st.session_state.console_output = git_ops.console_output
                        st.rerun()

                    # 执行 git commit
                    if not git_ops.commit(commit_msg):
                        # 可能没有可提交的内容
                        pass

                    # 执行 git push
                    if git_ops.push():
                        st.session_state.console_output = git_ops.console_output
                        st.session_state.last_action = "push_success"
                        st.rerun()
                    else:
                        st.session_state.console_output = git_ops.console_output
                        st.session_state.last_action = "push_error"
                        st.rerun()

    st.markdown("---")

    # 操作结果反馈
    if st.session_state.last_action:
        if st.session_state.last_action == "pull_success":
            render_success_box("拉取成功", "已从远程获取最新代码并自动合并。")
        elif st.session_state.last_action == "push_success":
            render_success_box("推送成功", f"已将代码推送到 GitHub，提交信息包含位置标记: {st.session_state.location}")
        elif st.session_state.last_action == "pull_error":
            render_error_box("拉取失败", "请检查网络连接或 Git 配置。如有冲突，请手动解决。")
        elif st.session_state.last_action == "push_error":
            render_error_box("推送失败", "请检查网络连接、仓库权限或是否有冲突需要解决。")
        elif st.session_state.last_action == "add_error":
            render_error_box("添加文件失败", "请检查文件权限或 Git 仓库状态。")
        elif st.session_state.last_action == "remote_updated":
            render_success_box("远程仓库已更新", "远程仓库地址已成功修改。")
        elif st.session_state.last_action == "remote_error":
            render_error_box("修改失败", "远程仓库地址修改失败，请检查地址格式是否正确。")
        elif st.session_state.last_action == "branch_switched":
            render_success_box("分支切换成功", f"已切换到新分支，请继续工作。")
        elif st.session_state.last_action == "branch_switch_error":
            render_error_box("切换失败", "分支切换失败，请检查是否有未提交的更改。")
        elif st.session_state.last_action == "branch_created":
            render_success_box("分支创建成功", "新分支已创建并自动切换。")
        elif st.session_state.last_action == "branch_created_from_remote":
            render_success_box("分支检出成功", "已从远程创建并切换到新分支。")
        elif st.session_state.last_action == "branch_create_error":
            render_error_box("创建失败", "分支创建失败，请检查分支名称是否合法。")
        elif st.session_state.last_action == "branch_deleted":
            render_success_box("分支删除成功", "分支已成功删除。")
        elif st.session_state.last_action == "branch_delete_error":
            render_error_box("删除失败", "分支删除失败，可能存在未合并的更改。")

    # 控制台输出
    if st.session_state.console_output:
        render_console_output(st.session_state.console_output)

    # 页脚
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #718096; font-size: 0.8rem; padding: 1rem;">
        Git 同步工具 v1.1 | 基于 Streamlit 构建 | 跨端同步无忧
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
