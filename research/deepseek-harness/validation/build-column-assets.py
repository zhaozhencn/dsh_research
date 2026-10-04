"""Render editable SVG and publication PNG from one explicit mechanism specification."""
from pathlib import Path
from html import escape
import json
import os
import subprocess
import sys
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parents[1]
ASSETS=ROOT/'articles/assets'
ASSETS.mkdir(parents=True,exist_ok=True)
MANIFEST=json.loads((ROOT/'validation/column-manifest.json').read_text())
FONT=Path(os.environ.get('DSH_COLUMN_FONT', '/System/Library/Fonts/STHeiti Medium.ttc'))
if not FONT.exists():
    raise SystemExit('Set FONT to an available Chinese font before rendering on another platform.')
DATA={1: ('flow',
     'Goal、Driver 与 Loop 的交接',
     [('Goal service', 'create / edit 生成 id 与 revision'),
      ('Session / goal/change', '提交目标事实后通知 consumer'),
      ('Driver / readyToDrive', 'idle 与 activation；checkpoint 后复核'),
      ('RoundAttempt / Inbox', '先保存预留，再 followup 入队'),
      ('Loop / user/message', '接纳后 fold 推进 roundsStarted'),
      ('Completion / acceptance', 'Turn 结束、目标完成与业务验收分别确认')],
     '主线按交接展开；append 与 flush 是不同边界'),
 2: ('flow',
     'Agent Loop：组件与执行主线',
     [('Input / Inbox', 'send() 选择 next-turn / next-step'),
      ('Driver / ReactLoopAgent', 'Phase 管活动；wakeDriver() → kick() → turn()'),
      ('Admission / preStep()', 'claim → PromptAssembly → PreparedStep'),
      ('Request / step() 与 LLM', 'prepareRequest() → buildRequest() → stream()'),
      ('Tool runtime / executeToolCalls()', 'runGroup() 调度；tool/result 与 context 分别回流'),
      ('Session / facts 与 surface', '记录 Step、Turn 边界；派生后续 messages')],
     'Session 贯穿执行；Turn / Step / attempt 分层推进'),
 3: ('flow',
     'PreparedLlmCall 的绑定与派发',
     [('Loop / route proposal', 'agent/request 提供 provider / model'),
      ('LLM / prepareCall', '捕获 registration，再 await 模型能力'),
      ('PreparedLlmCall', 'config、能力与绑定 stream 一起交接'),
      ('Request projection', '处理 input modalities、tools 和 replayState'),
      ('Bound stream', '检查单次使用与 config，再派发同一实现')],
     '从准备到发送使用同一次 registration'),
 4: ('flow',
     'Compaction 如何改变请求视图',
     [('TokenMeasurement', '当前 route 下的 baseline、delta 与 nodes'),
      ('ResolvedCompactSpec', 'contextWindow 扣除输出预留与 headroom'),
      ('Prune / remeasure', '先做无模型裁剪，再核对实际压力'),
      ('SurfaceSelection', '选择连续范围，保持 tool call / result 配对'),
      ('PreparedCompaction', '摘要返回后复核 signal 和选区身份'),
      ('Session / surfaceOp', '提交 summary 与 replacement，保留原事实')],
     '测量、选区、摘要与提交分别保存依据'),
 5: ('flow',
     'Session 事实如何进入恢复实例',
     [('Session.append', '快照校验 → seq → log → live 通知'),
      ('Live writer / buffer', '复制后的事件等待 batch drain'),
      ('Handle / operation chain', '连续写入；flush 等待持久屏障'),
      ('Resume / write open', '先取得 claim 与 lease，再 read'),
      ('Repair / Session seed', '补缺失结果与边界，再重建 projection'),
      ('New input / driver', '新执行由后续输入唤醒')],
     '写入与读取是相接的两条路径；历史工具不重做'),
 6: ('flow',
     'Tool runtime 从调用到规范结果',
     [('Loop / tool/call', '保存 callId 与 callSeq，解析参数'),
      ('Runtime / prepare', 'pre-execute → approval → guards'),
      ('Dispatch / body', '融合 callerSignal 后执行实际操作'),
      ('Outcome / value + content', '校验规范 value，render 模型内容'),
      ('Finalize / tools/result', 'post 与 finalContent 后通知 observer'),
      ('Loop / tool/result', '按模型顺序提交，再接纳 additionalContexts')],
     '规范 outcome、历史结果与业务回执各有来源'),
 7: ('pairs',
     '恢复动作分别消费什么证据',
     [('LLM failure', 'attempt settlement → request-error', 'Retry / compaction', 'failure 分类与输入进展支持恢复决定'),
      ('Missing tool result', 'ToolCallRecovery 中有 callSeq', 'TOOL_OUTCOME_UNKNOWN', '查询 operationId，再选择业务恢复动作'),
      ('Cancel / deadline', 'signal 请求停止；关闭新增派发', 'Drain / settlement', '等待已启动工作，再释放管理资源')],
     'checkpoint 保存本地证据；外部结果由回执确认'),
 8: ('pairs',
     '并发对象、提交和释放',
     [('Tool group', 'PlannedCall / inFlight / Slot', 'Model-ordered commit', 'body 可重叠，committed 按模型顺序推进'),
      ('Local job', 'TrackedJob / producer / pump', 'running + stopping', 'settled 后结束活跃计数'),
      ('Child Agent', '独立 Loop、Session 与 handle', 'Result + dispose', '父 signal、结果检查与资源释放分别处理')],
     '局部额度以各自对象的实际生命周期为依据'),
 9: ('flow',
     '敏感文件操作的执行资格',
     [('Tool visibility', 'scoped ToolRestriction 约束可见集合'),
      ('Pre-execute decision', 'allow / deny / cancel / ask'),
      ('ApprovalRequestEvent', 'ask 只接受受控 allowed-once'),
      ('Guard / callerSignal', '检查剩余限制及等待后的取消'),
      ('FS provider / fresh target', '重新解析、检查路径，再交给实际 write')],
     '文件主线；进程 confinement 使用独立 provider'),
 10: ('flow',
      'Plan intent 如何成为模式事实',
      [('exit_plan_mode', '读取计划，校验审阅条件'),
       ('User question service', '等待明确批准；检查 signal 和插件寿命'),
       ('pendingIntents', '保存 active / narrate，当前 batch 保持政策'),
       ('Loop / preStep assembly', 'plan:policy 回调消费 pending 选择'),
       ('Pre-step waterfall', 'accepted 且仍有效时调用 onBoundary'),
       ('Session / plan/mode', 'append 成功后清除 pending')],
      '选择、提示组装与事实提交分别发生'),
 11: ('pairs',
      'Budget 字段的单位与作用域',
      [('maxGoalRounds', 'goal driver / fold', 'Accepted Goal round', '同 Step 的 retry attempt 不增加 round'),
       ('normal / maxRetries', 'provider + policyKey 的状态', 'Current Step retries', 'always 使用不同的次数政策'),
       ('maxTokens', 'LlmCallConfig 中的单次参数', 'One-call output', '主请求、summary 和 child 各自产生消耗')],
      '任务账本需连接完整调用树；正文将其列为扩展'),
 12: ('flow',
      'Feedback 到 telemetry handoff',
      [('Session / canonical feedback', '合法反馈事实提交在自有后缀'),
       ('OTel reporter', '确认授权；on-demand 捕获'),
       ('Coordinator / throughSeq', '从 handoffCursor 后读取授权前缀'),
       ('SessionTelemetryRecord', '复制 envelope / body，进入 redaction'),
       ('Sink / backend.emit', '接受 record 进入后端 pipeline'),
       ('PendingRecord.seq', '推进进程内交接位置')],
      'handoff 之后还有独立传输与 collector 接收'),
 13: ('pairs',
      '测试证据怎样支撑运行契约',
      [('Static / build evidence', '类型、接口、源码与编译产物', 'Declared contract', '检查接口形态和指定产物'),
       ('Controlled integration', '实际 Loop、tools、Session 与脚本模型', 'Runtime protocol', '断言提交、回流、取消与释放'),
       ('Independent acceptance', '指定入口、任务集与外部产物', 'Business result', '检查具体版本、测试命令与可信回执')],
      '每层保存输入、替身、断言与结论范围'),
 14: ('flow',
      'Extension 的注册、消费与清理',
      [('Definition / dependencies', '声明 inject 与能力契约'),
       ('Provider / realm', '提供实现；notify 唤醒 consumer'),
       ('Fiber / epoch', '异步加载复核依赖身份'),
       ('Context / effects', '注册 listener、tool 与 disposer'),
       ('Lifetime / in-flight work', '撤销未来入口；取消并排空旧回调'),
       ('Owner / disposal', '等待资源释放；历史状态单独处理')],
      '生命周期地图；具体清理顺序由 owner 代码决定'),
 15: ('pairs',
      '交互结果的身份与内容来源',
      [('SDK / SessionPromptResult', 'messageId 对应排队输入', 'Input receipt', '由后续 user/message 与 Turn 事实确认消费'),
       ('Present / pending', '文件检查 → finalized tools/result', 'deliverables/presented', '声明文件引用；内容与访问另行检查'),
       ('Workspace / TurnRecord', 'summary 与 FileSources 对齐', 'Changes + diff source', '事件保存 turn，丰富内容依赖真实来源')],
      '接纳、声明与可访问内容共同组成交付链'),
 16: ('pairs',
      'Deployment 变化的三类对象',
      [('Entry / Reload', '候选配置、模块与运行树', 'Activation audit', '准备、等待和审计决定新组合是否可用'),
       ('Fiber / live Agent', '旧 driver、provider 和 producer', 'Drain / release', '先停止新增，再等待既有工作结束'),
       ('PreparedJsonlMigration', 'sourceIdentity / artifact / publish', 'Successor generation', '取得写所有权后发布转换结果')],
      '代码注册、实例寿命和状态兼容分别验收')}

