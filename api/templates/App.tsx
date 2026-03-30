import React from 'react';
import Header from './components/Header';
import Hero from './components/Hero';
import InteractivePreview from './components/InteractivePreview';
import Features from './components/Features';
import Footer from './components/Footer';

const App: React.FC = () => {
  return (
    <div className="min-h-screen flex flex-col bg-slate-50">
      <Header />
      
      <main className="flex-grow">
        <Hero />
        <InteractivePreview />
        <Features />
        
        {/* Simple Call to Action Section */}
        <section className="py-24 bg-slate-900 text-white text-center px-4">
          <div className="max-w-4xl mx-auto">
            <h2 className="text-3xl md:text-5xl font-bold mb-6">准备好提升效率了吗？</h2>
            <p className="text-slate-300 text-lg mb-10 max-w-2xl mx-auto">
              加入数千个使用 Synthos 的电商团队，将重复性工作交给自动化脚本。
              立即开始免费试用。
            </p>
            <button className="bg-primary-600 hover:bg-primary-500 text-white px-10 py-4 rounded-full text-lg font-semibold transition-all shadow-lg shadow-primary-600/30 hover:shadow-primary-500/50 hover:-translate-y-1">
              立即下载 Windows 版
            </button>
            <p className="mt-6 text-slate-500 text-sm">支持 Windows 10 / 11 · 暂不支持 macOS</p>
          </div>
        </section>
      </main>

      <Footer />
    </div>
  );
};

export default App;