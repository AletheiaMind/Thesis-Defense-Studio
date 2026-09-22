---

## 4.1 系统总体架构设计

Thesis Defense Studio 是一个基于 **Streamlit** 构建的轻量级 AI 辅助论文答辩训练系统，采用"前端展示层—业务逻辑层—AI 服务层—本地状态持久层"四层架构，整体技术栈为纯 Python（100%）。


**核心设计特点：**
- **无后端数据库、无独立服务端**：所有状态保存在 Streamlit 的 `session_state` 中，并通过 `.streamlit/shared_state.json` 做轻量落盘，保证多页面（Home / Document Review / Thesis Defense）切换时数据不丢失。
- **AI 能力与业务解耦**：`generate_ai_text` 是唯一的大模型调用入口，上层三大功能模块（审阅、出题、评分）通过不同的 Prompt 构造函数复用同一接口，便于统一治理超时、重试、日志与模型切换。
- **双模式运行**：既支持 `app.py` 单文件三 Tab 模式，也支持 `pages/` 目录的 Streamlit 原生多页应用（MPA）模式，两者共享 `utils.py` 业务逻辑，避免代码重复。

---
<img src="arch.svg" alt="System architecture">

## 4.2 核心功能模块设计与实现

### 4.2.1 论文全文智能审阅模块

**实现位置**：`pages/2_Document_Review.py` + `utils.py` 中的 `extract_text_from_upload` / `summarize_text` / `review_paper` / `build_review_prompt` / `_parse_ai_review_sections`。

**流程设计：**
1. **多格式解析**：`extract_text_from_upload` 依据文件后缀分流处理——`.txt` 直接解码；`.pdf` 使用 `pypdf.PdfReader` 逐页 `extract_text()` 并拼接；`.docx` 使用 `python-docx` 遍历段落文本拼接。不支持的格式抛出 `ValueError` 由页面层 `try/except` 捕获并以 `st.error` 提示。
2. **摘要压缩**：`summarize_text` 对全文做空白字符归一化后截断（默认 1800 字符），用于后续答辩出题阶段的"论文背景注入"，避免超长文本占满上下文。
3. **审阅 Prompt 构造**：`build_review_prompt` 将学生画像（姓名/学校/年龄）与论文全文拼接为结构化提示词，明确要求模型**仅返回 JSON**（`strengths` / `weaknesses` / `suggestions` / `summary` 四字段），提升结果可解析性。
4. **结果解析容错**：`_parse_ai_review_sections` 采用两级解析策略：
   - 优先尝试剥离 Markdown 代码围栏后做 `json.loads` 严格解析；
   - 若解析失败或字段缺失，退化为基于正则的按行 Markdown 小节识别（支持 `**Strengths:**`、`### Strengths` 等多种标题写法及同义词别名表 `section_aliases`），逐段归类到对应桶中。
5. **展示层**：`st.radio` 做分段切换（Strengths / Weaknesses / Improvement Suggestions / Condensed Summary），配合 `st.metric` 展示字数、字符数统计。

### 4.2.2 AI 虚拟评委出题与模拟答辩问答模块

**实现位置**：`pages/3_Thesis_Defense.py` + `utils.py` 中的 `defense_question` / `build_defense_question` / `local_defense_question`。

**流程设计：**
1. **多轮对话状态机**：以 `st.session_state.defense_turn`（0~10）驱动答辩进度，`defense_history` 存储 `{"role": "assistant"/"user", "content": ...}` 消息列表，通过 `st.chat_message` / `st.chat_input` 渲染类聊天界面，并用进度条实时反映 `turns_done/10`。
2. **上下文裁剪出题**：`build_defense_question` 仅截取最近 4 条历史对话（`recent = list(history)[-4:]`）作为上下文，结合论文摘要（而非全文）生成"严格但公正的答辩老师"提问 Prompt，首轮为开放式挑战性提问，后续为针对上一轮回答的追问，保证问题聚焦且上下文可控。
3. **本地兜底题库**：当 AI 服务不可用时，`local_defense_question` 提供 10 道通用但覆盖研究问题、重要性、假设、评估方法、批评、创新点、改进方向、薄弱环节、答辩策略、核心结论的固定题库，按轮次索引取用，保证系统在无 API Key 情况下依然可完整演示答辩流程。
4. **终局评审**：满 10 轮后调用 `defense_report` → `build_final_defense_report`，将完整对话历史与论文摘要一并提交模型，要求输出包含 Defense Summary / Strengths / Concerns / Final Score / Final Verdict 的结构化 Markdown 报告。

