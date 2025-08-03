# PIN 模型功能实现文档

## 功能概述
PIN 模型功能允许用户将常用的模型固定到侧边栏，方便快速访问。用户可以通过模型选择器的菜单选项来固定或取消固定模型。

## 后端实现

### API 路由
- **路径**: `POST /api/v1/users/user/settings/update`
- **文件**: `/home/ubuntu/open-webui-test/backend/open_webui/routers/users.py:214`

```python
@router.post("/user/settings/update", response_model=UserSettings)
async def update_user_settings_by_session_user(
    request: Request, form_data: UserSettings, user=Depends(get_verified_user)
):
    updated_user_settings = form_data.model_dump()
    # ... 权限检查逻辑
    user = Users.update_user_settings_by_id(user.id, updated_user_settings)
    if user:
        return user.settings
```

### 数据模型
- **文件**: `/home/ubuntu/open-webui-test/backend/open_webui/models/users.py:41`

```python
class UserSettings(BaseModel):
    ui: Optional[dict] = {}
    model_config = ConfigDict(extra="allow")
```

请求体示例：
```json
{
    "ui": {
        "pinnedModels": ["openai/gpt-4o"],
        "version": "0.6.18"
    }
}
```

## 前端实现

### 1. 状态管理
- **文件**: `/home/ubuntu/open-webui-test/src/lib/stores/index.ts:141`
- `pinnedModels` 存储在全局 `$settings` store 中

### 2. PIN 操作处理函数
- **文件**: `/home/ubuntu/open-webui-test/src/lib/components/chat/ModelSelector.svelte:28`

```javascript
const pinModelHandler = async (modelId) => {
    let pinnedModels = $settings?.pinnedModels ?? [];
    
    // 如果模型已固定，则取消固定
    if (pinnedModels.includes(modelId)) {
        pinnedModels = pinnedModels.filter((id) => id !== modelId);
    } else {
        // 如果模型未固定，则添加到固定列表
        pinnedModels = [...new Set([...pinnedModels, modelId])];
    }
    
    // 更新本地 settings
    settings.set({ ...$settings, pinnedModels: pinnedModels });
    
    // 同步到后端
    await updateUserSettings(localStorage.token, { ui: $settings });
};
```

### 3. UI 交互组件
- **文件**: `/home/ubuntu/open-webui-test/src/lib/components/chat/ModelSelector/ModelItemMenu.svelte`

菜单项显示逻辑（第55-70行）：
```svelte
<button on:click={() => {
    pinModelHandler(model?.id);
    show = false;
}}>
    {#if ($settings?.pinnedModels ?? []).includes(model?.id)}
        <EyeSlash />
        <div>{$i18n.t('Hide from Sidebar')}</div>
    {:else}
        <Eye />
        <div>{$i18n.t('Keep in Sidebar')}</div>
    {/if}
</button>
```

### 4. 侧边栏展示
- **文件**: `/home/ubuntu/open-webui-test/src/lib/components/layout/Sidebar.svelte:676`

显示固定模型的逻辑：
```svelte
{#if ($models ?? []).length > 0 && ($settings?.pinnedModels ?? []).length > 0}
    <div class="mt-0.5">
        {#each $settings.pinnedModels as modelId (modelId)}
            {@const model = $models.find((model) => model.id === modelId)}
            {#if model}
                <a href="/?model={modelId}"
                   on:click={() => {
                       selectedChatId = null;
                       chatId.set('');
                       if ($mobile) {
                           showSidebar.set(false);
                       }
                   }}>
                    <!-- 模型图标和名称显示 -->
                </a>
            {/if}
        {/each}
    </div>
{/if}
```

## 功能流程

1. **用户操作**: 在模型选择器中，点击模型旁边的菜单按钮
2. **显示选项**: 根据模型是否已固定，显示 "Keep in Sidebar" 或 "Hide from Sidebar"
3. **执行操作**: 点击选项后调用 `pinModelHandler(modelId)`
4. **更新状态**: 
   - 更新本地 `$settings.pinnedModels` 数组
   - 调用后端 API 持久化设置
5. **UI 更新**: 侧边栏自动更新，显示或隐藏相应的模型

## 特点

- 固定的模型显示在侧边栏顶部，方便快速访问
- 点击固定的模型会直接跳转到 `/?model={modelId}`
- 支持多个模型同时固定
- 使用 Set 确保不会重复添加同一模型
- 移动端点击后会自动关闭侧边栏

## 相关文件清单

- 后端 API: `/backend/open_webui/routers/users.py`
- 数据模型: `/backend/open_webui/models/users.py`
- 状态管理: `/src/lib/stores/index.ts`
- PIN 处理: `/src/lib/components/chat/ModelSelector.svelte`
- 菜单组件: `/src/lib/components/chat/ModelSelector/ModelItemMenu.svelte`
- 侧边栏: `/src/lib/components/layout/Sidebar.svelte`