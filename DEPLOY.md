# 冷藏车运营管理系统部署说明

这是一个 Python 内置 HTTP 服务 + 单页 HTML 的轻量系统。

## 文件说明

- `index.html`：系统页面
- `server.py`：网站服务和 `/api/data` 数据接口
- `server_data.json`：线上运行后生成的数据文件
- `requirements.txt`：Python 依赖，目前无第三方依赖
- `Procfile`：部分云平台的启动命令

## 本地运行

```bash
python server.py
```

打开：

```text
http://localhost:8080
```

## 部署到 Render

1. 新建一个 GitHub 仓库，把本文件夹内容上传。
2. 打开 Render，创建 `Web Service`。
3. 连接 GitHub 仓库。
4. Runtime 选择 `Python`。
5. Build Command 填：

```bash
pip install -r requirements.txt
```

6. Start Command 填：

```bash
python server.py
```

7. 部署完成后，打开 Render 提供的网址。

## 重要提醒

当前后端会把数据写入 `server_data.json`。很多免费云平台的磁盘不是永久稳定存储，重启或重新部署后可能丢失数据。

正式使用时建议继续使用系统里的“立即备份”，定期导出 JSON 和 HTML 数据备份。
