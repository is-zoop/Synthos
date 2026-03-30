import React, { useState } from 'react';
import { Home, LayoutGrid, Users, Settings, Plus, ArrowLeft, ArrowRight, Search, CheckSquare, Square } from 'lucide-react';

const InteractivePreview: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'dashboard' | 'tools' | 'admin'>('dashboard');

  return (
    <section id="ecosystem" className="py-24 bg-white overflow-hidden">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <h2 className="text-3xl md:text-4xl font-bold text-slate-900 mb-4">熟悉的界面，更强大的内核</h2>
          <p className="text-lg text-slate-600">采用现代化 UI 设计，还原原生桌面体验，流畅且高效。</p>
        </div>

        {/* Window Container */}
        <div className="relative max-w-5xl mx-auto rounded-xl shadow-2xl shadow-slate-400/20 border border-slate-200 bg-[#f3f3f3] overflow-hidden aspect-[16/10] md:aspect-[16/9] flex flex-col">
          
          {/* Title Bar */}
          <div className="h-10 bg-white border-b border-slate-200 flex items-center justify-between px-4 select-none">
            <div className="flex items-center gap-4">
              <div className="flex gap-2">
                <div className="w-3 h-3 rounded-full bg-red-400"></div>
                <div className="w-3 h-3 rounded-full bg-amber-400"></div>
                <div className="w-3 h-3 rounded-full bg-green-400"></div>
              </div>
              <div className="flex items-center gap-2 text-sm text-slate-500">
                <div className="w-4 h-4 bg-primary-500 rounded flex items-center justify-center">
                   <span className="text-[8px] text-white font-bold">S</span>
                </div>
                Synthos
              </div>
              <div className="flex gap-3 text-slate-400">
                <ArrowLeft className="w-4 h-4" />
                <ArrowRight className="w-4 h-4" />
              </div>
            </div>
          </div>

          <div className="flex flex-1 overflow-hidden">
            {/* Sidebar */}
            <div className="w-16 bg-white border-r border-slate-200 flex flex-col items-center py-4 gap-6">
              <button 
                onClick={() => setActiveTab('dashboard')}
                className={`p-2 rounded-lg transition-all ${activeTab === 'dashboard' ? 'bg-primary-50 text-primary-600' : 'text-slate-400 hover:text-slate-600'}`}
              >
                <Home className="w-6 h-6" />
              </button>
              <button 
                onClick={() => setActiveTab('tools')}
                className={`p-2 rounded-lg transition-all ${activeTab === 'tools' ? 'bg-primary-50 text-primary-600' : 'text-slate-400 hover:text-slate-600'}`}
              >
                <LayoutGrid className="w-6 h-6" />
              </button>
              <button 
                onClick={() => setActiveTab('admin')}
                className={`p-2 rounded-lg transition-all ${activeTab === 'admin' ? 'bg-primary-50 text-primary-600' : 'text-slate-400 hover:text-slate-600'}`}
              >
                <Users className="w-6 h-6" />
              </button>
              <div className="mt-auto text-slate-400">
                <Settings className="w-6 h-6" />
              </div>
            </div>

            {/* Content Area */}
            <div className="flex-1 bg-[#f8f9fb] p-6 overflow-y-auto relative">
              
              {/* TAB: DASHBOARD */}
              {activeTab === 'dashboard' && (
                <div className="animate-in fade-in zoom-in-95 duration-300 space-y-6">
                  <h2 className="text-2xl font-bold text-slate-800">欢迎回来，翻斗花园老爷爷！</h2>
                  
                  {/* Stats Cards */}
                  <div className="grid grid-cols-4 gap-4">
                    {[
                      { label: '已发布的应用', val: '12', icon: LayoutGrid },
                      { label: '近7天更新', val: '3', icon: Settings },
                      { label: '近30天发布', val: '2', icon: Plus },
                      { label: '已为您节省时间', val: '240分钟', icon: Users, highlight: true },
                    ].map((stat, i) => (
                      <div key={i} className="bg-white p-4 rounded-xl shadow-sm border border-slate-100">
                        <div className="w-10 h-10 rounded-full bg-orange-50 flex items-center justify-center mb-3">
                          <stat.icon className="w-5 h-5 text-orange-500" />
                        </div>
                        <div className="text-xs text-slate-500 mb-1">{stat.label}</div>
                        <div className={`text-xl font-bold ${stat.highlight ? 'text-primary-600' : 'text-slate-800'}`}>{stat.val}</div>
                      </div>
                    ))}
                  </div>

                  {/* Calendar & Log */}
                  <div className="grid grid-cols-3 gap-6">
                    <div className="col-span-2 bg-white p-6 rounded-xl shadow-sm border border-slate-100">
                      <div className="flex justify-between items-center mb-6">
                         <h3 className="font-bold text-slate-700">更新日志</h3>
                         <span className="text-sm text-slate-400">2025年 11月</span>
                      </div>
                      {/* Mock Calendar */}
                      <div className="grid grid-cols-7 gap-4 text-center text-sm">
                        {['周日','周一','周二','周三','周四','周五','周六'].map(d => <div key={d} className="text-red-500 font-medium">{d}</div>)}
                        {Array.from({length: 30}).map((_, i) => (
                           <div key={i} className={`py-2 rounded-lg ${i === 23 ? 'bg-primary-500 text-white shadow-lg shadow-primary-500/30' : 'text-slate-600 hover:bg-slate-50'}`}>
                             {i + 1}
                           </div>
                        ))}
                      </div>
                    </div>
                    <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-100">
                      <div className="flex gap-4 mb-4 border-b border-slate-100 pb-2">
                        <span className="font-bold text-primary-600 border-b-2 border-primary-600 pb-2 -mb-2.5">收藏</span>
                        <span className="text-slate-400">常用</span>
                      </div>
                      <div className="h-48 flex items-center justify-center text-slate-300 bg-slate-50 rounded-lg border border-dashed border-slate-200">
                        暂无收藏
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* TAB: TOOLS */}
              {activeTab === 'tools' && (
                <div className="animate-in fade-in zoom-in-95 duration-300 h-full flex gap-4">
                  {/* Sidebar Categories */}
                  <div className="w-48 shrink-0 space-y-1">
                    <div className="px-3 py-2 text-xs font-bold text-slate-400 uppercase tracking-wider">目录</div>
                    {['天猫运营工具', '商品运营工具', '抖音运营工具', '京东运营工具', '得物运营工具', '脚本开发工具'].map((item, i) => (
                      <div key={i} className={`px-4 py-3 rounded-lg text-sm font-medium cursor-pointer ${i===0 ? 'bg-white shadow-sm text-primary-600 border-l-4 border-primary-500' : 'text-slate-600 hover:bg-slate-100'}`}>
                        {item}
                      </div>
                    ))}
                  </div>

                  {/* Tool List */}
                  <div className="flex-1 space-y-3">
                    <div className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">列表</div>
                    {[
                      { title: '鹿班测图工具', desc: '按照款号批量获取本地图片上传至鹿班并自动上线测图', color: 'bg-slate-800' },
                      { title: '天猫直播闪降工具', desc: '闪降活动创建、闪降商品push或批量取消闪降商品', color: 'bg-red-500' },
                      { title: '淘宝直播营销中心工具', desc: '淘宝直播营销中心主图打标、库存追加工具', color: 'bg-red-600' },
                      { title: '天猫国际货品发布', desc: '自动填写天猫国际商品属性与规格', color: 'bg-purple-600' },
                    ].map((tool, i) => (
                      <div key={i} className="bg-white p-4 rounded-xl border border-slate-100 shadow-sm flex items-center gap-4 group hover:border-primary-200 transition-all">
                        <div className={`w-12 h-12 ${tool.color} rounded-xl flex items-center justify-center text-white font-bold text-lg shrink-0`}>
                          {tool.title[0]}
                        </div>
                        <div className="flex-1">
                          <h4 className="font-bold text-slate-800">{tool.title}</h4>
                          <p className="text-xs text-slate-500 mt-1 line-clamp-1">{tool.desc}</p>
                        </div>
                        <button className="px-4 py-1.5 bg-white border border-slate-200 text-slate-600 rounded-lg text-sm hover:bg-slate-50 hover:border-slate-300 transition-colors">
                          打开
                        </button>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* TAB: ADMIN */}
              {activeTab === 'admin' && (
                <div className="animate-in fade-in zoom-in-95 duration-300 h-full flex flex-col">
                  <div className="flex justify-between items-center mb-6">
                     <button className="bg-primary-600 text-white px-4 py-2 rounded-lg text-sm font-medium shadow-lg shadow-primary-500/20">新增用户</button>
                     <div className="relative">
                        <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
                        <input type="text" placeholder="搜索用户..." className="pl-9 pr-4 py-2 rounded-lg border border-slate-200 text-sm w-64 focus:outline-none focus:border-primary-500" />
                     </div>
                  </div>

                  {/* Table Header */}
                  <div className="grid grid-cols-6 gap-4 bg-slate-200/50 p-3 rounded-t-lg text-xs font-bold text-slate-600 text-center">
                    <div>用户ID</div>
                    <div>用户名</div>
                    <div>姓名</div>
                    <div>是否激活</div>
                    <div>用户角色</div>
                    <div>操作</div>
                  </div>
                  
                  {/* Mock Row */}
                  <div className="grid grid-cols-6 gap-4 bg-white p-3 border-b border-slate-100 text-sm text-slate-700 items-center text-center relative">
                    <div className="font-mono text-slate-400">00000000</div>
                    <div>User_Admin</div>
                    <div>管理员</div>
                    <div><span className="bg-green-100 text-green-700 px-2 py-0.5 rounded text-xs">是</span></div>
                    <div>Admin</div>
                    <div className="flex justify-center gap-2">
                       <button className="p-1 hover:bg-slate-100 rounded"><Settings className="w-4 h-4 text-slate-400" /></button>
                    </div>

                    {/* Modal Overlay (Simulated) */}
                    <div className="absolute top-8 left-1/4 right-1/4 bg-white rounded-xl shadow-2xl border border-slate-200 z-10 p-6 text-left animate-in zoom-in-95 fade-in">
                      <h3 className="font-bold text-lg mb-4">权限设置</h3>
                      <div className="border border-slate-200 rounded-lg p-4 max-h-60 overflow-y-auto mb-6 bg-slate-50">
                        <div className="space-y-2">
                           {[
                             {l: '鹿班测图工具', c: true}, 
                             {l: '天猫库存/预售时间调整工具', c: true},
                             {l: '天猫直播闪降工具', c: false},
                             {l: '与辉同行商品提报', c: false},
                             {l: 'pyd编译工具', c: true},
                             {l: 'Nuitka打包工具', c: true},
                           ].map((p, k) => (
                             <div key={k} className="flex items-center gap-3 p-2 hover:bg-white rounded cursor-pointer">
                               {p.c ? <CheckSquare className="w-5 h-5 text-primary-500" /> : <Square className="w-5 h-5 text-slate-300" />}
                               <span className={p.c ? 'text-slate-900' : 'text-slate-500'}>{p.l}</span>
                             </div>
                           ))}
                        </div>
                      </div>
                      <div className="flex gap-3">
                        <button className="flex-1 bg-primary-500 hover:bg-primary-600 text-white py-2 rounded-lg transition-colors">提交</button>
                        <button className="flex-1 bg-white border border-slate-200 text-slate-700 hover:bg-slate-50 py-2 rounded-lg">取消</button>
                      </div>
                    </div>
                  </div>
                  
                  {/* Blurred background rows */}
                  {[1,2,3].map(i => (
                     <div key={i} className="grid grid-cols-6 gap-4 bg-white p-3 border-b border-slate-100 text-sm text-slate-700 items-center text-center opacity-30 blur-[1px]">
                        <div>...</div><div>...</div><div>...</div><div>...</div><div>...</div><div>...</div>
                     </div>
                  ))}

                </div>
              )}

            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default InteractivePreview;