# Remote Tunnel 与手机协作指南

## 推荐组合

- VS Code Remote Tunnel：远程访问开发机工作区
- 手机浏览器：打开 `vscode.dev` 远程查看和轻量编辑
- 手机远程桌面：需要完整控制 Windows 桌面时使用

## 当前建议方案

- 主远控：`Chrome Remote Desktop`
- 备用远控：`RustDesk`
- 代码轻量访问：`VS Code Remote Tunnel`

## Chrome Remote Desktop

### 电脑端

1. 打开 `https://remotedesktop.google.com/access`
2. 登录 Google 账号
3. 选择开启远程访问
4. 安装主机组件
5. 设置设备名称和 PIN
6. 保持电脑开机联网

### 手机端

- iPhone / iPad：App Store 搜索 `Chrome Remote Desktop`
- Android：Google Play 搜索 `Chrome Remote Desktop`

### 适用场景

- 外出时完整控制当前这台 Windows 电脑
- 继续使用本地文件、图片、脚本和桌面工具
- 操作体验优先于网页方式

## RustDesk

- 免费、开源
- 适合作为备用方案
- 后期如果需要更高可控性，可考虑深入使用

## VS Code Remote Tunnel

- 适合轻量代码访问和文件查看
- 不建议作为图片处理、脚本运行和桌面工具操作的唯一方案

## 核心注意

- 电脑必须开机联网
- VS Code 必须保持运行，或使用 `code tunnel` 保持隧道
- 手机端复杂文件操作、图片工作、桌面软件调用，仍建议走远程桌面
