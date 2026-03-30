import React from 'react';
import { ArrowRight, Terminal, Package, ShieldCheck, Zap } from 'lucide-react';

const Hero: React.FC = () => {
  return (
    <section className="relative pt-32 pb-20 lg:pt-48 lg:pb-32 overflow-hidden">
      {/* Background Elements */}
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full h-full max-w-7xl -z-10 pointer-events-none">
        <div className="absolute top-20 left-10 w-72 h-72 bg-primary-200/40 rounded-full blur-3xl mix-blend-multiply animate-blob"></div>
        <div className="absolute top-20 right-10 w-72 h-72 bg-purple-200/40 rounded-full blur-3xl mix-blend-multiply animate-blob animation-delay-2000"></div>
        <div className="absolute -bottom-8 left-1/2 w-72 h-72 bg-pink-200/40 rounded-full blur-3xl mix-blend-multiply animate-blob animation-delay-4000"></div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary-50 border border-primary-100 text-primary-700 text-xs font-semibold uppercase tracking-wide mb-8 shadow-sm">
          <span className="w-2 h-2 rounded-full bg-primary-500 animate-pulse"></span>
          v2.0 全新发布
        </div>
        
        <h1 className="text-5xl md:text-7xl font-extrabold text-slate-900 tracking-tight mb-8 text-balance">
          电商自动化，<br className="hidden md:block" />
          <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary-600 to-purple-600">重新定义工作流</span>
        </h1>
        
        <p className="text-lg md:text-xl text-slate-600 max-w-2xl mx-auto mb-10 text-balance leading-relaxed">
          Synthos 是为电商团队打造的一站式桌面终端。
          集成自动化脚本、多平台工具箱与即时热更新插件系统。
          <br className="hidden sm:block" />
          提升效率，仅需一键。
        </p>

        <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-16">
          <button className="w-full sm:w-auto px-8 py-4 bg-slate-900 text-white rounded-2xl font-semibold text-lg shadow-xl shadow-slate-900/20 hover:bg-slate-800 hover:scale-105 transition-all duration-200 flex items-center justify-center gap-2">
            免费下载 (Windows)
            <ArrowRight className="w-5 h-5" />
          </button>
          <button className="w-full sm:w-auto px-8 py-4 bg-white text-slate-700 border border-slate-200 rounded-2xl font-semibold text-lg hover:bg-slate-50 hover:border-slate-300 transition-all duration-200 flex items-center justify-center gap-2">
            <Terminal className="w-5 h-5" />
            开发者文档
          </button>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 max-w-4xl mx-auto text-left">
          {[
            { icon: Package, label: "丰富的工具生态", desc: "开箱即用的电商工具" },
            { icon: Zap, label: "热更新技术", desc: "插件无感实时更新" },
            { icon: Terminal, label: "Python 驱动", desc: "强大的脚本扩展能力" },
            { icon: ShieldCheck, label: "企业级权限", desc: "精准的团队成员管理" },
          ].map((item, i) => (
            <div key={i} className="p-4 rounded-2xl bg-white border border-slate-100 shadow-sm hover:shadow-md transition-shadow">
              <item.icon className="w-6 h-6 text-primary-500 mb-3" />
              <h3 className="font-bold text-slate-900 text-sm">{item.label}</h3>
              <p className="text-xs text-slate-500 mt-1">{item.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default Hero;