### 4.2.3 多维度量化评分与改进建议输出模块

**实现位置**：`utils.py` 中的 `build_final_defense_report` / `local_defense_report`，及审阅模块的 `suggestions` 字段。

- **量化评分**：AI 路径下由模型基于完整问答历史给出百分制 `Final Score`；本地兜底路径 `local_defense_report` 采用启发式公式 `score = max(60, 92 - max(0, 10 - rounds) * 2)`，保证在无网络/无 Key 时仍能给出合理区间的确定性分数（避免评分为空或异常波动）。
- **多维反馈**：审阅模块的 Strengths / Weaknesses / Suggestions 三段式反馈，与答辩模块的 Defense Summary / Strengths / Concerns / Final Verdict 五段式报告，共同构成"论文质量维度 + 答辩表现维度"的双轨量化评估体系。
- **可扩展性**：当前评分逻辑集中在 Prompt 层（由模型自行给出维度权重），后续可将各维度（逻辑性、创新性、表达清晰度、抗压应变等）拆分为独立字段并加权计算，进一步提升评分的可解释性和一致性。

---

## 4.3 风险应对方案：AI 幻觉抑制、长文本溢出处理、论文隐私保护方案

| 风险类别 | 现状/触发点 | 应对方案 |
|---|---|---|
| **AI 幻觉抑制** | 模型可能编造论文中不存在的内容或给出格式混乱的评审结果 | 1）Prompt 层强约束输出 Schema（`build_review_prompt` 要求"仅返回合法 JSON"，`build_final_defense_report` 要求固定 Markdown 小节结构），降低自由发挥空间；2）`_parse_ai_review_sections` 双级解析容错，JSON 失败自动走结构化正则兜底，避免脏数据直接展示给用户；3）出题与评审均**锚定论文摘要/对话历史**作为唯一事实来源（"Use this paper summary to stay grounded in the topic"），减少无依据发散；4）当 AI 返回空/异常时，`review_paper`、`defense_question`、`defense_report` 统一 fallback 到本地确定性规则（`local_*` 系列函数），从产品层面兜底避免呈现幻觉内容。建议后续增强：引入答案与原文的相似度校验、关键引用溯源高亮、多轮自我一致性投票等机制。 |
| **长文本溢出处理** | 论文全文可能远超模型上下文窗口，尤其是答辩多轮对话叠加原文会持续增长 | 1）`summarize_text(text, limit=1800)` 在上传阶段即对全文做归一化截断，答辩/追问阶段仅使用摘要而非全文，从源头控制单次请求体量；2）`build_defense_question` 仅取最近 4 条历史消息作为上下文（滑动窗口机制），避免对话历史随轮次线性增长导致 token 溢出；3）`generate_ai_text` 中显式设置 `max_tokens=2048` 限制单次响应长度，并通过可配置的 `get_nvidia_api_timeout`（默认 120s）防止长请求阻塞。建议后续增强：对超大文档（如超长学位论文）增加分段摘要+层级压缩（map-reduce式摘要），以及基于 token 计数而非字符计数的更精确截断策略。 |
| **论文隐私保护** | 论文原文包含学生个人信息、未发表研究成果，存在数据泄露风险 | 1）**无持久化数据库**：论文全文仅存在于内存 `st.session_state` 和本地 `.streamlit/shared_state.json`（可配置为不持久化或加密落盘），不上传至第三方存储；2）API Key 通过 `st.secrets` / 环境变量管理，代码中已注释禁用明文环境变量读取方式（`get_nvidia_api_key`），降低密钥泄露风险；3）调试日志 `generate_ai_text` 中对 `Authorization` 请求头做 `***REDACTED***` 脱敏处理后才打印，避免密钥随日志外泄；4）`NVIDIA_DEBUG` 调试开关默认关闭，仅在显式开启时才输出请求详情，减少生产环境敏感信息误打印风险。建议后续增强：论文文本发送前进行 PII（姓名/学号/单位）自动脱敏或匿名化替换、增加用户可选的"仅本地评审（不出网）"模式、对第三方 API 调用增加数据不留存承诺审计、传输链路强制 TLS 校验与请求签名。 |

---

## 4.4 "需求发起-AI 生成-实操演练-用户反馈-模型迭代"服务闭环构建

结合现有代码结构，可将系统扩展为如下闭环运营体系：

