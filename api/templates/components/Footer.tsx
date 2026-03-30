import React from 'react';

const Footer: React.FC = () => {
  return (
    <footer className="bg-white border-t border-slate-200 pt-16 pb-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-8 mb-12">
          <div className="col-span-2 md:col-span-1">
             <div className="flex items-center gap-2 mb-4">
                <div className="w-8 h-8 bg-slate-900 rounded-lg flex items-center justify-center text-white">
                  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" className="w-5 h-5">
                    <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/>
                  </svg>
                </div>
                <span className="text-xl font-bold text-slate-900">Synthos</span>
             </div>
             <p className="text-slate-500 text-sm leading-relaxed">
               专为电商团队设计的桌面自动化解决方案。<br/>让繁琐的工作自动化，让创造力回归。
             </p>
          </div>
          
          <div>
            <h4 className="font-bold text-slate-900 mb-4">产品</h4>
            <ul className="space-y-2 text-sm text-slate-500">
              <li><a href="#" className="hover:text-primary-600">功能特性</a></li>
              <li><a href="#" className="hover:text-primary-600">应用市场</a></li>
              <li><a href="#" className="hover:text-primary-600">更新日志</a></li>
              <li><a href="#" className="hover:text-primary-600">下载客户端</a></li>
            </ul>
          </div>

          <div>
            <h4 className="font-bold text-slate-900 mb-4">开发者</h4>
            <ul className="space-y-2 text-sm text-slate-500">
              <li><a href="#" className="hover:text-primary-600">开发者文档</a></li>
              <li><a href="#" className="hover:text-primary-600">API 参考</a></li>
              <li><a href="#" className="hover:text-primary-600">GitHub 仓库</a></li>
              <li><a href="#" className="hover:text-primary-600">提交插件</a></li>
            </ul>
          </div>

          <div>
            <h4 className="font-bold text-slate-900 mb-4">支持</h4>
            <ul className="space-y-2 text-sm text-slate-500">
              <li><a href="#" className="hover:text-primary-600">帮助中心</a></li>
              <li><a href="#" className="hover:text-primary-600">社区论坛</a></li>
              <li><a href="#" className="hover:text-primary-600">联系我们</a></li>
              <li><a href="#" className="hover:text-primary-600">隐私政策</a></li>
            </ul>
          </div>
        </div>
        
        <div className="pt-8 border-t border-slate-100 flex flex-col md:flex-row justify-between items-center gap-4">
          <p className="text-slate-400 text-sm">© 2025 Synthos Inc. All rights reserved.</p>
          <div className="flex gap-6">
            {/* Social placeholders */}
            <div className="w-5 h-5 bg-slate-200 rounded-full"></div>
            <div className="w-5 h-5 bg-slate-200 rounded-full"></div>
            <div className="w-5 h-5 bg-slate-200 rounded-full"></div>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;