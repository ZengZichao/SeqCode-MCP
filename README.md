# SeqCode MCP 服务器

[English](./README_en.md) | 中文

<div align="center">

**版本 0.1.0**

一个用于 [SeqCode Registry](https://registry.seqco.de/) 数据库的 [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) 服务器

</div>

---

## 目录

- [简介](#简介)
- [关于 SeqCode Registry](#关于-seqcode-registry)
- [功能特性](#功能特性)
- [安装](#安装)
- [配置与使用](#配置与使用)
- [可用工具](#可用工具)
- [工具详解](#工具详解)
- [API 数据模型](#api-数据模型)
- [开发指南](#开发指南)
- [许可证](#许可证)

---

## 简介

> **⚠️ 免责声明：** 本项目是一个**非官方的**社区驱动的 Model Context Protocol (MCP) 服务器，与 SeqCode Registry 官方组织没有隶属关系。SeqCode 和 SeqCode Registry 是其各自所有者的商标/项目名称。

**SeqCode MCP** 是一个基于 Model Context Protocol 的服务器，使 AI 助手（如 Claude）能够直接查询和检索 [SeqCode Registry](https://registry.seqco.de/) 数据库中的微生物命名信息。

SeqCode Registry 是原核生物（细菌和古菌）基于序列数据命名的中央存储库。本 MCP 服务器封装了 SeqCode Registry 的全部公开 REST API 端点，提供 18 个工具函数，涵盖名称检索、基因组查询、出版物浏览、作者/期刊/主题浏览、注册列表查询、菌株查询和全文搜索等功能。

### 工作原理

```
┌──────────────┐     stdio      ┌──────────────────┐     HTTPS     ┌─────────────────────┐
│  AI 助手      │ ◄──────────► │  SeqCode MCP     │ ◄──────────► │  SeqCode Registry   │
│  (Claude等)  │                │  服务器          │               │  REST API           │
└──────────────┘                └──────────────────┘               └─────────────────────┘
```

---

## 关于 SeqCode Registry

SeqCode Registry 是 [SeqCode 倡议](https://isme-microbes.org/public/seqcode-initiative/) 的一部分，旨在为未培养的原核生物（通过基因组数据描述的微生物）建立一个正式的命名法规体系。

### 关键数据

| 数据类型 | 数量（截至 2026 年 10 月） |
|---------|--------------------------|
| 已注册名称 | 48,431 |
| SeqCode 有效发表名称 | 3,373 |
| 验证注册列表 | 264 |

### 数据许可

SeqCode Registry 中的所有信息均在 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可下发布。

---

## 功能特性

- **18 个 MCP 工具**：覆盖 SeqCode Registry REST API 的所有公开端点
- **异步 HTTP 客户端**：基于 `httpx` 的高性能异步请求
- **全文搜索**：支持按名称、基因组、出版物、作者、主题搜索
- **分页支持**：所有列表端点均支持分页查询
- **状态过滤**：名称列表支持按 `SeqCode`、`ICNP`、`valid` 等状态过滤
- **错误处理**：完善的错误处理和友好的错误信息
- **零配置**：安装后即可使用，无需认证或 API Key

---

## 安装

### 前提条件

- Python ≥ 3.10
- pip 或 uv

### 从源码安装

```bash
# 克隆项目
git clone https://github.com/SeqCode-MCP/seqcode-mcp.git
cd seqcode-mcp

# 安装（推荐使用虚拟环境）
pip install -e .

# 或者使用 uv
uv pip install -e .
```

### 依赖项

| 依赖 | 最低版本 | 说明 |
|------|---------|------|
| `mcp` | ≥ 1.0.0 | Model Context Protocol SDK |
| `httpx` | ≥ 0.27.0 | 异步 HTTP 客户端 |
| `anyio` | ≥ 4.0.0 | 异步兼容层 |

---

## 配置与使用

### 在 Claude Desktop 中配置

在 Claude Desktop 的配置文件中添加以下内容：

**配置文件位置：**
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "seqcode": {
      "command": "python",
      "args": ["-m", "seqcode_mcp.server"],
      "cwd": "/path/to/seqcode-mcp"
    }
  }
}
```

> 如果已通过 `pip install -e .` 安装，可直接使用：
> ```json
> {
>   "mcpServers": {
>     "seqcode": {
>       "command": "seqcode-mcp"
>     }
>   }
> }
> ```

### 在其他 MCP 客户端中配置

本服务器使用标准 **stdio** 传输协议，兼容所有支持 MCP 的客户端。

### 直接运行

```bash
# 方式一：命令行入口
seqcode-mcp

# 方式二：Python 模块
python -m seqcode_mcp.server
```

---

## 可用工具

下表列出本 MCP 服务器提供的全部 18 个工具：

| # | 工具名称 | 说明 | 类别 |
|---|---------|------|------|
| 1 | `check_api_status` | 检查 API 是否可访问 | 通用 |
| 2 | `list_names` | 获取名称列表（支持状态过滤和分页） | 名称 |
| 3 | `get_name` | 根据 ID 获取名称详细信息 | 名称 |
| 4 | `list_genomes` | 获取基因组列表 | 基因组 |
| 5 | `get_genome` | 根据 ID 获取基因组详细信息 | 基因组 |
| 6 | `list_type_genomes` | 获取有效发表名称的模式基因组列表 | 基因组 |
| 7 | `list_registers` | 获取验证注册列表 | 注册列表 |
| 8 | `get_register` | 根据登录号获取注册列表详情 | 注册列表 |
| 9 | `list_publications` | 获取出版物列表 | 出版物 |
| 10 | `get_publication` | 根据 ID 获取出版物详情 | 出版物 |
| 11 | `list_authors` | 获取作者列表 | 作者 |
| 12 | `get_author` | 根据 ID 获取作者详情及其出版物 | 作者 |
| 13 | `list_journals` | 获取期刊列表 | 期刊 |
| 14 | `get_journal` | 根据名称获取期刊详情及其出版物 | 期刊 |
| 15 | `list_subjects` | 获取出版物主题列表 | 主题 |
| 16 | `get_subject` | 根据 ID 获取主题详情及其出版物 | 主题 |
| 17 | `get_strain` | 根据 ID 获取菌株详情 | 菌株 |
| 18 | `search_seqcode` | 全文搜索（支持名称/基因组/出版物/作者/主题） | 搜索 |

---

## 工具详解

### 通用

#### `check_api_status`
检查 SeqCode REST API 是否可访问。

- **参数**：无
- **返回示例**：
```json
{"status": "ok"}
```

### 名称

#### `list_names`
获取名称列表，支持分页和状态过滤。

- **参数**：
  - `page` (int, 可选, 默认 1)：页码
  - `status` (str, 可选)：状态过滤，可选值：`public`, `automated`, `SeqCode`, `ICNP`, `ICNafp`, `valid`
- **返回**：分页的名称列表，每项包含 `id`、`name`、`url`、`uri`

#### `get_name`
根据 ID 获取名称详细信息。

- **参数**：
  - `name_id` (int, 必需)：名称 ID
- **返回**：包含以下字段：
  - `rank`：分类等级（domain, phylum, class, order, family, genus, species 等）
  - `status_name`：命名状态（如 `Valid (SeqCode)`, `Valid (ICNP)` 等）
  - `syllabication`：音节划分
  - `etymology`：词源说明
  - `description`：描述文本（含 raw 和 html 格式）
  - `formal_styling`：正式引文格式
  - `nomenclatural_type`：模式类型（基因组、名称或菌株）
  - `classification`：分类层级（从域到种）
  - `proposed_in`：提出该名称的出版物
  - `register`：所属注册列表
  - `priority_date`：优先日期
  - `children`：子级名称列表
  - `qc_warnings`：质量检查警告

### 基因组

#### `get_genome`
根据 ID 获取基因组详细信息。

- **参数**：
  - `genome_id` (int, 必需)：基因组 ID
- **返回**：包含以下字段：
  - `database` / `accession`：数据库及登录号（如 NCBI Assembly: GCA_988280555.1）
  - `kind`：基因组类型（`isolate`, `mag`, `sag`, `enrichment`）
  - `genomic_features`：基因组特征
    - 完整度、污染度、GC含量
    - 16S/23S rRNA 基因数量和完整度
    - tRNA 数量、编码密度、密码子表
    - N50、contigs 数、最大 contig、组装长度
  - `names`：关联的名称列表
  - `strain`：关联的菌株信息

### 注册列表

#### `get_register`
根据登录号获取注册列表详情。

- **参数**：
  - `acc` (str, 必需)：注册列表登录号（如 `r:0w5t6dud`，可带或不带 `r:` 前缀）
  - `page` (int, 可选, 默认 1)：名称列表页码
- **返回**：
  - 注册列表信息（标题、DOI、优先日期）
  - 提交者和作者列表
  - 有效出版物
  - 包含的名称列表

### 出版物

#### `get_publication`
根据 ID 获取出版物详情。

- **参数**：
  - `publication_id` (int, 必需)：出版物 ID
- **返回**：
  - 引文、DOI、标题、期刊、期刊位置和日期
  - 出版物类型、摘要
  - 作者列表
  - 关联的名称列表
  - 主题列表

### 搜索

#### `search_seqcode`
全文搜索 SeqCode Registry。

- **参数**：
  - `query` (str, 必需)：搜索关键词
  - `what` (str, 可选, 默认 `names`)：搜索类型，可选值：`names`, `genomes`, `publications`, `authors`, `subjects`
- **返回**：匹配项列表，每项包含：
  - `id`：结果 ID
  - `name`：结果名称/标题
  - `url`：Registry 页面链接
  - `api_url`：API JSON 端点

---

## API 数据模型

本服务器封装的 SeqCode Registry REST API 的公开端点位于 `https://api.seqco.de/v1/`。以下是主要数据模型概览：

### name_item
```json
{
  "id": 49702,
  "name": "Spongiamicus weybensis",
  "url": "https://api.seqco.de/v1/names/49702.json",
  "uri": "https://seqco.de/i:49702"
}
```

### genome_item
```json
{
  "id": 6326,
  "database": "assembly",
  "accession": "GCA_988280555.1",
  "kind": "mag",
  "url": "https://api.seqco.de/v1/genomes/6326.json",
  "uri": "https://seqco.de/g:6326"
}
```

### publication_item
```json
{
  "id": 3944,
  "citation": "Sun et al., 2025, Microbial Genomics",
  "doi": "10.1099/mgen.0.001351",
  "url": "https://api.seqco.de/v1/publications/3944.json"
}
```

### register_item
```json
{
  "acc_url": "seqco.de/r:0w5t6dud",
  "title": "Register list for Spongiamicus weybensis gen. nov. sp. nov. ...",
  "priority_date": "2026-09-23T09:58:21.630Z",
  "url": "https://api.seqco.de/v1/registers/r:0w5t6dud.json",
  "uri": "https://seqco.de/r:0w5t6dud"
}
```

### classification（分类层级）
分类层级是一个从高到低排列的数组，第一个元素通常是 `domain` 级别的名称：

```json
[
  {"id": 753, "name": "Bacteria", "rank": "domain", "status_name": "Valid (ICNP)", ...},
  {"id": 49701, "name": "Spongiamicota", "rank": "phylum", ...},
  {"id": 49703, "name": "Spongiamicia", "rank": "class", ...},
  {"id": 49704, "name": "Spongiamicales", "rank": "order", ...},
  {"id": 49705, "name": "Spongiamicaceae", "rank": "family", ...},
  {"id": 49706, "name": "Spongiamicus", "rank": "genus", ...},
  {"id": 49702, "name": "Spongiamicus weybensis", "rank": "species", ...}
]
```

### 分页响应

所有列表端点返回分页结构：

```json
{
  "response": {
    "status": "ok",
    "message_type": "name",
    "count": 48431,
    "current_page": 1,
    "total_pages": 2422,
    "next": "https://api.seqco.de/v1/names.json?page=2"
  },
  "values": [...]
}
```

---

## 开发指南

### 项目结构

```
seqcode-mcp/
├── pyproject.toml              # 项目配置和依赖
├── README.md                  # 中文文档（本文件）
├── README_en.md               # 英文文档
├── LICENSE                    # MIT 许可证
├── .gitignore
└── src/
    └── seqcode_mcp/
        ├── __init__.py         # 包初始化
        ├── client.py           # SeqCode REST API 异步客户端
        └── server.py           # MCP 服务器实现
```

### 本地开发

```bash
# 安装开发依赖
pip install -e ".[dev]"

# 运行代码检查
ruff check src/

# 运行测试
pytest
```

### 添加新工具

1. 在 `client.py` 中添加对应的 API 调用方法
2. 在 `server.py` 的 `ALL_TOOLS` 列表中添加工具定义
3. 在 `server.py` 的 `_dispatch_tool` 函数中添加路由分支

### SeqCode REST API 参考

完整的 API 文档请参见：[https://registry.seqco.de/page/api](https://registry.seqco.de/page/api)

API 基础地址：`https://api.seqco.de/v1/`

---

## 许可证

本项目采用 [MIT 许可证](./LICENSE)。

SeqCode Registry 数据采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可证发布。

---

<div align="center">

© 2026 SeqCode-MCP Contributors

</div>