1. **需求发起**：学生在 Home 页填写 `profile`（姓名/年龄/学校）并上传论文（Document Review 页），构成一次明确的"服务请求"，`save_profile` / `save_uploaded_document` 完成需求的结构化采集与状态落盘。
2. **AI 生成**：`review_paper` 与 `defense_question` / `defense_report` 基于 Prompt 工程调用统一的 `generate_ai_text` 接口，生成审阅报告与答辩问答，是当前系统已具备的核心自动化生产能力。
3. **实操演练**：`pages/3_Thesis_Defense.py` 提供 10 轮沉浸式模拟问答（`st.chat_message` / `st.chat_input`），学生在真实交互中演练应答策略，进度条与轮次统计（`defense_turn`）量化演练完成度。
4. **用户反馈**（待补全，建议新增）：
   - 在 Review 结果页与 Defense 终局报告页增加"评分是否准确 / 建议是否有帮助"的轻量反馈组件（如 `st.feedback` 或点赞/点踩+文本框）；
   - 反馈数据结构建议：`{profile, doc_hash, review_result/defense_report, rating, comment, timestamp}`，写入独立的反馈存储（当前 `shared_state.json` 可扩展为 `feedback_log.jsonl` 追加写入，或后续迁移至轻量数据库）。
5. **模型迭代**（待补全，建议新增）：
   - 基于反馈日志定期分析低分/差评样本，针对性优化 `build_review_prompt`、`build_defense_question`、`build_final_defense_report` 的措辞与约束条件（Prompt 迭代成本最低，优先实施）；
   - 对反复出现的解析失败案例，扩充 `_parse_ai_review_sections` 的 `section_aliases` 别名库；
   - 中长期可积累"用户反馈+人工复核"标注数据，用于对模型进行少样本示例（Few-shot）调优或针对性微调，并通过 A/B 对比（新旧 Prompt/模型版本）验证迭代效果后再全量上线。

**闭环示意：**

```
学生画像+论文上传 → Prompt构造+NVIDIA API生成 → 10轮模拟答辩实操
        ↑                                                │
        └── Prompt/别名库/兜底逻辑迭代 ← 反馈日志分析 ← 用户评分/评论反馈 ┘
```

当前代码已完整覆盖闭环中"需求发起→AI生成→实操演练"三个环节，"用户反馈"与"模型迭代"环节为下一阶段建议重点建设内容，可作为项目后续里程碑规划。

## 4.5  与“LLM-as-a-Judge”范式的关系

本项目的核心方法论与“LLM-as-a-Judge”范式高度契合，实质上是将大语言模型作为“论文评审器”与“答辩评委”参与教学训练与质量评价过程。系统中，AI 不仅负责对上传论文进行文本理解与分析，还承担了审阅意见生成、追问式答辩提问、最终评分与结论输出等评判任务，形成了一个典型的 LLM 角色替代人工评审的应用场景。

从功能上看，系统中的 “论文全文智能审阅模块”可视为 LLM-as-a-Judge 的论文评审子任务：模型依据论文内容、学术逻辑、表达结构和改进方向等维度输出 “优点、问题、改进建议、总体摘要” 四类评审结论；“AI 虚拟评委出题与模拟答辩问答模块”则进一步模拟了评委在答辩现场的问答与追问场景，要求模型根据论文背景与学生回答进行针对性追问；“多维度量化评分与改进建议输出模块”则是将评判结果转化为可量化的分数和定性结论，实现从“主观意见”到“结构化评价”的转换。也就是说，本项目不是简单的生成式问答系统，而是把 LLM 当作评审者，参与学术评价与反馈闭环。

同时，本项目也体现了 LLM-as-a-Judge 的典型设计原则：一是通过 Prompt 约束输出格式，统一评审结果的结构；二是通过 JSON 解析与 Markdown 解析的双重容错机制，确保评审结果可被系统稳定消费；三是通过“论文摘要—历史对话—评分结论”的链式输入，控制评委判断的上下文规模，减少幻觉和长文本溢出；四是通过本地 fallback 机制，确保在 API 不可用时仍能输出合理的评审与评分结果。

需要说明的是，本项目更偏向“面向训练场景的 LLM-as-a-Judge 助手”，而非完全自动化的学术判定系统。它将 AI 作为“评委代理”参与过程，并将结果作为学生改进论文与提升答辩能力的反馈依据，真正体现了“AI 评审 + 人类决策”的协同机制。在学术教育、能力训练和 AI 赋能教学场景中，本项目具有较强的实践价值，也为 LLM-as-a-Judge 在高阶知识评估任务中的落地提供了可复制的范式参考。