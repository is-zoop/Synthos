import React from 'react';
import { User, Code2, Crown } from 'lucide-react';

const Features: React.FC = () => {
  const roles = [
    {
      role: '用户端',
      title: '简单，触手可及',
      description: '通过清晰的目录结构查看所有工具。支持一键应用热加载、查看详细教程、收藏常用工具及快速问题反馈。',
      icon: User,
      color: 'text-blue-500',
      bg: 'bg-blue-50',
      features: ['目录式工具浏览', '应用秒级热更新', '一键收藏常用功能']
    },
    {
      role: '开发者端',
      title: '无限扩展可能',
      description: '自主开发 Python 插件并发布到平台。拥有完整的版本迭代管理功能，让你的代码创造价值。',
      icon: Code2,
      color: 'text-purple-500',
      bg: 'bg-purple-50',
      features: ['Python 插件开发 SDK', '自动化版本发布流', '实时日志调试']
    },
    {
      role: '管理端',
      title: '掌控全局',
      description: '精细化的用户管理与权限控制系统。可以针对不同账号分配特定的工具访问权限，保障数据安全。',
      icon: Crown,
      color: 'text-orange-500',
      bg: 'bg-orange-50',
      features: ['用户账号生命周期管理', '颗粒度权限分配', '操作审计日志']
    }
  ];

  return (
    <section id="features" className="py-20 bg-slate-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center max-w-3xl mx-auto mb-16">
          <h2 className="text-3xl font-bold text-slate-900 sm:text-4xl">全角色覆盖的解决方案</h2>
          <p className="mt-4 text-lg text-slate-600">
            无论您是运营人员、开发者还是管理者，Synthos 都能提供量身定制的高效体验。
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {roles.map((role, index) => (
            <div 
              key={index} 
              className="bg-white rounded-3xl p-8 shadow-sm border border-slate-100 hover:shadow-xl hover:-translate-y-1 transition-all duration-300"
            >
              <div className={`w-14 h-14 ${role.bg} rounded-2xl flex items-center justify-center mb-6`}>
                <role.icon className={`w-7 h-7 ${role.color}`} />
              </div>
              <div className="text-sm font-bold tracking-wide text-slate-400 uppercase mb-2">{role.role}</div>
              <h3 className="text-2xl font-bold text-slate-900 mb-4">{role.title}</h3>
              <p className="text-slate-600 leading-relaxed mb-8 min-h-[80px]">
                {role.description}
              </p>
              <ul className="space-y-3">
                {role.features.map((feat, i) => (
                  <li key={i} className="flex items-center gap-3 text-slate-700">
                    <div className="w-1.5 h-1.5 rounded-full bg-slate-300"></div>
                    {feat}
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default Features;