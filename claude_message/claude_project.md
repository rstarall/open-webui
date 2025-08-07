# Open WebUI项目结构

## 目录结构
```
open-webui-dev/
├── claude_message/              # Claude工作文档
│   ├── claude_code.md          # 代码变更记录
│   ├── claude_work.md          # 工作内容记录
│   └── claude_project.md       # 项目结构说明
├── src/                         # 前端源代码
│   ├── lib/
│   │   ├── components/         # Svelte组件
│   │   │   ├── admin/          # 管理员组件
│   │   │   │   └── Settings/   # 设置页面
│   │   │   ├── chat/           # 聊天组件
│   │   │   └── workspace/      # 工作空间组件
│   │   └── apis/               # API调用
└── backend/                     # 后端源代码
    └── open_webui/
        └── apps/
            └── retrieval/        # 文档检索模块
```

## 模块代码示例

### src/lib/components/admin/Settings/Documents.svelte
```svelte
<script>
  import { getRAGConfig, updateRAGConfig } from '$lib/apis/retrieval';
  
  let content = {
    extraction: {
      engine: 'default',
      engine_docs_images: false,
      engine_docs_tables: false
    }
  };
  
  // 保存配置
  const saveHandler = async () => {
    const res = await updateRAGConfig(localStorage.token, content);
    if (res) {
      toast.success($i18n.t('Settings updated successfully'));
    }
  };
</script>

<template>
  <div class="settings-container">
    <!-- 文档解析引擎选择 -->
    <select bind:value={content.extraction.engine}>
      <option value="default">默认</option>
      <option value="unstructured">Unstructured</option>
      <option value="mineru">MinerU</option>
    </select>
  </div>
</template>
```

### backend/open_webui/apps/retrieval/main.py
```python
from fastapi import APIRouter, HTTPException
from typing import Optional, List

router = APIRouter()

class RAGConfig:
    """RAG配置管理"""
    def __init__(self):
        self.extraction = {
            "engine": "default",
            "engine_docs_images": False,
            "engine_docs_tables": False
        }

@router.post("/process/doc")
async def process_document(file_path: str, config: dict):
    """处理文档解析"""
    engine = config.get("engine", "default")
    
    if engine == "mineru":
        loader = MinerULoader(
            file_path,
            parse_images=config.get("engine_docs_images", False),
            parse_tables=config.get("engine_docs_tables", False)
        )
    else:
        loader = DefaultLoader(file_path)
    
    return await loader.load()
```

### src/lib/apis/retrieval/index.js
```javascript
export const getRAGConfig = async (token) => {
  const res = await fetch(`${WEBUI_API_BASE_URL}/retrieval/config`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`
    }
  });
  return await res.json();
};

export const updateRAGConfig = async (token, config) => {
  const res = await fetch(`${WEBUI_API_BASE_URL}/retrieval/config/update`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`
    },
    body: JSON.stringify(config)
  });
  return await res.json();
};
```