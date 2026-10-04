"""Render editable SVG and publication PNG from one explicit mechanism specification."""
from pathlib import Path
from html import escape
import json
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parents[1]
ASSETS=ROOT/'articles/assets'
ASSETS.mkdir(parents=True,exist_ok=True)
MANIFEST=json.loads((ROOT/'validation/column-manifest.json').read_text())
FONT=Path('/System/Library/Fonts/STHeiti Medium.ttc')
if not FONT.exists():
    raise SystemExit('Set FONT to an available Chinese font before rendering on another platform.')
DATA={
1:('flow','目标续跑的接纳过程',[
 ('目标服务','保存描述、修订身份和回合额度'),('提交 goal/change','事实追加之后才通知观察者'),
 ('续跑准入','检查 idle、授权；checkpoint 后重查'),('预留并入队','携带 goalId、revision、round'),
 ('接纳并追加 user/message','fold 验证身份并推进 roundsStarted'),('模型与工具执行','循环结束与业务验收分别判断')], '正常续跑主线；日志提交不等于立即磁盘 flush'),
2:('flow','从输入到多步骤循环',[
 ('输入 inbox','followup 与 steer 选择不同接纳位置'),('preStep','claim → assembly → 准入 waterfall'),
 ('请求准备','绑定路由，提交输入，构造请求'),('模型结算与工具','assistant/message → 工具 → tool/result'),
 ('步骤收尾','step/end；必要时进入下一 Step'),('回合收尾','stopping 后重查输入，再 turn/end')], '同一步骤可有多次 attempt；idle 不是业务成功'),
3:('flow','一次模型调用的绑定过程',[
 ('选择路由','agent/request 提供 provider / model'),('prepareCall','捕获注册并解析精确模型能力'),
 ('固定调用描述','冻结配置、能力与一次性句柄'),('适配历史与输入','处理模态、工具更新和 replayState'),
 ('派发绑定实现','拒绝句柄复用或配置错配')], '共同输入统一；供应商差异仍须显式保留'),
4:('flow','上下文压力处理支线',[
 ('测量当前 surface','使用 token meter 与精确路由窗口'),('压力判定','结合输出预留与策略阈值'),
 ('裁剪并重测','按需执行无需模型的结果裁剪'),('选择摘要范围','保留尾部，维持工具调用与结果配对'),
 ('摘要与校验','有效完整输出；取消和范围稳定性检查'),('提交替换视图','记录摘要与 surfaceOp，历史事实保留')], '溢出恢复须有视图进展；不保证摘要语义无损'),
5:('flow','会话持久化与恢复',[
 ('Session.append','校验、快照、seq、日志与通知'),('live writer 缓冲','事件等待有界批处理'),
 ('有序写入与 flush','持久 handle 建立实际存储屏障'),('写 open 与有效前缀','先取得所有权，再读取日志'),
 ('逻辑闭合与重建','补 unknown 等事实，重建 Session'),('后续唤醒才执行','读取、恢复、fork 不重做历史')], '示意主线；后台作业和临时 diff 不是日志恢复对象'),
6:('flow','工具结果形成的顺序',[
 ('记录 tool/call','解析参数与调度分类'),('准备与审批','pre-execute；ask 必须取得 grant'),
 ('guard 与取消检查','批准不绕过剩余限制'),('body 与规范结果','外部副作用可能已经发生'),
 ('finalize 与观察','post / content；tools/result 通知'),('Loop 追加 tool/result','按模型调用顺序进入后续历史')], '观察者后续成功与工具 outcome 分别核对'),
7:('pairs','不同失败需要不同恢复依据',[
 ('模型请求失败','attempt 与 request-error','策略退避 / 输入修复','按失败类型决定是否重试'),
 ('工具缺少最终结果','已记录开始，结果未记录','TOOL_OUTCOME_UNKNOWN','外部状态查询；不盲目重做'),
 ('取消或工具 deadline','请求停止，不再新增派发','等待在途结算','释放资源仍依赖协作式停止')], 'checkpoint 缩小缺口，不提供外部副作用统一回滚'),
8:('pairs','三套局部资源治理',[
 ('工具调度','一个 Loop 的工具组','安全 body 有限并行','结果按模型顺序提交'),
 ('后台 jobs','精确 owner 的生产者','running + stopping','真实结算后才释放活跃额度'),
 ('子 Agent','独立 Loop 与结果','深度 / 活跃容量','父 signal、结果检查与 dispose')], '局部额度不会自动组成跨 Agent 全局调度'),
9:('flow','一次敏感操作的检查层次',[
 ('工具可见性','注册范围与 restriction'),('pre-execute 决策','allow / deny / cancel / ask'),
 ('必要时审批','只有 allowed-once 授予本次权力'),('guard 与取消','等待后仍须确认执行有效'),
 ('资源 provider','实际文件目标或进程隔离检查')], '缺审批通道的 ask 拒绝；Scope 本身不是沙箱'),
10:('flow','规划退出的状态提交',[
 ('计划读取与用户审阅','校验内容，等待明确答复'),('精确批准','单项批准且没有 custom 回复'),
 ('pending intent','当前工具 batch 保持规划指导'),('下一 preStep 组装','提示段可读取待应用模式'),
 ('准入 waterfall 接受','拒绝或取消不提交模式'),('追加 plan/mode','事实落地后按新的模式推进')], '图示规划支线；工具授权与目标准入分别控制'),
11:('pairs','上限约束不同执行对象',[
 ('maxGoalRounds','目标 driver 与 fold','已接纳自动回合','不计同 Step 的多次 attempt'),
 ('normal maxRetries','provider / policy 状态','该步骤请求恢复','always 不受此次数条件约束'),
 ('maxTokens','本次模型请求','单次输出额度','不包含整个任务所有调用')], '摘要、委派和累计费用需要另设任务级口径'),
12:('flow','反馈授权的 Session 遥测',[
 ('反馈事实提交','新 canonical 事件，而非任意 emit'),('OTel reporter 授权','检查 Session 自有后缀与身份'),
 ('coordinator 捕获前缀','按 throughSeq 和交接游标读取'),('复制并走 redaction','没有附加规则时原样通过'),
 ('backend.emit','记录进入后端处理'),('推进 handoff cursor','进程内交接，不是 collector ACK')], '本地 ledger、实时显示与外发遥测各有职责'),
13:('pairs','验证层次与结论范围',[
 ('源码 / 类型 / 构建','查看路径、签名与产物','实现和接口依据','不等于运行时已经生效'),
 ('真实 runtime + 受控边界','保留 Loop、工具和 Session','执行契约与异常路径','不等于真实供应商兼容'),
 ('真实入口与外部断言','检查文件、命令和实际界面','业务结果与部署行为','结论仍限定环境和任务集合')], '完成标记和模型自述不能替代独立业务验收'),
14:('flow','扩展参与完整生命周期',[
 ('依赖解析','服务定义、provider 与 consumer'),('Fiber 激活','配置、epoch 与加载检查'),
 ('贡献注册','listener、工具与服务归属 effect'),('在途回调','await 期间 owner 可能变化'),
 ('撤销、取消与排空','分别处理注册和正在执行的工作'),('资源释放','历史 Session 状态不自动删除')], '生命周期示意；实际释放顺序由 owner 实现决定'),
15:('pairs','三种用户可见结果',[
 ('SDK prompt 响应','返回 messageId','输入接纳身份','不是任务完成或独占 Turn'),
 ('present','检查文件并声明','deliverables/presented','文件引用，不是永久内容归档'),
 ('workspace-changes','按 Turn 基线记录修改','日志身份与临时 diff','完整 summary / sources 依赖缓存')], '重连 baseline 不能补回进程丢失的未结算字块'),
16:('pairs','升级需要分别处理的对象',[
 ('代码与配置','profile、Entry 与 HMR','激活与失败审计','局部恢复不是全树事务'),
 ('在途实例','Agent、provider 和生产者','停止接纳并排空','不能只替换注册就释放资源'),
 ('会话数据','codec、迁移、generation','旧格式与新状态兼容','保留前代不等于任意降级')], '入口验证、数据兼容和外部副作用分别承担义务'),
}

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
