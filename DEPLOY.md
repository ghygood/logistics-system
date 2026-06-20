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

## 设置访问密码

部署到公网后，必须在 Render 的 `Environment` 页面添加环境变量：

```text
APP_PASSWORD=你自己的访问密码
```

保存后点击 `Manual Deploy` 重新部署。

之后打开网站时会要求输入访问密码，后端 `/api/data` 也会校验这个密码。

## 长期保存数据：Supabase 数据库

Render 免费服务的本地文件不适合保存重要数据。长期使用建议把数据保存到 Supabase。

### 1. 创建 Supabase 项目

1. 打开 Supabase 官网并登录。
2. 创建新项目。
3. 进入项目后打开 `SQL Editor`。
4. 新建查询，执行下面 SQL：

```sql
create table if not exists logistics_data (
  id text primary key,
  data jsonb not null,
  updated_at timestamptz default now()
);
```

### 2. 获取 Supabase 配置

在 Supabase 项目里打开：

```text
Project Settings -> API
```

复制：

- `Project URL`
- `service_role` key

注意：`service_role` key 只能放在 Render 后端环境变量里，不要写进前端网页，不要公开发给别人。

### 3. 在 Render 添加环境变量

Render 项目左侧打开 `Environment`，添加：

```text
SUPABASE_URL=你的 Project URL
SUPABASE_SERVICE_KEY=你的 service_role key
SUPABASE_TABLE=logistics_data
DATA_ID=main
```

保留原来的：

```text
APP_PASSWORD=你的系统访问密码
```

保存后点击 `Manual Deploy -> Deploy latest commit`。

### 4. 恢复旧数据

部署成功后，打开系统，使用“恢复数据”选择之前下载的 JSON 备份文件。恢复后数据会写入 Supabase，后续 Render 重启或重新部署也不会丢。

## 重要提醒

如果未配置 Supabase，后端会退回写入 `server_data.json`。很多免费云平台的磁盘不是永久稳定存储，重启或重新部署后可能丢失数据。

正式使用时建议继续使用系统里的“立即备份”，定期导出 JSON 和 HTML 数据备份。
