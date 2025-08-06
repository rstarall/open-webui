# OpenWebUI 项目结构

## 后端结构 (backend/)

### 核心配置
```
backend/
├── open_webui/
│   ├── config.py                    # 全局配置和环境变量
│   ├── main.py                      # FastAPI应用入口
│   └── env.py                       # 环境变量处理
```

### 路由模块 (routers/)
```
backend/open_webui/routers/
├── auth.py                          # 认证相关路由
├── configs.py                       # 配置管理路由
├── files.py                         # 文件上传和管理
├── models.py                        # 模型管理
├── retrieval.py                     # RAG和文档处理
├── users.py                         # 用户管理
└── chats.py                         # 对话管理
```

### 文档处理 (retrieval/)
```
backend/open_webui/retrieval/
├── loaders/
│   ├── main.py                      # Loader主类，文件类型路由
│   ├── external_document.py         # 外部文档加载器
│   ├── mineru.py                    # MinerU文档解析器
│   ├── mistral.py                   # Mistral OCR
│   ├── datalab_marker.py            # Datalab Marker API
│   └── [其他加载器...]
├── vector_dbs/                      # 向量数据库实现
└── utils.py                         # 工具函数
```

### 数据模型 (models/)
```
backend/open_webui/models/
├── auth.py                          # 认证模型
├── chats.py                         # 对话模型
├── configs.py                       # 配置模型
├── files.py                         # 文件模型
├── models.py                        # AI模型配置
└── users.py                         # 用户模型
```

## 前端结构 (src/)

### 主要组件
```
src/
├── routes/
│   ├── +page.svelte                 # 主页面（对话界面）
│   ├── (app)/
│   │   └── c/[id]/+page.svelte     # 具体对话页面
│   └── auth/                        # 认证页面
```

### 库文件 (lib/)
```
src/lib/
├── apis/                            # API调用函数
│   ├── configs/                     # 配置API
│   ├── files/                       # 文件API
│   ├── models/                      # 模型API
│   └── users/                       # 用户API
├── components/                      # UI组件
│   ├── admin/                       # 管理界面
│   │   └── Settings/
│   │       ├── Documents.svelte     # 文档设置（文件类型路由）
│   │       └── General.svelte       # 通用设置
│   ├── chat/                        # 对话组件
│   │   ├── Chat.svelte              # 主对话组件
│   │   ├── ModelSelector.svelte     # 模型选择器
│   │   └── Messages/                # 消息相关组件
│   ├── layout/
│   │   └── Sidebar.svelte           # 侧边栏
│   └── workspace/
│       └── Models/
│           ├── ModelEditor.svelte   # 模型编辑器
│           └── ModelItemMenu.svelte # 模型菜单
├── stores/                          # Svelte stores
│   ├── config.js                    # 配置store
│   ├── models.js                    # 模型store
│   └── user.js                      # 用户store
└── utils/                           # 工具函数
```

## 配置文件
```
/
├── backend/
│   ├── dev.sh                       # 后端开发启动脚本
│   └── requirements.txt             # Python依赖
├── package.json                     # 前端依赖
├── vite.config.js                   # Vite配置
└── docker-compose.yml               # Docker配置
```

## 文档和记录
```
/
├── claude_code.md                   # Claude修改记录
├── claude_work.md                   # 工作内容记录
├── claude_project.md                # 项目结构文档（本文件）
└── file_type_routing_implementation.md  # 文件类型路由实现文档
```

## 重要文件位置快速索引

### 文件上传和处理
- 上传入口: `backend/open_webui/routers/files.py`
- 处理逻辑: `backend/open_webui/routers/retrieval.py:1330` (process_file)
- 文件加载: `backend/open_webui/retrieval/loaders/main.py:209` (Loader类)

### 配置管理
- 后端配置: `backend/open_webui/config.py`
- 配置路由: `backend/open_webui/routers/configs.py`
- 前端配置: `src/lib/stores/config.js`

### 文件类型路由
- 后端实现: `backend/open_webui/retrieval/loaders/main.py:236-280`
- 前端界面: `src/lib/components/admin/Settings/Documents.svelte`
- 配置结构: FILE_TYPE_ENGINE_MAPPING

### MinerU集成
- Loader实现: `backend/open_webui/retrieval/loaders/mineru.py`
- 集成点: `backend/open_webui/retrieval/loaders/main.py:301-305`
- 前端配置: Documents.svelte中的MinerU相关字段