def draw(n,row):
    kind,title,items,note=DATA[n]
    width=1200; y0=170; boxheight=154; gap=64
    count=len(items)
    height=y0+count*(boxheight+gap)+150
    if kind=='pairs':height=1730
    im=Image.new('RGB',(width,height),'#f6f8fb');d=ImageDraw.Draw(im)
    font=ImageFont.truetype(str(FONT),46);small=ImageFont.truetype(str(FONT),34);heading=ImageFont.truetype(str(FONT),52)
    parts=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">', '<rect width="100%" height="100%" fill="#f6f8fb"/>']
    def text(x,y,value,size=46,color='#182d49'):
        use=heading if size==52 else small if size==34 else font
        assert d.textbbox((0,0),value,font=use)[2]<=width-100, value
        d.text((x,y),value,font=use,fill=color,anchor='mt')
        parts.append(f'<text x="{x}" y="{y+size}" text-anchor="middle" font-family="Heiti SC, PingFang SC, sans-serif" font-size="{size}" fill="{color}">{escape(value)}</text>')
    def box(x,y,w,h,main,detail):
        d.rounded_rectangle((x,y,x+w,y+h),radius=18,fill='white',outline='#c5d1df',width=2)
        parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="18" fill="white" stroke="#c5d1df" stroke-width="2"/>')
        for value,use in [(main,font),(detail,small)]:assert d.textbbox((0,0),value,font=use)[2]<=w-36, value
        text(x+w/2,y+22,main);text(x+w/2,y+91,detail,34,'#516781')
    def arrow(x1,y1,x2,y2):
        d.line((x1,y1,x2,y2),fill='#7390ac',width=4)
        if x1==x2:tri=[(x2,y2),(x2-9,y2-14),(x2+9,y2-14)]
        else:tri=[(x2,y2),(x2-14,y2-9),(x2-14,y2+9)]
        d.polygon(tri,fill='#7390ac')
        points=' '.join(f'{x},{y}' for x,y in tri)
        parts.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#7390ac" stroke-width="4"/><polygon points="{points}" fill="#7390ac"/>')
    text(600,27,f'{n:02} / 从源码理解 Agent Harness',34,'#516781');text(600,83,title,52)
    if kind=='flow':
        for i,(main,detail) in enumerate(items):
            y=y0+i*(boxheight+gap);box(80,y,1040,boxheight,main,detail)
            if i+1<count:arrow(600,y+boxheight+10,600,y+boxheight+gap-10)
        bottom=y0+count*(boxheight+gap)+15
    else:
        for i,(a,b,c,f) in enumerate(items):
            y=190+i*460;box(80,y,1040,154,a,b);box(80,y+213,1040,154,c,f);arrow(600,y+164,600,y+203)
        bottom=1570
    text(600,bottom,note,34,'#516781')
    text(600,bottom+55,'研究基线 5badb15009ae · 机制示意，非全量调用图',34,'#657a92')
    stem=Path(row['file']).stem
    im.save(ASSETS/f'{stem}.png',dpi=(160,160),optimize=True)
    parts.append('</svg>');(ASSETS/f'{stem}.svg').write_text('\n'.join(parts)+'\n')
    return {'article':n,'stem':stem,'width':width,'height':height,'kind':kind,'title':title,'nodes':items,'note':note,'png':f'articles/assets/{stem}.png','svg':f'articles/assets/{stem}.svg'}

rows=[draw(n,row) for n,row in enumerate(MANIFEST['articles'],1)]
(ASSETS/'diagrams.json').write_text(json.dumps({'sha':MANIFEST['sha'],'font':str(FONT),'renderer':'Pillow 11.3.0; SVG geometry from same specification','figures':rows},ensure_ascii=False,indent=2)+'\n')
sheet=Image.new('RGB',(1600,2200),'white')
for i,row in enumerate(rows):
    im=Image.open(ROOT/row['png']);im.thumbnail((380,525))
    sheet.paste(im,(10+(i%4)*400,10+(i//4)*550))
sheet.save(ROOT/'validation/column-contact-sheet.png')
print('Rendered 16 PNGs, 16 editable SVGs and contact sheet.')

# Rebuild the complete set when the supplemental specification is present.
if (ASSETS/'diagram-supplements.json').exists():
    subprocess.run([sys.executable, str(ROOT/'validation/build-column-supplements.py')], check=True)
